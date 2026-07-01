"""Main entry point for the RAG AI Customer Support Chatbot."""

import logging

import streamlit as st
from dotenv import load_dotenv

from chatbot.sidebar import init_session_state, render_sidebar
from database.models import init_db

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

init_db()


def main() -> None:
    """Render the app shell."""
    st.set_page_config(
        page_title="RAG AI Support Chatbot",
        page_icon=":speech_balloon:",
        layout="wide",
    )
    init_session_state()
    render_sidebar()

    st.title("Welcome to RAG AI Support!")
    st.markdown(
        """
        Ask questions about your knowledge base documents.

        **Get started:**
        1. Upload documents in the **Upload** page
        2. Ask questions in **New Chat**
        3. View conversation stats in **Analytics**
        """
    )


if __name__ == "__main__":
    main()
