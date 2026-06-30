# Agent Roles — RAG AI Customer Support Chatbot

Since this tool runs in a single context (no sub-agent delegation), the roles below are worked through sequentially per phase by the same agent. They define focus areas, not parallel workers.

| Role | Responsibility | Key Outputs |
|------|---------------|-------------|
| **Architect** | Project structure, module interfaces, ADRs | `.project/DECISIONS.md`, directory tree, module stubs |
| **RAG Engineer** | `rag/` + `ingestion/` — chunking, embedding, retrieval, vector store, all loaders | `rag/*.py`, `ingestion/*.py`, corresponding tests |
| **Chat Engineer** | `chatbot/` — prompts, memory, response builder, Groq streaming integration | `chatbot/*.py`, Groq client, streaming UI |
| **UI Engineer** | `app.py`, `pages/*` — Streamlit pages, session state, navigation | All page files, `.streamlit/config.toml` |
| **QA** | Tests, Definition of Done verification, edge case review | All `tests/*.py` files, stage sign-off |

## Workflow per Phase
1. Architect reviews the phase scope and updates DECISIONS.md with any choices
2. RAG Engineer / Chat Engineer / UI Engineer builds the code (depending on phase)
3. QA writes/updates tests and runs them
4. QA checks Definition of Done and marks phase complete in STAGES.md
5. Architect updates STATE.md
