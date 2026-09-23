import os
import requests
import streamlit as st

# Configure Streamlit Page
st.set_page_config(
    page_title="Multimodal RAG Assistant",
    page_icon="📄",
    layout="wide"
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# Title & Subheader
st.title("📄 Multimodal Document Intelligence & RAG Assistant")
st.caption("Upload PDFs, Scanned PDFs, Images, or DOCX files and ask questions with grounded citations.")

# Check Backend API Health
@st.cache_data(ttl=5)
def check_backend_health():
    try:
        res = requests.get(f"{API_BASE_URL}/health", timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

health_status = check_backend_health()

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Sidebar - Document Management
with st.sidebar:
    st.header("⚙️ System Status & Files")
    if health_status:
        st.success(f"Backend API: {health_status.get('status')} | DB: {health_status.get('database')}")
    else:
        st.warning("Connecting to Backend API on port 8000...")

    st.subheader("📤 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a file (PDF, PNG, JPG, DOCX)",
        type=["pdf", "png", "jpg", "jpeg", "docx"]
    )

    if uploaded_file is not None:
        if st.button("Ingest Document", type="primary"):
            with st.spinner("Parsing, Chunking & Indexing in ChromaDB..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    res = requests.post(f"{API_BASE_URL}/documents/upload", files=files)
                    if res.status_code in [200, 201]:
                        doc_info = res.json()
                        st.success(f"Successfully indexed '{doc_info.get('filename')}' ({doc_info.get('total_pages')} pages)!")
                        st.cache_data.clear()
                    else:
                        st.error(f"Upload failed: {res.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    # List Uploaded Documents
    st.subheader("📚 Indexed Documents")
    try:
        docs_res = requests.get(f"{API_BASE_URL}/documents", timeout=3)
        if docs_res.status_code == 200:
            docs_data = docs_res.json().get("documents", [])
            if not docs_data:
                st.info("No documents uploaded yet.")
            for doc in docs_data:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"• {doc['filename']} ({doc['status']})")
                with col2:
                    if st.button("🗑️", key=f"del_{doc['id']}"):
                        requests.delete(f"{API_BASE_URL}/documents/{doc['id']}")
                        st.cache_data.clear()
                        st.rerun()
    except Exception:
        st.text("Could not load document list.")

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
    # Add User Message
    st.session_state.messages.append({"sender": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    # Call RAG Assistant API
    with st.chat_message("assistant"):
        with st.spinner("Retrieving relevant chunks & generating answer..."):
            try:
                payload = {
                    "question": user_question,
                    "session_id": st.session_state.session_id,
                    "top_k": 5
                }
                res = requests.post(f"{API_BASE_URL}/chat", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "")
                    citations = data.get("citations", [])
                    st.session_state.session_id = data.get("session_id")

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
                else:
                    st.error("Error from RAG Assistant server.")
            except Exception as e:
                st.error(f"Failed to reach RAG Assistant: {e}")
