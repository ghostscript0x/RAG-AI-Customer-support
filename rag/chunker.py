"""Text chunking with configurable size and overlap."""

import logging
from typing import List

logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks of approximately equal size.

    Splits on sentence boundaries when possible, falling back to word boundaries.

    Args:
        text: The text to chunk.
        chunk_size: Target number of characters per chunk.
        overlap: Number of characters of overlap between consecutive chunks.

    Returns:
        A list of text chunks.
    """
    if not text or chunk_size <= 0:
        return []

    chunks: List[str] = []
    start = 0
    text_len = len(text)

    if text_len <= chunk_size:
        return [text.strip()]

    last_end = 0
    while start < text_len:
        end = min(start + chunk_size, text_len)

        if end < text_len:
            end = _find_sentence_boundary(text, end)

        if end <= last_end:
            end = min(last_end + chunk_size, text_len)

        chunks.append(text[start:end].strip())
        last_end = end

        if end >= text_len:
            break

        start = end - overlap

        if start <= last_end - overlap:
            start = last_end

        if start < 0:
            start = 0

    return [c for c in chunks if c]


def _find_sentence_boundary(text: str, position: int) -> int:
    """Find the nearest sentence end near the given position.

    Searches forward up to 100 characters for a sentence-ending punctuation.

    Args:
        text: The full text.
        position: The starting search position.

    Returns:
        Adjusted position at a sentence boundary.
    """
    search_end = min(position + 100, len(text))
    segment = text[position:search_end]

    for punct in [". ", "! ", "? ", "\n\n"]:
        idx = segment.find(punct)
        if idx != -1:
            return position + idx + len(punct)

    last_space = segment.rfind(" ")
    if last_space != -1:
        return position + last_space + 1

    return position
