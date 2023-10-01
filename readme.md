# PM-Clarify Microservice

`pm-clarify` is a versatile microservice initially designed for OCR (Optical Character Recognition) on photos and documents. While its current capabilities focus on image and document classification, future plans include the integration of NLP and various model training functionalities.

## Key Features

- **Document Definition**: Define and manage various document types.
- **OCR Extraction**: Extract text from images.
- **Document-based OCR**: Extract specific details based on predefined document types.

## Endpoints Overview

- **`/define_document` (POST)**: Define a new document type.
- **`/get_all_documents` (GET)**: Retrieve all defined document types.
- **`/classify_image` (POST)**: Perform OCR on an uploaded image to extract text.
- **`/classify_image_doc` (POST)**: Extract details from an image based on a specified document type.

## Setup & Installation

(Add brief setup and installation instructions if necessary.)

## Contribution & Feedback

We're continually working to enhance `pm-clarify` and your feedback is invaluable. (You can add contribution guidelines or methods to provide feedback here.)

## License

(Include license details if necessary.)
