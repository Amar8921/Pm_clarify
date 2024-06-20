import pytesseract
from PIL import Image
import re
from io import BytesIO
import logging
import fitz  # PyMuPDF
from .image_optimizer import *

log = logging.getLogger(__name__)

def identify_document_type(text):
    patterns = [
        r'\bemployment\b',
        r'\bINCOME TAX DEPARTMENT\b',
        r'(?i)\bdriv(?:ing licen[cs]e|er[\'’]?s? license)\b',
        r'\bNew Work Entry Permit\b',
        r'\bCommercial License\b',
        r'\bTourism\b|\bMAXIMUM STAY\b',
        r'\bClinic\b|\bInsurance\b',
        r'\bChange Status\b',
        r'\bEMPLOYMENT CONTRACT\b|\bJOB OFFER\b',
        r'(?i)\b(new residency|residen(?:ce|cy|ts)|registration id card|identity)\b',
        r'\b[eE]visa\b',
        r'\bWork Permit\b',
        r'\bEstablishment Information\b',
        r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
        r'\d{4}\s\d{4}\s\d{4}\b',
        r'\b[A-Z]{1}\s?[0-9]{7}\b',
        r'\bL.L.C\b|\bbranch\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            document_type = None
            if pattern == r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b' or pattern==r'\bINCOME TAX DEPARTMENT\b':
                document_type = "PAN"
            elif pattern == r'\d{4}\s\d{4}\s\d{4}\b':
                document_type = "Aadhaar"
            elif pattern == r'\b[A-Z]{1}\s?[0-9]{7}\b':
                document_type = "passport"
            else:
                document_type = match.group()
            log.info(f"Document type identified: {document_type}")
            return f"{document_type} card"
    log.info("No match found for document type")
    return "No match found"

def extract_text_from_image(image_stream):
    try:
        image = Image.open(BytesIO(image_stream))
        extracted_text = pytesseract.image_to_string(image)
        log.info(f"Extracted text: {extracted_text}")
        return extracted_text
    except Exception as e:
        log.error(f"Error while extracting text from image: {e}")
        return None

def extract_text_from_pdf(pdf_stream):
    try:
        pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text("text")
        log.info(f"Extracted text from PDF: {text}")
        return text
    except Exception as e:
        log.error(f"Error while extracting text from PDF: {e}")
        return ""
