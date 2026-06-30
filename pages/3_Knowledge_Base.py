"""Knowledge Base page — manage indexed documents."""

import logging

import streamlit as st

from chatbot.sidebar import render_sidebar
from database.repository import list_documents, delete_document as delete_doc_record
from rag.vector_store import delete_documents as delete_vs_docs, list_documents as list_vs_docs, add_documents
from rag.chunker import chunk_text
from rag.embedder import embed_batch
from rag.pipeline import ingest_file
import tempfile
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def main() -> None:
    """Manage knowledge base documents."""
    st.session_state.current_page = "3_Knowledge_Base"
    render_sidebar()

    st.title(":books: Knowledge Base")

    docs = list_documents()

    if not docs:
        st.info("No documents in the knowledge base yet. Go to the Upload page to add some.")
        return

    st.markdown(f"**{len(docs)} document(s) indexed**")

    for doc in docs:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{doc['filename']}**")
                st.caption(
                    f"Type: {doc['doc_type']} | Chunks: {doc['chunk_count']} | "
                    f"Added: {doc['created_at'][:10] if doc['created_at'] else 'N/A'}"
                )
            with col2:
                if st.button("Re-index", key=f"reindex_{doc['id']}", use_container_width=True):
                    _reindex_document(doc)
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"delete_{doc['id']}", type="secondary", use_container_width=True):
                    _delete_document(doc)
                    st.rerun()


def _delete_document(doc: dict) -> None:
    """Delete a document from both SQLite and vector store.

    Args:
        doc: The document dict from the database.
    """
    vs_docs = list_vs_docs()
    vs_ids = [
        v["id"]
        for v in vs_docs
        if v.get("metadata", {}).get("source") == doc["source"]
    ]
    if vs_ids:
        delete_vs_docs(vs_ids)
    delete_doc_record(doc["id"])
    st.success(f"Deleted {doc['filename']}")


def _reindex_document(doc: dict) -> None:
    """Delete and re-ingest a document.

    Args:
        doc: The document dict from the database.
    """
    vs_docs = list_vs_docs()
    vs_ids = [
        v["id"]
        for v in vs_docs
        if v.get("metadata", {}).get("source") == doc["source"]
    ]
    if vs_ids:
        delete_vs_docs(vs_ids)

    delete_doc_record(doc["id"])

    if doc["doc_type"] == "website":
        from rag.pipeline import ingest_website
        success, chunk_count, message = ingest_website(doc["source"])
    else:
        success, chunk_count, message = ingest_file(doc["source"])

    if success:
        from database.repository import add_document
        add_document(
            filename=doc["filename"],
            source=doc["source"],
            doc_type=doc["doc_type"],
            chunk_count=chunk_count,
        )
        st.success(f"Re-indexed {doc['filename']} ({chunk_count} chunks)")
    else:
        st.error(f"Re-index failed: {message}")


if __name__ == "__main__":
    main()
