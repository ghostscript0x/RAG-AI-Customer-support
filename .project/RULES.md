# Engineering Rules — RAG AI Customer Support Chatbot

## Universal
- Python 3.11+
- Type hints on every function signature
- Docstrings on every public function/class
- Logging via `import logging`, never `print`
- No hardcoded secrets or model names — everything configurable via `.env`
  - `GROQ_API_KEY`, `GROQ_MODEL`, `EMBEDDING_MODEL`, `TOP_K`, `CONFIDENCE_THRESHOLD`, `CHROMA_PERSIST_DIR`
- No feature from Future Enhancements (multi-tenant, auth, Slack, etc.) — scope creep

## Architecture
- UI (Streamlit pages) never talks to ChromaDB or Groq directly — always through `chatbot/` and `rag/` service layers
- Modular separation: `ingestion/` → `rag/` → `chatbot/` → UI

## Error Handling
- Every external call (Groq API, file parsing, ChromaDB) wrapped in `try/except`
- Graceful degradation — never a raw stack trace to the UI
- User-facing errors are friendly, not technical

## Testing
- Every module in `rag/`, `chatbot/`, `ingestion/`, `database/` gets a corresponding test file in `tests/`
- Write the test in the same phase as the code, not after

## Project Structure (PRD Section 7 — do not reorganize)
```
rag-ai/
├── app.py                         # Streamlit entry point
├── pages/
│   ├── 1_New_Chat.py
│   ├── 2_Upload.py
│   ├── 3_Knowledge_Base.py
│   ├── 4_Analytics.py
│   └── 5_Settings.py
├── chatbot/
│   ├── __init__.py
│   ├── memory.py
│   ├── prompts.py
│   └── response_builder.py
├── rag/
│   ├── __init__.py
│   ├── chunker.py
│   ├── embedder.py
│   ├── vector_store.py
│   ├── retriever.py
│   └── pipeline.py
├── ingestion/
│   ├── __init__.py
│   ├── pdf_loader.py
│   ├── docx_loader.py
│   ├── csv_loader.py
│   └── website_loader.py
├── database/
│   ├── __init__.py
│   ├── models.py
│   └── repository.py
├── tests/
│   ├── __init__.py
│   ├── test_chunker.py
│   ├── test_embedder.py
│   ├── test_vector_store.py
│   ├── test_retriever.py
│   ├── test_pipeline.py
│   ├── test_memory.py
│   ├── test_prompts.py
│   ├── test_response_builder.py
│   ├── test_pdf_loader.py
│   ├── test_docx_loader.py
│   ├── test_csv_loader.py
│   └── test_website_loader.py
├── .env
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── .project/
```
