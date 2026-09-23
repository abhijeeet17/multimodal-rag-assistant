from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.document import ChatSession, ChatMessage
from app.schemas.document import QueryRequest, QueryResponse, Citation
from app.services.retrieval.retriever import RAGRetriever
from app.services.generation.rag_generator import RAGGenerator

router = APIRouter()


@router.post("/query", response_model=QueryResponse, summary="Query RAG Assistant")
def query_rag(request: QueryRequest, db: Session = Depends(get_db)):
    """
    POST /api/v1/query & POST /api/v1/chat
    Performs RAG pipeline:
    User Question -> Query Embedding -> ChromaDB Vector Search -> Relevant Chunks -> Grounded LLM -> Answer + Citations
    """
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question string cannot be empty."
        )

    # 1. Retrieval Phase: Query Embedding -> ChromaDB Search -> Top-K Chunks
    retriever = RAGRetriever()
    relevant_chunks = retriever.retrieve_relevant_chunks(
        query=request.question,
        top_k=request.top_k or 5,
        document_ids=request.document_ids
    )

    # 2. Generation Phase: Context + Question -> Grounded LLM Answering
    generator = RAGGenerator()
    generated_result = generator.generate_answer(
        question=request.question,
        retrieved_chunks=relevant_chunks
    )

    # 3. Store Chat Session & Messages in Database
    session_id = request.session_id
    if not session_id:
        session = ChatSession(title=request.question[:40])
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id

    # User message
    user_msg = ChatMessage(
        session_id=session_id,
        sender="user",
        content=request.question
    )
    db.add(user_msg)

    # Assistant message with citations
    citations_data = generated_result.get("citations", [])
    assistant_msg = ChatMessage(
        session_id=session_id,
        sender="assistant",
        content=generated_result.get("answer", ""),
        citations=citations_data
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    parsed_citations = [
        Citation(
            document=c["document"],
            page=c["page"],
            chunk_id=c.get("chunk_id"),
            snippet=c.get("snippet")
        )
        for c in citations_data
    ]

    return QueryResponse(
        question=request.question,
        answer=generated_result.get("answer", ""),
        citations=parsed_citations,
        retrieved_chunks=relevant_chunks,
        session_id=session_id,
        message_id=assistant_msg.id
    )


@router.post("/chat", response_model=QueryResponse, summary="Chat with Document Assistant")
def chat_rag(request: QueryRequest, db: Session = Depends(get_db)):
    return query_rag(request=request, db=db)
