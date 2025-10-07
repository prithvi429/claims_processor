import cv2
import numpy as np
from PIL import Image
import pytesseract
from ..utils.logging import logger

def ocr_image(img):
    """
    Perform OCR on a PIL Image (handles preprocessing for handwriting/images).
    """
    try:
        # Preprocess: Convert to OpenCV, grayscale, threshold
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # OCR
        text = pytesseract.image_to_string(Image.fromarray(thresh))
        logger.debug(f"OCR extracted: {text[:100]}...")  # Truncate for log
        return text.strip()
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return ""