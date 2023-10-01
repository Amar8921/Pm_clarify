from django.http import JsonResponse

def custom_404(request, exception):
    return JsonResponse({"status": "error", "message": "Resource not found."}, status=404)

def custom_500(request):
    return JsonResponse({"status": "error", "message": "Internal server error."}, status=500)
