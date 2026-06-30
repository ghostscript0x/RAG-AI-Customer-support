"""Analytics page — view conversation metrics."""

import streamlit as st

from chatbot.sidebar import render_sidebar


def main() -> None:
    """View chat analytics and metrics."""
    st.session_state.current_page = "4_Analytics"
    render_sidebar()

    st.title(":bar_chart: Analytics")
    st.info("Analytics will be available after some conversations have been recorded.")


if __name__ == "__main__":
    main()
