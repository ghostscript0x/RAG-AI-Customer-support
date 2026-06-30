"""Response builder — assembles answer, source citations, and suggested follow-ups."""

import logging
import os
import re
from typing import List, Optional

logger = logging.getLogger(__name__)


def build_sources_section(sources: List[str]) -> str:
    """Build a formatted sources section from document names.

    Args:
        sources: List of source document names.

    Returns:
        A markdown-formatted sources string.
    """
    if not sources:
        return ""
    unique = list(dict.fromkeys(sources))
    lines = ["\n\n**Sources:**"]
    for s in unique[:5]:
        lines.append(f"- {s}")
    return "\n".join(lines)


def parse_sources_from_response(response: str) -> List[str]:
    """Extract source document names from a response.

    Looks for patterns like (Source: ...) or **Sources:** blocks.

    Args:
        response: The assistant's response text.

    Returns:
        A list of source document names.
    """
    sources = re.findall(r"\(Source:\s*([^)]+)\)", response)
    return [s.strip() for s in sources]


def build_follow_up_suggestions(context: str) -> List[str]:
    """Generate follow-up question suggestions based on the retrieved context.

    Args:
        context: The retrieved knowledge base context.

    Returns:
        A list of suggested follow-up questions.
    """
    topics = re.findall(r"Source:\s*([^\n]+)", context)
    topics = list(dict.fromkeys(topics))[:3]

    if not topics:
        topics = re.findall(r"(?:about|regarding|for)\s+([A-Za-z][A-Za-z0-9\s/]+?)(?:\.|,|$)", context)
        topics = [t.strip() for t in topics[:3]]

    suggestions = []
    for topic in topics:
        topic_short = topic.split("/")[-1].split("\\")[-1].strip()
        suggestions.append(f"Tell me more about {topic_short}")

    if not suggestions:
        suggestions = ["Can you explain that in more detail?", "What related topics are available?"]

    return suggestions[:3]


def assemble_response(
    llm_answer: str,
    source_docs: List[str],
    confidence: float,
) -> str:
    """Assemble the final response with answer, citations, and follow-ups.

    Args:
        llm_answer: The raw answer from the LLM.
        source_docs: List of source document names.
        confidence: The retrieval confidence score.

    Returns:
        The complete response string.
    """
    threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))

    if confidence < threshold and not source_docs:
        return (
            "I don't have enough information from the knowledge base to answer that fully. "
            "I'd recommend reaching out to our support team who can help you with this."
        )

    sources_section = build_sources_section(source_docs)
    return llm_answer + sources_section
