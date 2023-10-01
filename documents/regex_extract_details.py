import re

def extract_detail(detail, extracted_text):
    """
    This function attempts to extract details using various regex patterns.
    """
    # Possible OCR variants of "Name" and "Nationality" due to OCR inaccuracies
    name_variants = ["name", "nane", "namc", "narn", "naine", "nmae", "naem"]
    nationality_variants = ["nationality", "rationality", "naticnality", "nationahty"]

    # Mapping original detail key with possible OCR misreads
    variant_map = {
        "Name": name_variants,
        "Nationality": nationality_variants,
        # Add more detail keys and their possible variants here...
    }
    
    patterns = []
    for variant in variant_map.get(detail, []):
        patterns.extend([
            rf"{variant}:[^\w]*([\w\s]+?)(?=\n|\Z)",  # For inline entry
            rf"{variant}:[^\w]*\n+([\w\s]+?)(?=\n|\Z)",  # For multiline entry
        ])

    for pattern in patterns:
        match = re.search(pattern, extracted_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None

