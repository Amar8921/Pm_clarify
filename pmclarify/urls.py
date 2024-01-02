from django.urls import path
from documents import ocr_views, error_views, consul_views, azure_views
from rest_framework import permissions

handler404 = error_views.custom_404
handler500 = error_views.custom_500

urlpatterns = [
    path('health/', consul_views.health_check, name='health_check'),
    path('image-reader/', ocr_views.classify_image, name='classify'),
    path('image-extractor/', ocr_views.classify_image_doc, name='classify_image'),
    path('image-validate/', ocr_views.image_validator, name='validate_image'),

    path('azure-extractor/', azure_views.azure_id_card_analysis, name='azure_id'),
    path('expiry-checker/', azure_views.azure_expiry_checker, name='azure_layout'),

    path('define-document/', ocr_views.define_document),
    path('documents/', ocr_views.get_all_documents)
]
