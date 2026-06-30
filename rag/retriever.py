"""Retrieval — query embedding + vector store search with confidence scoring."""

import logging
import os
from typing import List, Optional

import numpy as np

from rag.embedder import embed_text
from rag.vector_store import search

logger = logging.getLogger(__name__)


def retrieve(query: str, top_k: Optional[int] = None) -> List[dict]:
    """Retrieve relevant chunks for a query with similarity scores.

    Args:
        query: The user's question.
        top_k: Number of results to return. Defaults to TOP_K env var (5).

    Returns:
        A list of dicts with 'id', 'document', 'metadata', 'distance', and 'score'.
        Score is 1 - distance (higher is more similar).
    """
    top_k = top_k or int(os.getenv("TOP_K", "5"))

    embedding = embed_text(query)
    if embedding is None:
        logger.warning("Failed to generate embedding for query")
        return []

    embedding_list = embedding.tolist() if hasattr(embedding, "tolist") else list(embedding)
    results = search(embedding_list, top_k=top_k)
    for r in results:
        r["score"] = 1.0 - r.get("distance", 0.0)

    return results


def compute_confidence(results: List[dict]) -> float:
    """Compute an overall confidence score for the retrieval results.

    Uses the mean of the top-3 scores. Returns 0.0 if no results.

    Args:
        results: The retrieval results with 'score' keys.

    Returns:
        A confidence score between 0.0 and 1.0.
    """
    if not results:
        return 0.0

    scores = [r.get("score", 0.0) for r in results[:3]]
    return float(np.mean(scores))
