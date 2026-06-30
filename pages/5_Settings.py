"""Settings page — view environment configuration."""

import os

import streamlit as st

from chatbot.sidebar import render_sidebar


def main() -> None:
    """Display environment configuration."""
    st.session_state.current_page = "5_Settings"
    render_sidebar()

    st.title(":gear: Settings")

    st.subheader("Environment Configuration")
    st.caption("These values are read from your .env file and cannot be changed here at runtime.")

    config_vars = {
        "GROQ_MODEL": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5"),
        "TOP_K": os.getenv("TOP_K", "5"),
        "CONFIDENCE_THRESHOLD": os.getenv("CONFIDENCE_THRESHOLD", "0.65"),
        "CHROMA_PERSIST_DIR": os.getenv("CHROMA_PERSIST_DIR", "./chroma_db"),
    }

    api_key = os.getenv("GROQ_API_KEY", "")
    masked_key = api_key[:8] + "..." if api_key and api_key != "your-groq-api-key-here" else "Not configured"

    st.markdown(f"**GROQ_API_KEY:** `{masked_key}`")

    for var, val in config_vars.items():
        st.markdown(f"**{var}:** `{val}`")

    st.subheader("About")
    st.markdown(
        """
        **RAG AI Customer Support Chatbot** v1.0.0

        Built with Streamlit, Groq, ChromaDB, and BGE embeddings.

        Retrieves answers from your uploaded knowledge base documents.
        """
    )


if __name__ == "__main__":
    main()
