from typing import List, Dict, Any
import fitz  # PyMuPDF


def parse_pdf_document(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse PDF file using PyMuPDF (fitz).
    Returns list of page details:
    [
        {
            "page_number": 1,
            "text": "Extracted text string",
            "has_usable_text": True/False,
            "image_count": 2,
            "images": [bytes, ...]
        }, ...
    ]
    """
    doc = fitz.open(file_path)
    pages_data = []

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text("text").strip()

        # Check if page text is sufficient (non-scanned)
        has_usable_text = len(text) > 30

        # Extract embedded image objects
        image_list = page.get_images(full=True)
        images = []
        for img_info in image_list:
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                images.append({
                    "bytes": image_bytes,
                    "ext": base_image["ext"]
                })
            except Exception:
                continue

        pages_data.append({
            "page_number": page_idx + 1,
            "text": text,
            "has_usable_text": has_usable_text,
            "image_count": len(images),
            "images": images
        })

    doc.close()
    return pages_data
