import os
import sys
import tempfile
import streamlit as st

# Add backend directory to sys.path so services can be imported directly
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Configure Streamlit Page
st.set_page_config(
    page_title="Multimodal RAG Assistant",
    page_icon="📄",
    layout="wide"
)

# Title & Subheader
st.title("📄 Multimodal Document Intelligence & RAG Assistant")
st.caption("Upload PDFs, Scanned PDFs, Images, or DOCX files and ask questions with grounded citations.")

# Initialize RAG Services
@st.cache_resource
def load_rag_services():
    from app.services.chunking.chunker import DocumentChunker
    from app.services.embeddings.embedding_service import EmbeddingService
    from app.services.retrieval.vector_store import ChromaVectorStore
    from app.services.generation.rag_generator import RAGGenerator

    chunker = DocumentChunker()
    embedding_service = EmbeddingService()
    vector_store = ChromaVectorStore()
    generator = RAGGenerator()
    return chunker, embedding_service, vector_store, generator

try:
    chunker, embedding_service, vector_store, generator = load_rag_services()
    rag_ready = True
except Exception as e:
    rag_ready = False
    st.error(f"Initialization error: {e}")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []

# Sidebar - Document Management
with st.sidebar:
    st.header("⚙️ Document Manager")
    st.success("RAG Engine Active (Self-Contained)")

    st.subheader("📤 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a file (PDF, PNG, JPG, DOCX)",
        type=["pdf", "png", "jpg", "jpeg", "docx"]
    )

    if uploaded_file is not None:
        if st.button("Ingest Document", type="primary"):
            with st.spinner(f"Parsing '{uploaded_file.name}' & Indexing in ChromaDB..."):
                try:
                    # Save temporary file
                    os.makedirs("./data/uploads", exist_ok=True)
                    temp_path = os.path.join("./data/uploads", uploaded_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getvalue())

                    file_ext = os.path.splitext(uploaded_file.name)[1].lower().lstrip(".")
                    pages_data = []

                    if file_ext == "pdf":
                        from app.services.ingestion.pdf_parser import parse_pdf_document
                        pages_data = parse_pdf_document(temp_path)
                    elif file_ext == "docx":
                        from app.services.ingestion.docx_parser import parse_docx_document
                        pages_data = parse_docx_document(temp_path)
                    else:
                        from app.services.ocr.ocr_service import perform_ocr_on_image_bytes
                        ocr_text = perform_ocr_on_image_bytes(uploaded_file.getvalue())
                        pages_data = [{
                            "page_number": 1,
                            "text": ocr_text or f"Image file: {uploaded_file.name}",
                            "has_usable_text": True,
                            "content_type": "image",
                            "image_count": 1,
                            "images": []
                        }]

                    # Chunk & Embed
                    chunks = chunker.create_chunks_from_pages(
                        document_id=uploaded_file.name,
                        filename=uploaded_file.name,
                        pages_data=pages_data
                    )

                    if chunks:
                        texts = [c["content"] for c in chunks]
                        embeddings = embedding_service.embed_documents(texts)
                        vector_store.add_chunks(chunks, embeddings)

                        if uploaded_file.name not in st.session_state.indexed_files:
                            st.session_state.indexed_files.append(uploaded_file.name)

                        st.success(f"Indexed '{uploaded_file.name}' ({len(pages_data)} pages, {len(chunks)} chunks)!")
                    else:
                        st.warning("No text extracted from document.")
                except Exception as e:
                    st.error(f"Processing error: {e}")

    # List Indexed Files
    st.subheader("📚 Indexed Documents")
    if not st.session_state.indexed_files:
        st.info("No documents uploaded yet.")
    else:
        for fname in st.session_state.indexed_files:
            st.text(f"• {fname}")

# Main Chat Interface
for msg in st.session_state.messages:
    with st.chat_message(msg["sender"]):
        st.markdown(msg["content"])
        if msg.get("citations"):
            st.markdown("---")
            st.caption("📚 **Sources & Citations:**")
            for cit in msg["citations"]:
                st.info(f"📄 **{cit['document']}** — Page {cit['page']}")

# User Question Input
if user_question := st.chat_input("Ask a question about your uploaded documents..."):
    st.session_state.messages.append({"sender": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        with st.spinner("Searching vector index & generating answer..."):
            try:
                # Retrieve relevant chunks from ChromaDB
                query_vector = embedding_service.embed_query(user_question)
                relevant_chunks = vector_store.similarity_search(
                    query_embedding=query_vector,
                    top_k=5
                )

                # Generate Answer
                result = generator.generate_answer(
                    question=user_question,
                    retrieved_chunks=relevant_chunks
                )

                answer = result.get("answer", "")
                citations = result.get("citations", [])

                st.markdown(answer)
                if citations:
                    st.markdown("---")
                    st.caption("📚 **Sources & Citations:**")
                    for cit in citations:
                        st.info(f"📄 **{cit['document']}** — Page {cit['page']}")

                st.session_state.messages.append({
                    "sender": "assistant",
                    "content": answer,
                    "citations": citations
                })
            except Exception as e:
                st.error(f"Search error: {e}")
