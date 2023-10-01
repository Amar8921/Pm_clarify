from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import cv2

# TODO: Make better image optimization

@csrf_exempt
def image_optimizer(image_file):
    try:
        # Convert the image file to a numpy array and optimize
        npimg = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(npimg, cv2.IMREAD_GRAYSCALE)

        # Perform image optimization: resize, denoise, etc.
        optimized_image = perform_optimization(image)

        # Convert the optimized image back to binary format
        _, img_encoded = cv2.imencode('.png', optimized_image)
        img_data = img_encoded.tobytes()
        
        return img_data

    except Exception as e:
        # Handle the exception as needed; maybe log it, send an email, etc.
        print(f"Error in image optimization: {str(e)}")
        return None


def perform_optimization(image):
    # Example: Resize image
    height, width = image.shape
    new_width = 1000
    new_height = int((new_width/width) * height)
    resized_image = cv2.resize(image, (new_width, new_height))

    # Example: Apply Gaussian Blur
    blurred_image = cv2.GaussianBlur(resized_image, (5, 5), 0)

    # Example: Binarization using Otsu's method
    _, binarized_image = cv2.threshold(blurred_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Additional optimization steps like denoising, deskewing, etc. can be added here.

    return binarized_image
