# Architecture Decision Log

## ADR-001: Single-context sequential build (no sub-agents)
**Date:** 2026-06-30
**Context:** AGENTS.md defines roles but the tool doesn't support parallel sub-agent invocation.
**Decision:** Work through roles sequentially per phase. Architect → RAG Engineer → Chat Engineer → UI Engineer → QA per phase.

## ADR-002: SQLite for MVP relational store
**Date:** 2026-06-30
**Context:** Need lightweight persistence for conversations, documents, analytics.
**Decision:** SQLite via SQLAlchemy. Zero infrastructure, trivially portable to PostgreSQL later.

## ADR-003: BAAI/bge-base-en-v1.5 for embeddings
**Date:** 2026-06-30
**Context:** Need a local embedding model (no API cost, no latency). Must run on CPU.
**Decision:** bge-base-en-v1.5 via sentence-transformers. 768-dim, good retrieval benchmarks, small enough for CPU inference.

## ADR-004: ChromaDB for vector store
**Date:** 2026-06-30
**Context:** Need persistent vector storage with similarity search.
**Decision:** ChromaDB. Embed + persist locally, no external service. Default persist dir `./chroma_db`.

## ADR-005: Default CONFIDENCE_THRESHOLD = 0.65
**Date:** 2026-06-30
**Context:** Need a sane default for when to escalate vs answer from context.
**Decision:** 0.65 (cosine similarity). Can be tuned via env var. Below this, the bot says "not confident" and offers escalation.

## ADR-006: Default TOP_K = 5
**Date:** 2026-06-30
**Context:** Need enough context chunks for a good answer without blowing the prompt window.
**Decision:** 5 chunks retrieved. Configurable via TOP_K env var.

## ADR-007: Conversation memory is session-scoped (in-memory)
**Date:** 2026-06-30
**Context:** MVP doesn't need persistent multi-session conversation history.
**Decision:** Store conversation history in Streamlit session state. Persist to SQLite for analytics only. Future: user auth → persistent per-user history.
