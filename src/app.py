import streamlit as st
import os
import tempfile
import hashlib
from components.file_uploader import FileUploader
from components.pdf_viewer import PdfViewer
from components.chat_interface import ChatInterface
from services.pdf_processor import PDFProcessor
from services.embedding_service import EmbeddingService
from services.gemini_client import GeminiClient
from services.rag_service import RAGService

def initialize_session_state():
    defaults = {
        "chat_history": [],
        "pdf_processed": False,
        "pdf_id": None,
        "pdf_chunks": [],
        "uploaded_file_path": None,
        "current_file_name": None,
        "current_file_hash": None,
        "processing": False,
        "streaming": False,
        "chat_input": "",
        "clear_chat_input": False,   # <--- new flag
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_app_state(embedding_service: EmbeddingService) -> None:
    old_path = st.session_state.get("uploaded_file_path")
    if old_path and os.path.exists(old_path):
        try: os.unlink(old_path)
        except Exception: pass
    try:
        embedding_service.vector_store.clear_embeddings()
    except Exception:
        pass
    st.session_state.chat_history = []
    st.session_state.pdf_processed = False
    st.session_state.pdf_id = None
    st.session_state.pdf_chunks = []
    st.session_state.uploaded_file_path = None
    st.session_state.current_file_name = None
    st.session_state.current_file_hash = None
    st.session_state.processing = False
    st.session_state.streaming = False

def _file_hash(uploaded_file) -> str:
    return hashlib.md5(uploaded_file.getvalue()).hexdigest()

def auto_process_pdf(uploaded_file, tmp_file_path, embedding_service: EmbeddingService, force: bool = False):
    if st.session_state.processing:
        return
    if st.session_state.pdf_processed and not force:
        return
    st.session_state.processing = True
    status = st.empty()
    try:
        status.markdown("⏳ Processing PDF... 10%")
        pdf_processor = PDFProcessor()
        chunks = pdf_processor.process_pdf(tmp_file_path)
        if not chunks:
            status.error("Failed to extract text.")
            return
        pdf_id = uploaded_file.name.replace(".pdf","").replace(" ","_").replace(".","_")
        st.session_state.pdf_id = pdf_id
        st.session_state.pdf_chunks = chunks
        status.markdown("⏳ Processing PDF... 50%")
        embedding_service.store_pdf_embeddings(pdf_id, chunks)
        status.markdown("⏳ Processing PDF... 90%")
        st.session_state.pdf_processed = True
        status.success(f"✅ Processing complete (100%). {len(chunks)} chunks ready.")
    except Exception as e:
        status.error(f"❌ Error: {e}")
    finally:
        st.session_state.processing = False

def main():
    st.set_page_config(page_title="PDF Chat Assistant", page_icon="📄", layout="wide")
    st.title("📄 PDF Chat Assistant")
    initialize_session_state()

    embedding_service = EmbeddingService()
    gemini_client = GeminiClient()
    rag_service = RAGService(embedding_service, gemini_client)

    col1, col2 = st.columns([1,1])

    with col1:
        st.header("📁 Upload & Preview PDF")
        uploaded_file = FileUploader().upload_file()
        if uploaded_file:
            new_hash = _file_hash(uploaded_file)
            if st.session_state.current_file_hash and st.session_state.current_file_hash != new_hash:
                reset_app_state(embedding_service)
            if st.session_state.current_file_hash != new_hash:
                st.session_state.current_file_name = uploaded_file.name
                st.session_state.current_file_hash = new_hash
                st.session_state.pdf_processed = False
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            st.session_state.uploaded_file_path = tmp_path
            PdfViewer().display_pdf(tmp_path)
            auto_process_pdf(uploaded_file, tmp_path, embedding_service)
            if st.session_state.pdf_processed and not st.session_state.processing:
                if st.button("🔄 Reprocess PDF"):
                    st.session_state.pdf_processed = False
                    auto_process_pdf(uploaded_file, tmp_path, embedding_service, force=True)
        else:
            st.info("Upload a PDF to begin.")

    with col2:
        st.header("💬 Chat with your PDF")
        if st.session_state.processing:
            st.info("⏳ Processing... Please wait.")
            return

        chat_ui = ChatInterface()

        if st.session_state.pdf_processed and st.session_state.pdf_id:
            if st.session_state.clear_chat_input:
                st.session_state.chat_input = ""
                st.session_state.clear_chat_input = False

            chat_ui.render(st.session_state.chat_history)
            disabled = st.session_state.streaming
            user_input = st.text_input(
                "Ask a question:",
                key="chat_input",
                placeholder="Type your question...",
                disabled=disabled,
                label_visibility="collapsed"
            )
            send = st.button("Send", disabled=disabled or not user_input.strip(), use_container_width=True)

            if send and user_input.strip():
                query = user_input.strip()
                st.session_state.chat_history.append({"role": "user", "content": query})
                st.session_state.streaming = True

                st.session_state.clear_chat_input = True
                stream_iter = rag_service.stream_response(
                    query,
                    st.session_state.pdf_id,
                    st.session_state.chat_history
                )
                assistant_text = chat_ui.stream_assistant(st.session_state.chat_history, stream_iter)
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_text})
                st.session_state.streaming = False
                st.rerun()

            col_a, col_b = st.columns([1,1])
            with col_a:
                if st.button("Clear Chat", disabled=st.session_state.streaming):
                    st.session_state.chat_history = []
                    st.session_state.clear_chat_input = True
                    st.rerun()
            with col_b:
                pass
        else:
            st.info("Upload and wait for processing to chat.")

if __name__ == "__main__":
    main()