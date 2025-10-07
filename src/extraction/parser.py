import pdfplumber
from pdf2image import convert_from_path  # pip install pdf2image
from .ocr import ocr_image
from ..config import DATA_DIR
from ..utils.logging import logger

def extract_text(file_path):
    """
    Extract text from PDF or Image. Handles structured (forms/tables) and unstructured.
    Returns dict: {"structured": {}, "unstructured": str, "confidence": float}
    """
    extracted = {"structured": {}, "unstructured": "", "confidence": 0.9}
    
    try:
        if file_path.suffix.lower() == '.pdf':
            with pdfplumber.open(file_path) as pdf:
                text_found = False
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        extracted["unstructured"] += page_text + "\n"
                        text_found = True
                    
                    # Structured: Extract tables/forms (basic; enhance with Textract in prod)
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            for row in table or []:
                                if len(row) >= 2:
                                    key = str(row[0]).strip().lower().replace(" ", "_")
                                    value = str(row[1]).strip()
                                    extracted["structured"][key] = value
                
                # If no text (scanned PDF), OCR as images
                if not text_found:
                    logger.info("No text in PDF; treating as scanned and OCR-ing")
                    images = convert_from_path(str(file_path))
                    for img in images:
                        extracted["unstructured"] += ocr_image(img) + "\n"
                
                # Mock confidence (use real OCR scores in prod)
                extracted["confidence"] = 0.85 if "handwritten" in extracted["unstructured"].lower() else 0.95
                
        else:  # Image file (PNG/JPG)
            from PIL import Image as PILImage
            img = PILImage.open(file_path)
            extracted["unstructured"] = ocr_image(img)
            extracted["confidence"] = 0.9
        
        logger.info(f"Extraction complete. Unstructured len: {len(extracted['unstructured'])}")
        return extracted
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        extracted["confidence"] = 0.0
        return extracted