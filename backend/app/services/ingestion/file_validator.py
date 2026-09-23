import os
import re
from typing import Tuple
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and illegal path characters."""
    filename = os.path.basename(filename)
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    return filename or "uploaded_document"


def validate_upload_file(file: UploadFile, file_bytes: bytes) -> Tuple[str, str, int]:
    """
    Validate uploaded file type, filename, and size boundaries.
    Returns (sanitized_filename, file_extension, file_size).
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename."
        )

    sanitized_name = sanitize_filename(file.filename)
    ext = os.path.splitext(sanitized_name)[1].lower().lstrip(".")

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '.{ext}'. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    file_size = len(file_bytes)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    return sanitized_name, ext, file_size
