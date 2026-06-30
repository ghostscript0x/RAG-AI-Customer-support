# RAG AI Customer Support Chatbot

A production-ready RAG-based AI Customer Support Chatbot that ingests product manuals, policy PDFs, and website docs, then answers natural-language questions grounded in that knowledge base.

## Features

- **Multi-format ingestion** — PDF, DOCX, CSV, and website scraping
- **Intelligent chunking** — semantic-aware text splitting with overlap
- **Local embeddings** — BAAI/bge-base-en-v1.5 via sentence-transformers
- **Vector store** — ChromaDB persisted to disk
- **Retrieval-augmented generation** — top-k chunks injected into Groq prompt
- **Conversation memory** — session-scoped with pronoun resolution
- **Grounded responses** — never hallucinates, always cites sources
- **Confidence scoring** — escalates below configurable threshold
- **Knowledge Base management** — upload, list, delete, re-index via UI
- **Analytics dashboard** — conversation stats, top questions, daily trends

## Tech Stack

| Layer | Choice |
|-------|--------|
| Frontend | Streamlit |
| LLM | Groq API (model configurable via `GROQ_MODEL`) |
| Embeddings | BAAI/bge-base-en-v1.5 (sentence-transformers, local) |
| Vector DB | ChromaDB (persisted to disk) |
| Relational DB | SQLite via SQLAlchemy |

## Prerequisites

- Python 3.11+
- Groq API key ([get one free](https://console.groq.com/))

## Quick Start (Local)

```bash
# 1. Clone and enter the directory
git clone <repo-url> && cd rag-ai

# 2. Create a .env file with your Groq API key
echo "GROQ_API_KEY=gsk_your_key_here" > .env

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Docker

```bash
# Build and run with Docker Compose
docker compose up --build
```

Or with plain Docker:

```bash
docker build -t rag-ai-chatbot .
docker run -p 8501:8501 --env-file .env -v "$(pwd)/chroma_db:/app/chroma_db" -v "$(pwd)/rag_ai.db:/app/rag_ai.db" rag-ai-chatbot
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | Your Groq API key (required) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | LLM model to use |
| `EMBEDDING_MODEL` | `BAAI/bge-base-en-v1.5` | Sentence-transformer model |
| `TOP_K` | `5` | Number of chunks to retrieve |
| `CONFIDENCE_THRESHOLD` | `0.65` | Minimum confidence to answer without escalating |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB persistence directory |

## Project Structure

```
rag-ai/
├── app.py                         # Streamlit entry point
├── pages/                         # Streamlit pages
│   ├── 1_New_Chat.py              # Chat interface
│   ├── 2_Upload.py                # Document upload
│   ├── 3_Knowledge_Base.py        # KB management
│   ├── 4_Analytics.py             # Analytics dashboard
│   └── 5_Settings.py              # Configuration viewer
├── chatbot/                       # LLM interaction layer
│   ├── groq_client.py             # Groq API wrapper
│   ├── memory.py                  # Conversation memory
│   ├── prompts.py                 # System prompts
│   ├── response_builder.py        # Response assembly
│   └── sidebar.py                 # Shared navigation
├── rag/                           # RAG pipeline
│   ├── chunker.py                 # Text chunking
│   ├── embedder.py                # Embedding generation
│   ├── vector_store.py            # ChromaDB operations
│   ├── retriever.py               # Retrieval + confidence
│   └── pipeline.py                # Orchestration
├── ingestion/                     # Document loaders
│   ├── pdf_loader.py
│   ├── docx_loader.py
│   ├── csv_loader.py
│   └── website_loader.py
├── database/                      # SQLite persistence
│   ├── models.py
│   └── repository.py
├── tests/                         # Test suite
├── .env                           # Configuration
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Testing

```bash
pytest tests/ -v
```

## Architecture Decisions

See `.project/DECISIONS.md` for the full architecture decision log.
