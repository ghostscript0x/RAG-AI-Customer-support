"""Upload page — upload documents to the knowledge base."""

import logging
import os
import tempfile
from pathlib import Path

import streamlit as st

from chatbot.sidebar import render_sidebar
from database.repository import add_document
from rag.pipeline import ingest_file, ingest_website

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".csv"}


def main() -> None:
    """Upload documents to the knowledge base."""
    st.session_state.current_page = "2_Upload"
    render_sidebar()

    st.title(":open_file_folder: Upload Documents")
    st.caption("Supported formats: PDF, DOCX, CSV, and website URLs")

    tab_files, tab_website = st.tabs(["File Upload", "Website URL"])

    with tab_files:
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            type=["pdf", "docx", "csv"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                ext = Path(uploaded_file.name).suffix.lower()
                if ext not in ALLOWED_EXTENSIONS:
                    st.warning(f"Skipping unsupported file: {uploaded_file.name}")
                    continue

                with st.status(f"Processing {uploaded_file.name}...") as status:
                    try:
                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix=ext
                        ) as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name

                        success, chunk_count, message = ingest_file(tmp_path)

                        if success:
                            add_document(
                                filename=uploaded_file.name,
                                source=uploaded_file.name,
                                doc_type=ext[1:],
                                chunk_count=chunk_count,
                            )
                            status.update(
                                label=f":white_check_mark: {uploaded_file.name} — {chunk_count} chunks",
                                state="complete",
                            )
                        else:
                            status.update(
                                label=f":x: {uploaded_file.name} — {message}",
                                state="error",
                            )
                    except Exception as exc:
                        logger.exception("Upload failed for %s", uploaded_file.name)
                        status.update(
                            label=f":x: {uploaded_file.name} — {str(exc)}",
                            state="error",
                        )
                    finally:
                        if "tmp_path" in locals():
                            os.unlink(tmp_path)

    with tab_website:
        url = st.text_input("Enter a website URL to ingest:")
        if url and st.button("Ingest Website", type="primary"):
            if not url.startswith(("http://", "https://")):
                st.error("Please enter a valid URL starting with http:// or https://")
            else:
                with st.status(f"Ingesting {url}...") as status:
                    try:
                        success, chunk_count, message = ingest_website(url)
                        if success:
                            add_document(
                                filename=url,
                                source=url,
                                doc_type="website",
                                chunk_count=chunk_count,
                            )
                            status.update(
                                label=f":white_check_mark: {url} — {chunk_count} chunks",
                                state="complete",
                            )
                        else:
                            status.update(
                                label=f":x: {message}",
                                state="error",
                            )
                    except Exception as exc:
                        logger.exception("Website ingestion failed for %s", url)
                        status.update(
                            label=f":x: {str(exc)}",
                            state="error",
                        )


if __name__ == "__main__":
    main()
