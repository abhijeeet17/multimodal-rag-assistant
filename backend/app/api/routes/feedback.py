from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.document import Document, DocumentStatus, ChatMessage, Feedback
from app.schemas.document import FeedbackRequest, FeedbackResponse

router = APIRouter()


@router.post("", response_model=FeedbackResponse, summary="Submit RAG response feedback")
def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    feedback = Feedback(
        message_id=request.message_id,
        question=request.question,
        answer=request.answer,
        retrieved_chunks=request.retrieved_chunks,
        is_helpful=request.is_helpful,
        user_comment=request.user_comment
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return FeedbackResponse(id=feedback.id, status="success", message="Feedback recorded successfully")


@router.get("/stats", summary="Get dashboard metrics")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_docs = db.query(Document).count()
    completed_docs = db.query(Document).filter(Document.status == DocumentStatus.COMPLETED).count()
    failed_docs = db.query(Document).filter(Document.status == DocumentStatus.FAILED).count()

    total_questions = db.query(ChatMessage).filter(ChatMessage.sender == "user").count()
    helpful_responses = db.query(Feedback).filter(Feedback.is_helpful == True).count()
    unhelpful_responses = db.query(Feedback).filter(Feedback.is_helpful == False).count()

    return {
        "total_documents": total_docs,
        "completed_documents": completed_docs,
        "failed_documents": failed_docs,
        "total_questions": total_questions,
        "helpful_responses": helpful_responses,
        "unhelpful_responses": unhelpful_responses
    }
