"""Session-scoped conversation memory with pronoun/context resolution."""

import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

PRONOUN_PATTERN = re.compile(
    r"\b(it|they|them|this|that|these|those|he|she|him|her|his|hers)\b",
    re.IGNORECASE,
)


def resolve_pronouns(question: str, history: List[Dict[str, str]]) -> str:
    """Resolve pronoun references in a question using conversation history.

    Looks at the last 2 assistant messages for noun phrases to substitute.

    Args:
        question: The current user question.
        history: The conversation history (list of {"role": ..., "content": ...}).

    Returns:
        The question with pronouns resolved where possible, or the original question.
    """
    if not PRONOUN_PATTERN.search(question):
        return question

    candidates: List[str] = []
    for msg in reversed(history):
        if msg["role"] == "assistant":
            nouns = _extract_noun_phrases(msg["content"])
            candidates.extend(nouns)
        if len(candidates) >= 3:
            break

    if not candidates:
        return question

    resolved = question
    for pronoun, replacement in PRONOUN_MAP.items():
        if pronoun in resolved.lower():
            resolved = re.sub(
                rf"\b{pronoun}\b",
                candidates[0],
                resolved,
                flags=re.IGNORECASE,
                count=1,
            )
            break

    return resolved


PRONOUN_MAP = {
    "it": "it",
    "they": "they",
    "them": "them",
    "this": "this",
    "that": "that",
    "these": "these",
    "those": "those",
    "he": "he",
    "she": "she",
    "him": "him",
    "her": "her",
    "his": "his",
    "hers": "hers",
}


def _extract_noun_phrases(text: str) -> List[str]:
    """Extract likely noun phrases from a text.

    Uses a simple heuristic: capitalized multi-word sequences and
    phrases after prepositions.

    Args:
        text: The text to extract from.

    Returns:
        A list of candidate noun phrases.
    """
    candidates = []
    capitalized = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)
    candidates.extend(capitalized)

    topics = re.findall(r"(?:about|regarding|for|of|like)\s+([A-Za-z][A-Za-z0-9\s]+?)(?:\.|,|$)", text)
    candidates.extend(t.strip() for t in topics if t.strip())

    return candidates


def get_recent_history(history: List[Dict[str, str]], limit: int = 6) -> List[Dict[str, str]]:
    """Get the most recent history messages.

    Args:
        history: Full conversation history.
        limit: Max number of messages to return.

    Returns:
        The most recent messages.
    """
    return history[-limit:] if len(history) > limit else history
