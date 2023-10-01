import spacy
import re

# Load the spaCy model outside the function to avoid loading it multiple times
NLP_MODEL = spacy.load("en_core_web_sm")

def clean_and_extract_details(ocr_data, details_to_extract):
    # Basic cleaning to remove obvious OCR noise. This can be adjusted.
    clean_data = re.sub(r'[_]', ' ', ocr_data)  # Replace underscores with space
    clean_data = re.sub(r'\n{2,}', '\n', clean_data)  # Replace multiple newlines with a single newline
    print(clean_data)
    doc = NLP_MODEL(clean_data)
    extracted_details = {detail: None for detail in details_to_extract}

    for ent in doc.ents:
        for detail in details_to_extract:
            if detail.lower() in ent.text.lower():
                extracted_details[detail] = ent.text

    return extracted_details
