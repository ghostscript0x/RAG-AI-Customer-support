"""Main entry point for the RAG AI Customer Support Chatbot."""

import logging

import streamlit as st
from dotenv import load_dotenv

from chatbot.sidebar import render_sidebar

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def init_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = ""


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
