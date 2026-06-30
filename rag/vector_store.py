"""ChromaDB vector store operations."""

import logging
import os
from typing import List, Optional

import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

CHROMA_COLLECTION = "knowledge_base"
_CHROMA_CLIENT_CACHE: dict = {}


def _get_client() -> Optional[chromadb.Client]:
    """Get or create the ChromaDB client (cached).

    Returns:
        The ChromaDB client, or None if initialization failed.
    """
    cache_key = "client"
    if cache_key not in _CHROMA_CLIENT_CACHE:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        try:
            client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(anonymized_telemetry=False),
            )
            _CHROMA_CLIENT_CACHE[cache_key] = client
        except Exception as exc:
            logger.exception("Failed to initialize ChromaDB client")
            return None
    return _CHROMA_CLIENT_CACHE[cache_key]


def _get_collection(client: chromadb.Client) -> Optional[chromadb.Collection]:
    """Get or create the knowledge base collection.

    Args:
        client: The ChromaDB client.

    Returns:
        The collection, or None if it could not be created.
    """
    try:
        return client.get_or_create_collection(name=CHROMA_COLLECTION)
    except Exception as exc:
        logger.exception("Failed to get or create ChromaDB collection")
        return None


def add_documents(
    chunks: List[str],
    metadatas: Optional[List[dict]] = None,
    ids: Optional[List[str]] = None,
    embeddings: Optional[List[List[float]]] = None,
) -> bool:
    """Add document chunks to the vector store.

    Args:
        chunks: List of text chunks.
        metadatas: Optional list of metadata dicts per chunk.
        ids: Optional list of IDs. Auto-generated if not provided.
        embeddings: Optional pre-computed embedding vectors. ChromaDB will
                    auto-embed documents if not provided.

    Returns:
        True if successful, False otherwise.
    """
    client = _get_client()
    if client is None:
        return False

    collection = _get_collection(client)
    if collection is None:
        return False

    if ids is None:
        import uuid
        ids = [str(uuid.uuid4()) for _ in chunks]

    try:
        kwargs = {
            "documents": chunks,
            "metadatas": metadatas or [{}] * len(chunks),
            "ids": ids,
        }
        if embeddings is not None:
            kwargs["embeddings"] = embeddings
        collection.add(**kwargs)
        logger.info("Added %d chunks to vector store", len(chunks))
        return True
    except Exception as exc:
        logger.exception("Failed to add documents to vector store")
        return False


def search(query_embedding: List[float], top_k: int = 5) -> List[dict]:
    """Search the vector store for similar chunks.

    Args:
        query_embedding: The query embedding vector.
        top_k: Number of results to return.

    Returns:
        A list of dicts with 'id', 'document', 'metadata', and 'distance' keys.
    """
    client = _get_client()
    if client is None:
        return []

    collection = _get_collection(client)
    if collection is None:
        return []

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if results.get("distances") else 0.0,
            })
        return output
    except Exception as exc:
        logger.exception("Failed to search vector store")
        return []


def delete_documents(document_ids: List[str]) -> bool:
    """Delete documents from the vector store by ID.

    Args:
        document_ids: List of document IDs to delete.

    Returns:
        True if successful, False otherwise.
    """
    client = _get_client()
    if client is None:
        return False

    collection = _get_collection(client)
    if collection is None:
        return False

    try:
        collection.delete(ids=document_ids)
        logger.info("Deleted %d documents from vector store", len(document_ids))
        return True
    except Exception as exc:
        logger.exception("Failed to delete documents from vector store")
        return False


def list_documents() -> List[dict]:
    """List all documents in the vector store with their metadata.

    Returns:
        A list of dicts with chunk information.
    """
    client = _get_client()
    if client is None:
        return []

    collection = _get_collection(client)
    if collection is None:
        return []

    try:
        results = collection.get()
        output = []
        for i in range(len(results["ids"])):
            output.append({
                "id": results["ids"][i],
                "document": results["documents"][i],
                "metadata": results["metadatas"][i],
            })
        return output
    except Exception as exc:
        logger.exception("Failed to list documents from vector store")
        return []


def count_documents() -> int:
    """Count the number of chunks in the vector store.

    Returns:
        The number of chunks.
    """
    client = _get_client()
    if client is None:
        return 0

    collection = _get_collection(client)
    if collection is None:
        return 0

    try:
        return collection.count()
    except Exception as exc:
        logger.exception("Failed to count documents")
        return 0
