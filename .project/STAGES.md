# Build Stages — RAG AI Customer Support Chatbot

## Phase 0: Scaffolding
- [x] Create `.project/` directory with CONTEXT.md, RULES.md, STAGES.md, AGENTS.md, STATE.md, DECISIONS.md
- [ ] Create full directory tree (app.py, pages/, chatbot/, rag/, ingestion/, database/, tests/, .env, requirements.txt)
- [ ] Initialize git repo + first commit

## Phase 1: Foundation
- [ ] `app.py` — Streamlit shell with sidebar navigation
- [ ] `pages/1_New_Chat.py` — chat UI with message history
- [ ] `pages/5_Settings.py` — env var viewer (read-only)
- [ ] `chatbot/prompts.py` — system prompt (grounded, no hallucination)
- [ ] Groq integration with streaming response
- [ ] Session state for chat history
- [ ] Tests for Groq integration
- [ ] **Definition of Done:** `streamlit run app.py` boots, send message → streamed Groq response, no RAG yet

## Phase 2: RAG Core
- [ ] `ingestion/pdf_loader.py` — PDF text extraction
- [ ] `ingestion/docx_loader.py` — DOCX text extraction
- [ ] `ingestion/csv_loader.py` — CSV text extraction
- [ ] `ingestion/website_loader.py` — website scraping
- [ ] `rag/chunker.py` — text chunking with overlap
- [ ] `rag/embedder.py` — BAAI/bge-base-en-v1.5 embeddings
- [ ] `rag/vector_store.py` — ChromaDB operations
- [ ] `rag/retriever.py` — top-k retrieval with scores
- [ ] `rag/pipeline.py` — wiring: load → chunk → embed → store / retrieve
- [ ] Tests for all RAG modules
- [ ] **Definition of Done:** PDF ingested, chunked, embedded, stored; query returns relevant chunks with scores in <500ms

## Phase 3: Knowledge Management
- [ ] `database/models.py` — SQLAlchemy models (documents, conversations)
- [ ] `database/repository.py` — CRUD operations
- [ ] `pages/2_Upload.py` — drag-drop upload with progress + chunk count
- [ ] `pages/3_Knowledge_Base.py` — list, delete, re-index documents
- [ ] Wire upload → ingestion → indexing pipeline
- [ ] Persist document metadata to SQLite
- [ ] Tests for database layer
- [ ] **Definition of Done:** Full upload→index→list→delete→re-index cycle through UI

## Phase 4: Intelligence
- [ ] `chatbot/memory.py` — session-scoped conversation memory, pronoun resolution
- [ ] `chatbot/prompts.py` — grounded system prompt (final version with citation/escalation rules)
- [ ] `chatbot/response_builder.py` — answer + citations + follow-ups
- [ ] Confidence scoring on retrieval results
- [ ] Wire RAG pipeline into chat flow
- [ ] Tests for memory, prompts, response builder
- [ ] **Definition of Done:** Multi-turn pronoun resolution; grounded, cited answer; "not confident" escalation for out-of-scope queries

## Phase 5: Polish
- [ ] `pages/4_Analytics.py` — conversation stats, response time, top questions, daily chart
- [ ] Error handling pass across all modules
- [ ] `Dockerfile` + `docker-compose.yml`
- [ ] `README.md` — setup, env vars, Docker, streamlit run instructions
- [ ] Final test suite run — fix everything red
- [ ] Final STATE.md update
- [ ] **Definition of Done:** `docker-compose up` boots from clean checkout; analytics shows real data; `pytest` passes clean
