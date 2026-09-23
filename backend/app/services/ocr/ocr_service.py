import io
from typing import Optional
from PIL import Image
import pytesseract
from app.core.config import settings

if settings.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


def perform_ocr_on_image_bytes(image_bytes: bytes) -> str:
    """Run Tesseract OCR on raw image bytes."""
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return ""


def perform_ocr_on_pdf_page(page_obj: any) -> str:
    """
    Render PDF page to pixmap image and run Tesseract OCR.
    Used for scanned pages with little or no selectable text.
    """
    try:
        # PyMuPDF page pixmap rendering (300 DPI equivalent via matrix)
        pix = page_obj.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")
        return perform_ocr_on_image_bytes(img_bytes)
    except Exception as e:
        return ""
