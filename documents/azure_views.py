from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from documents.models import DocumentDefinition
from django.http import JsonResponse
import json

import os

# Set Azure Key and Endpoint using environment variables or directly here
FR_KEY = "ade29cccc39749fa9e491f91d0e06fad"
FR_ENDPOINT = "https://processpilotaivalidator.cognitiveservices.azure.com/"

import requests
from io import BytesIO

@csrf_exempt
@require_http_methods(["POST"])
def azure_id_card_analysis(request):
    image_content = None

    # Get JSON data from POST request
    body = json.loads(request.body.decode('utf-8'))

    if 'image' in request.FILES:
        image_file = request.FILES['image']
        image_content = image_file.read()

    elif 'url' in body:  # Check the URL from raw JSON data
        image_url = body['url']
        response = requests.get(image_url)
        response.raise_for_status()
        image_content = response.content

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

    return JsonResponse({
        "status": "success",
        "data": results
    }, status=200)
