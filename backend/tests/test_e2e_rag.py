import fitz  # PyMuPDF
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.document import DocumentStatus

client = TestClient(app)


def create_sample_pdf_bytes() -> bytes:
    """Create in-memory PDF document with sample text and page numbers."""
    doc = fitz.open()

    # Page 1: Annual Financial Data
    page1 = doc.new_page()
    page1.insert_text(
        (50, 100),
        "ANNUAL FINANCIAL REPORT 2025\n"
        "Executive Summary:\n"
        "The company's total revenue in 2025 was ₹50 crore.\n"
        "Net income increased by 15% compared to fiscal year 2024.\n"
        "Operating costs were managed within budget targets.",
        fontsize=12
    )

    # Page 2: Employee Breakdown
    page2 = doc.new_page()
    page2.insert_text(
        (50, 100),
        "HUMAN RESOURCES & COMPENSATION TABLE\n"
        "Employee | Role | Salary | Experience\n"
        "John Doe | Lead Engineer | $120,000 | 8 years\n"
        "Alice Smith | Staff Scientist | $140,000 | 10 years\n"
        "Bob Johnson | Analyst | $85,000 | 4 years\n"
        "Alice Smith has the highest salary among team members.",
        fontsize=12
    )

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_end_to_end_rag_pipeline():
    """
    End-to-End Integration Test:
    Upload PDF -> Extract Text -> Chunk -> Embed -> Index in ChromaDB -> Query -> Citation Verification
    """
    pdf_bytes = create_sample_pdf_bytes()

    # 1. Upload PDF document
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("Annual_Report_2025.pdf", pdf_bytes, "application/pdf")}
    )

    assert response.status_code == 201
    doc_data = response.json()
    assert doc_data["filename"] == "Annual_Report_2025.pdf"
    assert doc_data["status"] == DocumentStatus.COMPLETED.value
    assert doc_data["total_pages"] == 2
    document_id = doc_data["id"]

    # 2. Query RAG system about revenue
    query_payload = {
        "question": "What was the revenue in 2025?",
        "document_ids": [document_id],
        "top_k": 3
    }
    query_resp = client.post("/api/v1/query", json=query_payload)
    assert query_resp.status_code == 200

    query_data = query_resp.json()
    assert "answer" in query_data
    assert len(query_data["answer"]) > 0
    assert "50 crore" in query_data["answer"].lower() or "revenue" in query_data["answer"].lower()

    # 3. Verify exact citation metadata
    citations = query_data["citations"]
    assert len(citations) > 0
    assert citations[0]["document"] == "Annual_Report_2025.pdf"
    assert citations[0]["page"] in [1, 2]

    # 4. Clean up document
    del_resp = client.delete(f"/api/v1/documents/{document_id}")
    assert del_resp.status_code == 200
