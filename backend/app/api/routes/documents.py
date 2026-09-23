import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.document import Document, DocumentStatus
from app.schemas.document import DocumentResponse, DocumentListResponse
from app.services.ingestion.file_validator import validate_upload_file
from app.services.ingestion.storage import save_upload_file
from app.services.ingestion.doc_processor import DocumentProcessor
from app.services.retrieval.vector_store import ChromaVectorStore

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED, summary="Upload document for RAG ingestion")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    POST /api/v1/documents/upload
    Upload document file (PDF, PNG, JPG, JPEG, DOCX).
    Validates, stores file on disk, indexes in ChromaDB, and returns processing status.
    """
    file_bytes = await file.read()
    sanitized_filename, file_ext, file_size = validate_upload_file(file, file_bytes)

    saved_path = save_upload_file(file_bytes, sanitized_filename)

    # Save DB record
    doc_record = Document(
        filename=sanitized_filename,
        file_path=saved_path,
        file_type=file_ext,
        file_size=file_size,
        status=DocumentStatus.UPLOADED,
        total_pages=0
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    # Trigger processing pipeline synchronously for immediate availability
    try:
        processor = DocumentProcessor()
        doc_record = processor.process_document(db, doc_record.id)
    except Exception as e:
        # Document processor logs error on failure status
        pass

    return doc_record


@router.get("", response_model=DocumentListResponse, summary="List uploaded documents")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return DocumentListResponse(total=len(docs), documents=docs)


@router.get("/{document_id}", response_model=DocumentResponse, summary="Get document by ID")
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    return doc


@router.delete("/{document_id}", summary="Delete document and clean up vectors")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )

    # 1. Clean vectors from ChromaDB
    try:
        vector_store = ChromaVectorStore()
        vector_store.delete_document_chunks(document_id)
    except Exception:
        pass

    # 2. Delete raw file from disk
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except OSError:
            pass

    # 3. Delete record from SQL DB
    db.delete(doc)
    db.commit()

    return {"status": "success", "message": f"Document {document_id} and associated embeddings deleted"}
