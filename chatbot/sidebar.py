"""Shared sidebar navigation for all pages."""

import streamlit as st


def render_sidebar() -> None:
    """Render shared sidebar navigation with links to all pages."""
    st.sidebar.title("RAG AI Support")
    st.sidebar.markdown("---")

    pages = {
        "New Chat": "1_New_Chat",
        "Upload": "2_Upload",
        "Knowledge Base": "3_Knowledge_Base",
        "Analytics": "4_Analytics",
        "Settings": "5_Settings",
    }

    current_page = st.session_state.get("current_page", "")
    for label, page_id in pages.items():
        if st.sidebar.button(
            label,
            key=f"nav_{page_id}",
            use_container_width=True,
            type="secondary" if page_id == current_page else "tertiary",
        ):
            st.switch_page(f"pages/{page_id}.py")

    st.sidebar.markdown("---")
    st.sidebar.caption("v1.0.0")
