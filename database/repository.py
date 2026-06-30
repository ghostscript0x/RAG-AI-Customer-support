"""Repository layer — CRUD operations for documents and conversations."""

import logging
from datetime import datetime
from typing import List, Optional

from database.models import Document, Conversation, get_session

logger = logging.getLogger(__name__)


# ── Document CRUD ─────────────────────────────────────────────────────────────


def add_document(
    filename: str,
    source: str,
    doc_type: str,
    chunk_count: int = 0,
) -> Optional[Document]:
    """Add a document record to the database.

    Args:
        filename: The uploaded filename.
        source: The source path or identifier.
        doc_type: File type extension (e.g., 'pdf', 'csv').
        chunk_count: Number of chunks generated.

    Returns:
        The created Document, or None on failure.
    """
    session = get_session()
    try:
        doc = Document(
            filename=filename,
            source=source,
            doc_type=doc_type,
            chunk_count=chunk_count,
        )
        session.add(doc)
        session.commit()
        session.refresh(doc)
        logger.info("Added document record: %s", filename)
        return doc
    except Exception as exc:
        session.rollback()
        logger.exception("Failed to add document record: %s", filename)
        return None
    finally:
        session.close()


def list_documents() -> List[dict]:
    """List all document records, newest first.

    Returns:
        A list of document dicts.
    """
    session = get_session()
    try:
        docs = session.query(Document).order_by(Document.created_at.desc()).all()
        return [doc.to_dict() for doc in docs]
    except Exception as exc:
        logger.exception("Failed to list documents")
        return []
    finally:
        session.close()


def get_document(doc_id: int) -> Optional[dict]:
    """Get a single document by ID.

    Args:
        doc_id: The document ID.

    Returns:
        The document dict, or None if not found.
    """
    session = get_session()
    try:
        doc = session.query(Document).filter(Document.id == doc_id).first()
        return doc.to_dict() if doc else None
    except Exception as exc:
        logger.exception("Failed to get document %d", doc_id)
        return None
    finally:
        session.close()


def delete_document(doc_id: int) -> bool:
    """Delete a document record by ID.

    Args:
        doc_id: The document ID.

    Returns:
        True if deleted, False otherwise.
    """
    session = get_session()
    try:
        doc = session.query(Document).filter(Document.id == doc_id).first()
        if doc:
            session.delete(doc)
            session.commit()
            logger.info("Deleted document record: %d", doc_id)
            return True
        logger.warning("Document not found for deletion: %d", doc_id)
        return False
    except Exception as exc:
        session.rollback()
        logger.exception("Failed to delete document %d", doc_id)
        return False
    finally:
        session.close()


# ── Conversation CRUD ─────────────────────────────────────────────────────────


def add_conversation(
    session_id: str,
    question: str,
    answer: str,
    confidence: float = 0.0,
    sources: Optional[str] = None,
    response_time_ms: int = 0,
) -> Optional[Conversation]:
    """Record a conversation turn.

    Args:
        session_id: The chat session identifier.
        question: The user's question.
        answer: The assistant's response.
        confidence: The retrieval confidence score.
        sources: Comma-separated source document names.
        response_time_ms: Response time in milliseconds.

    Returns:
        The created Conversation, or None on failure.
    """
    session = get_session()
    try:
        conv = Conversation(
            session_id=session_id,
            question=question,
            answer=answer,
            confidence=confidence,
            sources=sources,
            response_time_ms=response_time_ms,
        )
        session.add(conv)
        session.commit()
        session.refresh(conv)
        return conv
    except Exception as exc:
        session.rollback()
        logger.exception("Failed to add conversation record")
        return None
    finally:
        session.close()


def get_conversation_stats() -> dict:
    """Get aggregate conversation statistics for analytics.

    Returns:
        A dict with total_conversations, avg_response_time, answered, unanswered.
    """
    session = get_session()
    try:
        total = session.query(Conversation).count()
        avg_time = session.query(Conversation.response_time_ms).all()
        avg = sum(t[0] for t in avg_time) / len(avg_time) if avg_time else 0

        high_conf = session.query(Conversation).filter(Conversation.confidence >= 0.65).count()
        low_conf = total - high_conf

        return {
            "total_conversations": total,
            "avg_response_time_ms": round(avg, 1),
            "answered": high_conf,
            "unanswered": low_conf,
        }
    except Exception as exc:
        logger.exception("Failed to get conversation stats")
        return {
            "total_conversations": 0,
            "avg_response_time_ms": 0,
            "answered": 0,
            "unanswered": 0,
        }
    finally:
        session.close()


def get_recent_conversations(limit: int = 50) -> List[dict]:
    """Get the most recent conversations.

    Args:
        limit: Max number of records to return.

    Returns:
        A list of conversation dicts, newest first.
    """
    session = get_session()
    try:
        convs = (
            session.query(Conversation)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .all()
        )
        return [c.to_dict() for c in convs]
    except Exception as exc:
        logger.exception("Failed to get recent conversations")
        return []
    finally:
        session.close()
