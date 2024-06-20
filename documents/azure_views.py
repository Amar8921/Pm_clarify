# Import necessary modules
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseNotFound
import json, logging, re, magic
from .document_views import extract_text_from_image, extract_text_from_pdf, identify_document_type
import requests
from io import BytesIO

log = logging.getLogger(__name__)

# Azure Form Recognizer configuration
FR_KEY = "ade29cccc39749fa9e491f91d0e06fad"
FR_ENDPOINT = "https://processpilotaivalidator.cognitiveservices.azure.com/"

@csrf_exempt
@require_http_methods(["POST"])
def azure_id_card_analysis(request):
    image_content = None
    file_content_type = None

    allowed_content_types = [
        'application/pdf',      # PDF
        'image/jpeg',           # JPEG
        'image/png',            # PNG
        'image/bmp',            # BMP
        'image/tiff',           # TIFF
        'image/heif',           # HEIF
    ]

    if 'image' in request.FILES:
        image_file = request.FILES['image']
        file_content_type = magic.from_buffer(image_file.read(1024), mime=True)
        image_file.seek(0)

        if file_content_type not in allowed_content_types:
            return JsonResponse({"status": "error", "message": "Unsupported file type."}, status=400)

        image_content = image_file.read()

    elif request.content_type == 'application/json':
        try:
            body = json.loads(request.body.decode('utf-8'))
            if 'url' in body:
                image_url = body['url']
                response = requests.get(image_url)
                response.raise_for_status()
                image_content = response.content
                file_content_type = response.headers.get('Content-Type')
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON."}, status=400)
        except UnicodeDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid UTF-8 data."}, status=400)

    if not image_content:
        return JsonResponse({"status": "error", "message": "Image or URL missing."}, status=400)
    
    document_analysis_client = DocumentAnalysisClient(
        endpoint=FR_ENDPOINT, credential=AzureKeyCredential(FR_KEY)
    )

    try:
        # Attempt to analyze with prebuilt-idDocument model first
        poller = document_analysis_client.begin_analyze_document("prebuilt-idDocument", image_content)
        id_documents = poller.result()

        results = {}
        for idx, id_document in enumerate(id_documents.documents):
            for field_name in ["FirstName", "LastName", "DocumentNumber", "DateOfBirth", "DateOfExpiration", "Sex", "Address", "CountryRegion", "Region"]:
                field = id_document.fields.get(field_name)
                if field:
                    results[field_name] = {
                        "value": field.value,
                        "confidence": field.confidence
                    }
        
        if file_content_type in ['image/jpeg', 'image/png', 'image/bmp', 'image/tiff', 'image/heif']:

            full_text_content=extract_text_from_image(image_content)
            document_type = identify_document_type(full_text_content)
            results["DocumentType"] = {"value": document_type}
            log.info(f"Extracted text from ID document: {full_text_content}")
            
    
    except Exception as e:
        log.error(f"Error in analyzing with prebuilt-idDocument: {e}")
        results = {}

    # If no fields were extracted or it was a PDF, fall back to using prebuilt-read model
    if not results or file_content_type == 'application/pdf':
        try:
            if file_content_type == 'application/pdf':
                full_text_content = extract_text_from_pdf(image_content)
            else:
                poller = document_analysis_client.begin_analyze_document("prebuilt-read", image_content)
                id_documents = poller.result()
                full_text_content = ' '.join([line.content for page in id_documents.pages for line in page.lines])

            document_type = identify_document_type(full_text_content)
            results["DocumentType"] = {"value": document_type}
        
        except Exception as e:
            log.error(f"Error in analyzing with prebuilt-read: {e}")

    if not results:
        return JsonResponse({"status": "error", "message": "ID document not clear, upload again"}, status=400)

    return JsonResponse({
        "status": "success",
        "data": results
    }, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def azure_expiry_checker(request):
    image_content = None

    if 'image' in request.FILES:
        image_file = request.FILES['image']
        image_content = image_file.read()

    elif request.content_type == 'application/json':
        try:
            body = json.loads(request.body.decode('utf-8'))
            if 'url' in body:
                image_url = body['url']
                response = requests.get(image_url)
                response.raise_for_status()
                image_content = response.content
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON."}, status=400)
        except UnicodeDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid UTF-8 data."}, status=400)

    if not image_content:
        return JsonResponse({"status": "error", "message": "Image or URL missing."}, status=400)
    
    # Regular expression for matching various expiry date formats
    expiry_date_regex = r'(Expiry Date|تاريخ الإنتهاء|Date of Expiry)[\s\S]*?(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})'

    document_analysis_client = DocumentAnalysisClient(
        endpoint=FR_ENDPOINT, credential=AzureKeyCredential(FR_KEY)
    )

    try:
        if request.content_type == 'application/pdf':
            full_text_content = extract_text_from_pdf(image_content)
        else:
            poller = document_analysis_client.begin_analyze_document("prebuilt-read", image_content)
            result = poller.result()
            full_text_content = ' '.join([line.content for page in result.pages for line in page.lines])

        matches = re.search(expiry_date_regex, full_text_content)
        
        if not matches:
            return HttpResponseNotFound('Expiry date not found')

        raw_expiry_date = matches.group(2)

        def convert_date_format(date_str):
            try:
                # Try parsing as DD/MM/YYYY
                return datetime.strptime(date_str, "%d/%m/%Y").strftime("%d/%m/%Y")
            except ValueError:
                # Try parsing as YYYY/MM/DD
                return datetime.strptime(date_str, "%Y/%m/%d").strftime("%d/%m/%Y")

        expiry_date = convert_date_format(raw_expiry_date.replace("-", "/"))

        return JsonResponse({
            "status": "success",
            "expiry_date": expiry_date
        }, status=200)
    
    except Exception as e:
        log.error(f"Error in analyzing document for expiry date: {e}")
        return JsonResponse({"status": "error", "message": "Error analyzing document for expiry date."}, status=500)
