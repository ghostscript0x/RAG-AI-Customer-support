"""RAG pipeline — orchestrates ingestion, chunking, embedding, and retrieval."""

import logging
from pathlib import Path
from typing import List, Optional, Tuple

from rag.chunker import chunk_text
from rag.embedder import embed_batch
from rag.vector_store import add_documents, search

from ingestion.pdf_loader import load_pdf
from ingestion.docx_loader import load_docx
from ingestion.csv_loader import load_csv
from ingestion.website_loader import load_website

logger = logging.getLogger(__name__)


def ingest_file(file_path: str, original_filename: Optional[str] = None) -> Tuple[bool, int, str]:
    """Ingest a file: load, chunk, embed, and store in the vector DB.

    Args:
        file_path: Path to the file to ingest.
        original_filename: Original uploaded filename (for metadata display).
                           Falls back to file_path basename if not provided.

    Returns:
        A tuple of (success: bool, chunk_count: int, message: str).
    """
    path = Path(file_path)
    suffix = path.suffix.lower()
    display_name = original_filename or path.name

    loaders = {
        ".pdf": load_pdf,
        ".docx": load_docx,
        ".csv": load_csv,
    }

    loader = loaders.get(suffix)
    if loader is None:
        return False, 0, f"Unsupported file type: {suffix}"

    text = loader(file_path)
    if text is None:
        return False, 0, f"Failed to extract text from {display_name}"

    chunks = chunk_text(text)
    if not chunks:
        return False, 0, f"No chunks generated from {display_name}"

    metadatas = [{"source": display_name, "type": suffix[1:]} for _ in chunks]

    embeddings = embed_batch(chunks)
    if embeddings is None:
        return False, 0, f"Failed to generate embeddings for {display_name}"

    embedding_vectors = [emb.tolist() if hasattr(emb, "tolist") else list(emb) for emb in embeddings]

    import uuid
    ids = [str(uuid.uuid4()) for _ in chunks]

    success = add_documents(chunks, metadatas=metadatas, ids=ids, embeddings=embedding_vectors)
    if not success:
        return False, 0, f"Failed to store chunks in vector DB for {display_name}"

    return True, len(chunks), f"Successfully ingested {display_name} ({len(chunks)} chunks)"


def ingest_website(url: str) -> Tuple[bool, int, str]:
    """Ingest a website: load, chunk, embed, and store in the vector DB.

    Args:
        url: The website URL to ingest.

    Returns:
        A tuple of (success: bool, chunk_count: int, message: str).
    """
    text = load_website(url)
    if text is None:
        return False, 0, f"Failed to extract text from {url}"

    chunks = chunk_text(text)
    if not chunks:
        return False, 0, f"No chunks generated from {url}"

    metadatas = [{"source": url, "type": "website"} for _ in chunks]

    embeddings = embed_batch(chunks)
    if embeddings is None:
        return False, 0, f"Failed to generate embeddings for {url}"

    embedding_vectors = [emb.tolist() if hasattr(emb, "tolist") else list(emb) for emb in embeddings]

    import uuid
    ids = [str(uuid.uuid4()) for _ in chunks]

    success = add_documents(chunks, metadatas=metadatas, ids=ids, embeddings=embedding_vectors)
    if not success:
        return False, 0, f"Failed to store chunks in vector DB for {url}"

    return True, len(chunks), f"Successfully ingested {url} ({len(chunks)} chunks)"
