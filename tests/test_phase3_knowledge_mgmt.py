"""Tests for Phase 3: Knowledge Management — database models and repository."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from database.models import Document, Conversation


class TestModels:
    """Test suite for database.models."""

    def test_document_to_dict(self) -> None:
        doc = Document(
            id=1,
            filename="test.pdf",
            source="test.pdf",
            doc_type="pdf",
            chunk_count=10,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )
        d = doc.to_dict()
        assert d["id"] == 1
        assert d["filename"] == "test.pdf"
        assert d["doc_type"] == "pdf"
        assert d["chunk_count"] == 10

    def test_document_to_dict_handles_none_dates(self) -> None:
        doc = Document(id=2, filename="a.pdf", source="a.pdf", doc_type="pdf")
        d = doc.to_dict()
        assert d["created_at"] is None
        assert d["updated_at"] is None

    def test_conversation_to_dict(self) -> None:
        conv = Conversation(
            id=1,
            session_id="sess1",
            question="Hi",
            answer="Hello",
            confidence=0.9,
            sources="doc1, doc2",
            response_time_ms=150,
            created_at=datetime(2026, 1, 1),
        )
        d = conv.to_dict()
        assert d["question"] == "Hi"
        assert d["confidence"] == 0.9
        assert d["response_time_ms"] == 150


class TestRepository:
    """Test suite for database.repository."""

    @patch("database.repository.get_session")
    def test_list_documents_empty(self, mock_get_session: MagicMock) -> None:
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.order_by.return_value.all.return_value = []
        mock_session.query.return_value = mock_query
        mock_get_session.return_value = mock_session

        from database.repository import list_documents
        assert list_documents() == []

    @patch("database.repository.get_session")
    def test_add_document_returns_none_on_error(self, mock_get_session: MagicMock) -> None:
        mock_session = MagicMock()
        mock_session.add.side_effect = Exception("DB error")
        mock_get_session.return_value = mock_session

        from database.repository import add_document
        result = add_document("test.pdf", "test.pdf", "pdf", 5)
        assert result is None
        mock_session.rollback.assert_called_once()

    @patch("database.repository.get_session")
    def test_delete_document_not_found(self, mock_get_session: MagicMock) -> None:
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_session.return_value = mock_session

        from database.repository import delete_document
        assert delete_document(999) is False

    @patch("database.repository.get_session")
    def test_get_conversation_stats_empty(self, mock_get_session: MagicMock) -> None:
        mock_session = MagicMock()
        mock_session.query.return_value.count.return_value = 0
        mock_session.query.return_value.all.return_value = []
        mock_get_session.return_value = mock_session

        from database.repository import get_conversation_stats
        stats = get_conversation_stats()
        assert stats["total_conversations"] == 0
        assert stats["avg_response_time_ms"] == 0
