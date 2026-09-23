import os
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.document import Document, Chunk, DocumentStatus, ContentType
from app.services.ingestion.pdf_parser import parse_pdf_document
from app.services.ingestion.docx_parser import parse_docx_document
from app.services.ocr.ocr_service import perform_ocr_on_image_bytes, perform_ocr_on_pdf_page
from app.services.vision.vision_service import analyze_image_with_vision
from app.services.chunking.chunker import DocumentChunker
from app.services.embeddings.embedding_service import EmbeddingService
from app.services.retrieval.vector_store import ChromaVectorStore
import fitz  # PyMuPDF


class DocumentProcessor:
    def __init__(self):
        self.chunker = DocumentChunker()
        self.embedding_service = EmbeddingService()
        self.vector_store = ChromaVectorStore()

    def process_document(self, db: Session, document_id: str) -> Document:
        """
        Process uploaded document end-to-end:
        Extract Text/OCR -> Chunk -> Embed -> Store in ChromaDB -> Update DB.
        """
        doc_record = db.query(Document).filter(Document.id == document_id).first()
        if not doc_record:
            raise ValueError(f"Document {document_id} not found in database.")

        doc_record.status = DocumentStatus.PROCESSING
        db.commit()

        try:
            file_path = doc_record.file_path
            file_ext = doc_record.file_type.lower().lstrip(".")
            filename = doc_record.filename

            pages_data: List[Dict[str, Any]] = []

            # 1. Extraction Stage
            if file_ext == "pdf":
                pdf_pages = parse_pdf_document(file_path)
                doc_obj = fitz.open(file_path)

                for p_idx, p_data in enumerate(pdf_pages):
                    # Check if OCR fallback is needed for scanned pages
                    if not p_data["has_usable_text"]:
                        ocr_text = perform_ocr_on_pdf_page(doc_obj[p_idx])
                        if ocr_text:
                            p_data["text"] = ocr_text
                            p_data["content_type"] = ContentType.OCR.value
                    else:
                        p_data["content_type"] = ContentType.TEXT.value

                    # Process embedded images if present
                    if p_data["image_count"] > 0 and len(p_data["images"]) > 0:
                        for img in p_data["images"][:2]:  # Limit to first 2 images per page
                            vision_desc = analyze_image_with_vision(img["bytes"], filename)
                            if vision_desc:
                                p_data["text"] += f"\n\n{vision_desc}"

                    pages_data.append(p_data)
                doc_obj.close()

            elif file_ext == "docx":
                pages_data = parse_docx_document(file_path)

            elif file_ext in ["png", "jpg", "jpeg"]:
                with open(file_path, "rb") as f:
                    img_bytes = f.read()

                ocr_text = perform_ocr_on_image_bytes(img_bytes)
                vision_desc = analyze_image_with_vision(img_bytes, filename)

                combined_img_text = f"{ocr_text}\n\n{vision_desc}".strip()
                pages_data = [{
                    "page_number": 1,
                    "text": combined_img_text or f"Image file: {filename}",
                    "has_usable_text": True,
                    "content_type": ContentType.IMAGE.value,
                    "image_count": 1,
                    "images": []
                }]

            # 2. Chunking Stage
            chunks = self.chunker.create_chunks_from_pages(
                document_id=doc_record.id,
                filename=filename,
                pages_data=pages_data
            )

            # 3. Embeddings & Vector Indexing Stage
            if chunks:
                chunk_texts = [c["content"] for c in chunks]
                embeddings = self.embedding_service.embed_documents(chunk_texts)
                self.vector_store.add_chunks(chunks, embeddings)

                # 4. Save Chunk DB records
                for chunk_data in chunks:
                    db_chunk = Chunk(
                        id=chunk_data["chunk_id"],
                        document_id=doc_record.id,
                        content=chunk_data["content"],
                        page_number=chunk_data["page_number"],
                        content_type=ContentType(chunk_data["content_type"]),
                        chunk_index=chunk_data["chunk_index"],
                        embedding_id=chunk_data["chunk_id"],
                        chunk_metadata=chunk_data["metadata"]
                    )
                    db.add(db_chunk)

            # Update Document Record
            doc_record.status = DocumentStatus.COMPLETED
            doc_record.total_pages = len(pages_data)
            db.commit()
            db.refresh(doc_record)
            return doc_record

        except Exception as e:
            db.rollback()
            doc_record.status = DocumentStatus.FAILED
            doc_record.error_message = str(e)
            db.commit()
            raise e
