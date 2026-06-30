"""New Chat page — send messages and get RAG-grounded responses from Groq."""

import logging
import os
import time
import uuid

import streamlit as st

from chatbot.groq_client import get_groq_client, stream_response
from chatbot.memory import resolve_pronouns
from chatbot.prompts import build_prompt
from chatbot.response_builder import assemble_response, parse_sources_from_response
from chatbot.sidebar import render_sidebar
from database.repository import add_conversation
from rag.retriever import retrieve, compute_confidence

logger = logging.getLogger(__name__)


def main() -> None:
    """Render the chat interface with RAG-grounded responses."""
    st.session_state.current_page = "1_New_Chat"
    render_sidebar()

    st.title(":speech_balloon: New Chat")

    client = get_groq_client()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("Sources", expanded=False):
                    for s in msg["sources"][:5]:
                        st.caption(f"- {s}")

    if prompt := st.chat_input("Ask a question about your knowledge base..."):
        if not client:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I'm not fully configured yet. Please set up your GROQ_API_KEY in Settings to start chatting.",
                "sources": [],
            })
            st.rerun()

        start_time = time.time()

        resolved_prompt = resolve_pronouns(prompt, st.session_state.messages)

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        retrieval_results = retrieve(resolved_prompt)
        confidence = compute_confidence(retrieval_results)
        context = _format_context(retrieval_results)
        source_docs = list(
            dict.fromkeys(
                r.get("metadata", {}).get("source", "Unknown") for r in retrieval_results
            )
        )

        full_prompt = build_prompt(
            question=resolved_prompt,
            context=context,
            history=st.session_state.messages[:-1],
        )

        with st.chat_message("assistant"):
            try:
                rag_messages = [{"role": "system", "content": full_prompt}]
                for msg in st.session_state.messages[:-1]:
                    rag_messages.append({"role": msg["role"], "content": msg["content"]})
                rag_messages.append({"role": "user", "content": resolved_prompt})
                response_text = stream_response(client, rag_messages)

                if response_text:
                    final_response = assemble_response(
                        response_text, source_docs, confidence
                    )
                    st.markdown(final_response)

                    parsed_sources = parse_sources_from_response(response_text)
                    if not parsed_sources:
                        parsed_sources = source_docs

                    elapsed = int((time.time() - start_time) * 1000)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": final_response,
                        "sources": parsed_sources,
                        "confidence": confidence,
                    })

                    session_id = st.session_state.get(
                        "conversation_id", str(uuid.uuid4())[:8]
                    )
                    st.session_state.conversation_id = session_id

                    add_conversation(
                        session_id=session_id,
                        question=prompt,
                        answer=final_response,
                        confidence=confidence,
                        sources=", ".join(parsed_sources[:5]),
                        response_time_ms=elapsed,
                    )

                    if parsed_sources:
                        with st.expander("Sources", expanded=False):
                            for s in parsed_sources[:5]:
                                st.caption(f"- {s}")
                else:
                    st.error("Failed to get a response from the AI.")

            except Exception as exc:
                logger.exception("Chat error")
                st.error("Something went wrong. Please try again.")

    if st.session_state.messages and st.sidebar.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()


def _format_context(retrieval_results: list) -> str:
    """Format retrieval results into a context string for the prompt.

    Args:
        retrieval_results: List of retrieval result dicts.

    Returns:
        A formatted context string.
    """
    if not retrieval_results:
        return ""
    parts = []
    for i, r in enumerate(retrieval_results, 1):
        source = r.get("metadata", {}).get("source", "Unknown")
        score = r.get("score", 0.0)
        doc = r.get("document", "")
        parts.append(f"[Passage {i}] (Source: {source}, Relevance: {score:.2f})\n{doc}")
    return "\n\n".join(parts)


if __name__ == "__main__":
    main()
