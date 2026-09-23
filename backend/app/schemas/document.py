from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from app.models.document import DocumentStatus, ContentType


class DocumentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int


class DocumentCreate(DocumentBase):
    file_path: str


class DocumentResponse(DocumentBase):
    id: str
    status: DocumentStatus
    total_pages: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    total: int
    documents: List[DocumentResponse]


class ChunkMetadata(BaseModel):
    document_id: str
    filename: str
    page_number: int
    chunk_id: str
    content_type: ContentType = ContentType.TEXT


class ChunkResponse(BaseModel):
    id: str
    document_id: str
    content: str
    page_number: int
    content_type: ContentType
    chunk_index: int
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class Citation(BaseModel):
    document: str
    page: int
    chunk_id: Optional[str] = None
    snippet: Optional[str] = None


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User's query string")
    document_ids: Optional[List[str]] = Field(default=None, description="Optional filter by document IDs")
    session_id: Optional[str] = Field(default=None, description="Optional chat session ID")
    top_k: Optional[int] = Field(default=5, ge=1, le=20)


class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: List[Citation]
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None
    session_id: Optional[str] = None
    message_id: Optional[str] = None


class FeedbackRequest(BaseModel):
    message_id: Optional[str] = None
    question: str
    answer: str
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None
    is_helpful: bool
    user_comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: str
    status: str = "success"
    message: str = "Feedback recorded"


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str
