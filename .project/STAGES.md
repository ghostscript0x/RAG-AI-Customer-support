# Build Stages — RAG AI Customer Support Chatbot

## Phase 0: Scaffolding
- [x] Create `.project/` directory with CONTEXT.md, RULES.md, STAGES.md, AGENTS.md, STATE.md, DECISIONS.md
- [x] Create full directory tree (app.py, pages/, chatbot/, rag/, ingestion/, database/, tests/, .env, requirements.txt)
- [x] Initialize git repo + first commit

## Phase 1: Foundation
- [x] `app.py` — Streamlit shell with sidebar navigation
- [x] `pages/1_New_Chat.py` — chat UI with message history
- [x] `pages/5_Settings.py` — env var viewer (read-only)
- [x] `chatbot/prompts.py` — system prompt (grounded, no hallucination)
- [x] Groq integration with streaming response
- [x] Session state for chat history
- [x] Tests for Groq integration
- [x] **Definition of Done:** `streamlit run app.py` boots, send message → streamed Groq response, no RAG yet

## Phase 2: RAG Core
- [x] `ingestion/pdf_loader.py` — PDF text extraction
- [x] `ingestion/docx_loader.py` — DOCX text extraction
- [x] `ingestion/csv_loader.py` — CSV text extraction
- [x] `ingestion/website_loader.py` — website scraping
- [x] `rag/chunker.py` — text chunking with overlap
- [x] `rag/embedder.py` — BAAI/bge-base-en-v1.5 embeddings
- [x] `rag/vector_store.py` — ChromaDB operations
- [x] `rag/retriever.py` — top-k retrieval with scores
- [x] `rag/pipeline.py` — wiring: load → chunk → embed → store / retrieve
- [x] Tests for all RAG modules
- [x] **Definition of Done:** PDF ingested, chunked, embedded, stored; query returns relevant chunks with scores in <500ms

## Phase 3: Knowledge Management
- [x] `database/models.py` — SQLAlchemy models (documents, conversations)
- [x] `database/repository.py` — CRUD operations
- [x] `pages/2_Upload.py` — drag-drop upload with progress + chunk count
- [x] `pages/3_Knowledge_Base.py` — list, delete, re-index documents
- [x] Wire upload → ingestion → indexing pipeline
- [x] Persist document metadata to SQLite
- [x] Tests for database layer
- [x] **Definition of Done:** Full upload→index→list→delete→re-index cycle through UI

## Phase 4: Intelligence
- [x] `chatbot/memory.py` — session-scoped conversation memory, pronoun resolution
- [x] `chatbot/prompts.py` — grounded system prompt (final version with citation/escalation rules)
- [x] `chatbot/response_builder.py` — answer + citations + follow-ups
- [x] Confidence scoring on retrieval results
- [x] Wire RAG pipeline into chat flow
- [x] Tests for memory, prompts, response builder
- [x] **Definition of Done:** Multi-turn pronoun resolution; grounded, cited answer; "not confident" escalation for out-of-scope queries

## Phase 5: Polish
- [x] `pages/4_Analytics.py` — conversation stats, response time, top questions, daily chart
- [x] Error handling pass across all modules
- [x] `Dockerfile` + `docker-compose.yml`
- [x] `README.md` — setup, env vars, Docker, streamlit run instructions
- [x] Final test suite run — 65/65 passing
- [x] Final STATE.md update
- [x] **Definition of Done:** `docker-compose up` boots from clean checkout; analytics shows real data; `pytest` passes clean
