# RAG AI Customer Support Chatbot — Product Context

## Vision
An internal AI Customer Support Chatbot that lets a company's support team upload product manuals, policy PDFs, and website docs, then ask natural-language questions against that knowledge base. Responses are grounded in retrieved documents, cited, and escalate gracefully when confidence is low. No hallucinations, no robotic replies.

## Core Features (1–10)
1. **Multi-format ingestion** — PDF, DOCX, CSV, website scraping
2. **Intelligent chunking** — semantic-aware text splitting
3. **Local embeddings** — BAAI/bge-base-en-v1.5 via sentence-transformers
4. **Vector store** — ChromaDB persisted to disk
5. **Retrieval-augmented generation** — top-k chunks injected into Groq prompt
6. **Conversation memory** — session-scoped, resolves pronouns/ellipsis
7. **Grounded responses** — never hallucinates, always cites sources
8. **Confidence scoring** — escalates below configurable threshold
9. **Knowledge Base management** — upload, list, delete, re-index via UI
10. **Analytics dashboard** — conversation stats, top questions, daily trends

## Tech Stack
| Layer | Choice |
|-------|--------|
| Frontend | Streamlit |
| LLM | Groq API (model via `GROQ_MODEL`, default `llama-3.3-70b-versatile`) |
| Embeddings | `BAAI/bge-base-en-v1.5` via sentence-transformers, local |
| Vector DB | ChromaDB, persisted to disk |
| Relational DB | SQLite via SQLAlchemy |
| Core libs | streamlit, groq, sentence-transformers, chromadb, torch, pypdf, python-docx, beautifulsoup4, markdown, requests, sqlalchemy, python-dotenv, tiktoken, pytest |

## Non-Negotiables
- Never hallucinate — if retrieved context is insufficient, say so and escalate
- Always cite sources for grounded answers
- Environment-var-driven model configuration (no hardcoded model names or secrets)
- Every external call wrapped in try/except with graceful degradation
- No raw stack traces to UI
