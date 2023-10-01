from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
from rest_framework.decorators import api_view
import json, re
from django.views.decorators.http import require_http_methods
from documents.models import DocumentDefinition
import pytesseract

@require_http_methods(["POST"])
@csrf_exempt
def define_document(request):
    try:
        data = json.loads(request.body)
        name = data['name']
        details = data['details']

        # Check if a document with the given name already exists
        if DocumentDefinition.objects.filter(name=name).exists():
            return JsonResponse({
                "status": "error",
                "message": "A document with this name already exists."
            }, status=400)

        document_def = DocumentDefinition(name=name, details=details)
        document_def.save()

        return JsonResponse({'status': 'success', 'message': 'Document details saved successfully.'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def get_all_documents(request):
    documents = DocumentDefinition.objects.all()
    response_data = [{"name": doc.name, "details": doc.details} for doc in documents]
    
    return JsonResponse({
        "status": "success",
        "documents": response_data
    })


@csrf_exempt
# Currently not needed per se
def classify_image(request):
    if request.method == 'POST':
        if 'image' not in request.FILES:
            return JsonResponse({"status": "error", "message": "Image missing."}, status=400)

        image_file = request.FILES['image']
        image_for_ocr = Image.open(image_file)

        extracted_text = pytesseract.image_to_string(image_for_ocr)

        return JsonResponse({
            "status": "success",
            "extracted_text": extracted_text.strip()  # This returns the extracted text from the image
        }, status=200)

    else:
        # Optional: You can handle other HTTP methods if needed.
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
    
    
@csrf_exempt
def classify_image_doc(request):  # doc_name e.g. 'pan-card'
    if request.method == 'POST':
        if 'image' not in request.FILES:
            return JsonResponse({"status": "error", "message": "Image missing."}, status=400)
        
        doc_name = request.POST.get('doc_name', None)
        if not doc_name:
            return JsonResponse({"status": "error", "message": "Document name (doc_name) missing in form data."}, status=400)


        image_file = request.FILES['image']
        image_for_ocr = Image.open(image_file)

        extracted_text = pytesseract.image_to_string(image_for_ocr)

        # Retrieve the details to extract for the given document type from your database
        try:
            document = DocumentDefinition.objects.get(name=doc_name)
            details_to_extract = document.details
        except DocumentDefinition.DoesNotExist:
            return JsonResponse({"status": "error", "message": f"No document definition found for {doc_name}."}, status=404)

        # Extract details dynamically based on provided patterns
        extracted_details = {}
        for detail in details_to_extract:
            # Create a regex pattern dynamically for each detail to extract
            pattern = r"{}[^\w]+([\w\s]+?)(?=\n|\Z)".format(detail)    # This will look for the detail name followed by any non-word characters and then capture the following word characters. 
            match = re.search(pattern, extracted_text)
            if match:
                extracted_details[detail] = match.group(1).strip()

        return JsonResponse({
            "status": "success",
            "extracted_details": extracted_details
        }, status=200)

    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
