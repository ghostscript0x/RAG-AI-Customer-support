"""Upload page — upload documents to the knowledge base."""

import streamlit as st

from chatbot.sidebar import render_sidebar


def main() -> None:
    """Upload documents to the knowledge base."""
    st.session_state.current_page = "2_Upload"
    render_sidebar()

    st.title(":open_file_folder: Upload Documents")
    st.info("Document upload will be available in the next update. Please use the New Chat page for now.")


if __name__ == "__main__":
    main()
