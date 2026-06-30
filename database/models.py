"""SQLAlchemy models for the RAG AI Chatbot database."""

import logging
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()

DB_PATH = "sqlite:///rag_ai.db"


class Document(Base):
    """Document metadata for ingested knowledge base files."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(500), nullable=False, index=True)
    source = Column(String(1000), nullable=False)
    doc_type = Column(String(50), nullable=False)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        """Serialize to a dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "source": self.source,
            "doc_type": self.doc_type,
            "chunk_count": self.chunk_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Conversation(Base):
    """Conversation record for analytics."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    confidence = Column(Float, default=0.0)
    sources = Column(Text, nullable=True)
    response_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        """Serialize to a dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "question": self.question,
            "answer": self.answer,
            "confidence": self.confidence,
            "sources": self.sources,
            "response_time_ms": self.response_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def init_db() -> None:
    """Initialize the database, creating tables if they don't exist."""
    try:
        engine = create_engine(DB_PATH, echo=False)
        Base.metadata.create_all(engine)
        logger.info("Database initialized at %s", DB_PATH)
    except Exception as exc:
        logger.exception("Failed to initialize database")
        raise


def get_session():
    """Create a new SQLAlchemy session."""
    engine = create_engine(DB_PATH, echo=False)
    Session = sessionmaker(bind=engine)
    return Session()
