import base64
from typing import Optional
from openai import OpenAI
from app.core.config import settings
from app.services.ocr.ocr_service import perform_ocr_on_image_bytes


def analyze_image_with_vision(image_bytes: bytes, filename_hint: str = "document image") -> str:
    """
    Analyze image using OpenAI Vision model (or fallback OCR + summary).
    Generates structured textual description for indexing in RAG vector store.
    """
    ocr_text = perform_ocr_on_image_bytes(image_bytes)

    if settings.OPENAI_API_KEY and settings.LLM_PROVIDER == "openai":
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            base64_image = base64.b64encode(image_bytes).decode('utf-8')

            prompt = (
                "Analyze this image from a document (chart, graph, diagram, table, or photo). "
                "Provide a clear, detailed, factual textual description of what it shows, including numbers, trends, titles, "
                "labels, or data points. If there is text inside the image, include it accurately."
            )

            response = client.chat.completions.create(
                model=settings.VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )

            description = response.choices[0].message.content.strip()
            return f"Chart / Image Description ({filename_hint}):\n{description}"
        except Exception as e:
            pass

    # Fallback description using extracted OCR text
    if ocr_text:
        return f"Image Extracted Text / Content ({filename_hint}):\n{ocr_text}"
    return f"Image embedded in {filename_hint} (No readable text or vision provider available)."
