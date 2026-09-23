import uuid
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings
from app.models.document import ContentType


class DocumentChunker:
    def __init__(self, chunk_size: int = settings.CHUNK_SIZE, chunk_overlap: int = settings.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def create_chunks_from_pages(
        self,
        document_id: str,
        filename: str,
        pages_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Split page content into chunks while preserving metadata.
        Returns list of chunk objects:
        [
            {
                "chunk_id": "...",
                "document_id": "...",
                "filename": "...",
                "page_number": 4,
                "content": "...",
                "content_type": "text",
                "chunk_index": 0
            }
        ]
        """
        chunks = []
        global_chunk_idx = 0

        for page in pages_data:
            page_num = page.get("page_number", 1)
            text_content = page.get("text", "").strip()
            content_type = page.get("content_type", ContentType.TEXT.value)

            if not text_content:
                continue

            raw_splits = self.splitter.split_text(text_content)

            for split_text in raw_splits:
                if not split_text.strip():
                    continue

                chunk_id = str(uuid.uuid4())
                chunk_obj = {
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "filename": filename,
                    "page_number": page_num,
                    "content": split_text.strip(),
                    "content_type": content_type,
                    "chunk_index": global_chunk_idx,
                    "metadata": {
                        "document_id": document_id,
                        "filename": filename,
                        "page_number": page_num,
                        "chunk_id": chunk_id,
                        "content_type": content_type,
                        "chunk_index": global_chunk_idx
                    }
                }
                chunks.append(chunk_obj)
                global_chunk_idx += 1

        return chunks
