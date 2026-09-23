import os
import uuid
from app.core.config import settings


def save_upload_file(file_bytes: bytes, filename: str) -> str:
    """Save raw uploaded file bytes to storage directory and return absolute file path."""
    settings.create_directories()
    unique_prefix = str(uuid.uuid4())[:8]
    safe_name = f"{unique_prefix}_{filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return os.path.abspath(file_path)
