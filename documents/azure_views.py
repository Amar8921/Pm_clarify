from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime
from django.http import JsonResponse, HttpResponseNotFound
import json, logging, re, magic

import os

log = logging.getLogger(__name__)
# Set Azure Key and Endpoint using environment variables or directly here
FR_KEY = "ade29cccc39749fa9e491f91d0e06fad"
FR_ENDPOINT = "https://processpilotaivalidator.cognitiveservices.azure.com/"

import requests
from io import BytesIO

@csrf_exempt
@require_http_methods(["POST"])
def azure_id_card_analysis(request):
    image_content = None

    # Define allowed content types
    allowed_content_types = [
        'application/pdf',      # PDF
        'image/jpeg',           # JPEG
        'image/png',            # PNG
        'image/bmp',            # BMP
        'image/tiff',           # TIFF
        'image/heif',           # HEIF
    ]

    # Check if the request contains a file
    if 'image' in request.FILES:
        image_file = request.FILES['image']
        # Determine the file's content type
        file_content_type = magic.from_buffer(image_file.read(1024), mime=True)
        image_file.seek(0)  # Reset file pointer after reading

        # Check if the file's content type is allowed
        if file_content_type not in allowed_content_types:
            return JsonResponse({"status": "error", "message": "Unsupported file type."}, status=400)

        image_content = image_file.read()

    # If no file, check for JSON data
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
    
    # Create a DocumentAnalysisClient
    document_analysis_client = DocumentAnalysisClient(
        endpoint=FR_ENDPOINT, credential=AzureKeyCredential(FR_KEY)
    )

    # Analyze the ID document using Azure
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-idDocument", image_content
    )
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
    
    # Check if results dictionary is empty
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

    # Check if the request contains a file
    if 'image' in request.FILES:
        image_file = request.FILES['image']
        image_content = image_file.read()

    # If no file, check for JSON data
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
    # expiry_date_regex = r'(Expiry Date|تاريخ الانتهاء|Date of Expiry)\s*[:\-]?\s*(\d{2}/\d{2}/\d{4}|\d{4}/\d{2}/\d{2})'
    expiry_date_regex = r'(Expiry Date|تاريخ الإنتهاء|Date of Expiry)[\s\S]*?(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})'


    document_analysis_client = DocumentAnalysisClient(
        endpoint=FR_ENDPOINT, credential=AzureKeyCredential(FR_KEY)
    )

    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-read", image_content
    )
    result = poller.result()

    # Join all text content to form a single string for regex search
    full_text_content = ' '.join([line.content for page in result.pages for line in page.lines])

    # Search for expiry date using regex
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