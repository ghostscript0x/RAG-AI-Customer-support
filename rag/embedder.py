"""Embedding generation using sentence-transformers with BAAI/bge-base-en-v1.5."""

import logging
import os
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_EMBEDDER_CACHE: dict = {}


def _get_model() -> Optional[SentenceTransformer]:
    """Get or load the sentence-transformers model (cached).

    Returns:
        The SentenceTransformer model, or None if loading failed.
    """
    model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
    if model_name not in _EMBEDDER_CACHE:
        try:
            logger.info("Loading embedding model: %s", model_name)
            _EMBEDDER_CACHE[model_name] = SentenceTransformer(model_name)
        except Exception as exc:
            logger.exception("Failed to load embedding model %s", model_name)
            return None
    return _EMBEDDER_CACHE[model_name]


def embed_text(text: str) -> Optional[np.ndarray]:
    """Generate an embedding vector for a single text string.

    Args:
        text: The text to embed.

    Returns:
        A numpy array of embedding values, or None if embedding failed.
    """
    model = _get_model()
    if model is None:
        return None
    try:
        return model.encode(text, normalize_embeddings=True)
    except Exception as exc:
        logger.exception("Failed to embed text")
        return None


def embed_batch(texts: List[str], batch_size: int = 32) -> Optional[List[np.ndarray]]:
    """Generate embedding vectors for a batch of texts.

    Args:
        texts: List of texts to embed.
        batch_size: Number of texts to process per batch.

    Returns:
        A list of numpy arrays, or None if embedding failed.
    """
    model = _get_model()
    if model is None:
        return None
    try:
        embeddings = model.encode(texts, batch_size=batch_size, normalize_embeddings=True)
        return [embeddings[i] for i in range(len(texts))]
    except Exception as exc:
        logger.exception("Failed to embed batch")
        return None
