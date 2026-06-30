"""New Chat page — send messages and stream responses from Groq."""

import logging

import streamlit as st

from chatbot.groq_client import get_groq_client, stream_response
from chatbot.prompts import build_prompt
from chatbot.sidebar import render_sidebar

logger = logging.getLogger(__name__)


def main() -> None:
    """Render the chat interface."""
    st.session_state.current_page = "1_New_Chat"
    render_sidebar()

    st.title(":speech_balloon: New Chat")

    client = get_groq_client()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask a question about your knowledge base..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if client:
            messages = [{"role": "system", "content": "You are a helpful customer support assistant."}]
            messages.extend(st.session_state.messages[-10:])
            with st.chat_message("assistant"):
                try:
                    response = stream_response(client, messages)
                    if response:
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response}
                        )
                except Exception:
                    st.error("Failed to get a response from the AI. Please try again.")
        else:
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "I'm not fully configured yet. Please set up your GROQ_API_KEY in Settings to start chatting.",
                }
            )
            st.rerun()

    if st.session_state.messages and st.sidebar.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()


if __name__ == "__main__":
    main()
