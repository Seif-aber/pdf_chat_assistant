# PDF Chat Assistant

Interact with your PDF using Retrieval-Augmented Generation (RAG) + Gemini.  
Upload a PDF, it is chunked, embedded, and you can ask questions with contextual, streamed answers.

## Live Demos

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pdfchatassistant-seif-aber.streamlit.app/)
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/Seyfelislem/pdf_chat_assistant)

## Features
- PDF upload & inline preview
- Automatic text extraction, cleaning, chunking
- Embedding storage (pickle vector store)
- Similarity-based context retrieval
- Gemini response generation (streaming)
- Scrollable chat UI


## Conda Setup

```bash
git clone https://github.com/Seif-aber/pdf_chat_assistant
cd pdf-chat-assistant

# Create environment
conda create -n pdfchat python=3.12 -y
conda activate pdfchat

# Install dependencies
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in project root:

```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=models/embedding-001
STREAMLIT_PORT=8501
MAX_PDF_SIZE_MB=10
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
UPLOAD_FOLDER=data/uploads
EMBEDDINGS_FOLDER=data/embeddings
```

Then:

```bash
streamlit run src/app.py --server.port $STREAMLIT_PORT
```

## How It Works
1. Upload PDF → saved to a temp file.
2. Text extracted (PyPDF2 / pypdf fallback) and chunked with overlap.
3. Each chunk embedded via Gemini Embeddings API.
4. On question: create query embedding → cosine similarity → top chunks form context.
5. Gemini model generates constrained to context.
