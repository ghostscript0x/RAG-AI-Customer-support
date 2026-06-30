"""Groq API client wrapper with streaming support."""

import logging
import os
from typing import Optional

from groq import Groq

logger = logging.getLogger(__name__)


def get_groq_client() -> Optional[Groq]:
    """Initialize and return a Groq client, or None if the API key is missing or invalid."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your-groq-api-key-here":
        logger.warning("GROQ_API_KEY is not configured")
        return None
    try:
        return Groq(api_key=api_key)
    except Exception as exc:
        logger.exception("Failed to create Groq client")
        return None


def stream_response(client: Groq, messages: list, model: Optional[str] = None) -> str:
    """Send messages to Groq and return the streamed response text."""
    model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            stream=True,
        )
        return "".join(chunk.choices[0].delta.content or "" for chunk in stream)
    except Exception as exc:
        logger.exception("Groq API call failed")
        raise
