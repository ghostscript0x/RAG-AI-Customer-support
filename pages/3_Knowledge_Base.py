"""Knowledge Base page — manage indexed documents."""

import streamlit as st

from chatbot.sidebar import render_sidebar


def main() -> None:
    """Manage knowledge base documents."""
    st.session_state.current_page = "3_Knowledge_Base"
    render_sidebar()

    st.title(":books: Knowledge Base")
    st.info("Knowledge Base management will be available in the next update.")


if __name__ == "__main__":
    main()
