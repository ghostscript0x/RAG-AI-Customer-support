"""Analytics page — view conversation metrics and stats."""

import logging
from datetime import datetime, timedelta

import streamlit as st
from collections import Counter

from chatbot.sidebar import init_session_state, render_sidebar
from database.repository import get_conversation_stats, get_recent_conversations

logger = logging.getLogger(__name__)


def main() -> None:
    """View chat analytics and metrics."""
    init_session_state()
    st.session_state.current_page = "4_Analytics"
    render_sidebar()

    st.title(":bar_chart: Analytics")

    stats = get_conversation_stats()
    conversations = get_recent_conversations(limit=100)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Conversations", stats["total_conversations"])
    with col2:
        st.metric("Avg Response Time", f"{stats['avg_response_time_ms']:.0f}ms")
    with col3:
        st.metric("Answered", stats["answered"])
    with col4:
        st.metric("Unanswered", stats["unanswered"])

    st.divider()

    if not conversations:
        st.info("No conversation data yet. Start chatting to see analytics here.")
        return

    st.subheader("Recent Conversations")
    for conv in conversations[:10]:
        with st.container(border=True):
            st.markdown(f"**Q:** {conv['question'][:200]}")
            st.markdown(f"**A:** {conv['answer'][:200]}...")
            st.caption(
                f"Confidence: {conv['confidence']:.2f} | "
                f"Response: {conv['response_time_ms']}ms | "
                f"{conv['created_at'][:19] if conv['created_at'] else 'N/A'}"
            )

    st.divider()

    st.subheader("Top Questions")
    questions = [c["question"] for c in conversations if c.get("question")]
    if questions:
        top_questions = Counter(questions).most_common(10)
        for i, (q, count) in enumerate(top_questions, 1):
            st.markdown(f"{i}. \"{q[:100]}\" — asked {count} time(s)")

    st.divider()

    st.subheader("Daily Activity (Last 7 Days)")
    today = datetime.utcnow()
    daily_counts: dict = {}
    for i in range(7):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        daily_counts[day] = 0

    for conv in conversations:
        if conv.get("created_at"):
            day = conv["created_at"][:10]
            if day in daily_counts:
                daily_counts[day] += 1

    if daily_counts:
        days = sorted(daily_counts.keys())
        counts = [daily_counts[d] for d in days]
        chart_data = {"Day": days, "Conversations": counts}
        st.bar_chart(chart_data, x="Day", y="Conversations")


if __name__ == "__main__":
    main()
