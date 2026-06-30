"""Tests for Phase 2: RAG Core — ingestion and RAG modules."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from rag.chunker import chunk_text
from rag.embedder import embed_text, embed_batch
from rag.retriever import retrieve, compute_confidence


# ─── Chunker Tests ────────────────────────────────────────────────────────────

class TestChunker:
    """Test suite for rag.chunker."""

    def test_chunk_text_empty(self) -> None:
        assert chunk_text("") == []

    def test_chunk_text_short(self) -> None:
        result = chunk_text("Hello world.", chunk_size=500, overlap=50)
        assert len(result) == 1
        assert "Hello world." in result[0]

    def test_chunk_text_splits_long_text(self) -> None:
        text = "Sentence one. " * 50
        result = chunk_text(text, chunk_size=200, overlap=20)
        assert len(result) > 1
        for chunk in result:
            assert len(chunk) <= 220

    def test_chunk_text_overlap_contains_shared_content(self) -> None:
        text = "Word " * 200
        result = chunk_text(text, chunk_size=300, overlap=50)
        if len(result) > 1:
            assert result[0][-30:] in result[1]

    def test_chunk_text_handles_newlines(self) -> None:
        text = "Para one.\n\nPara two.\n\nPara three."
        result = chunk_text(text, chunk_size=20, overlap=0)
        assert len(result) >= 2


# ─── Embedder Tests ───────────────────────────────────────────────────────────

class TestEmbedder:
    """Test suite for rag.embedder."""

    @patch("rag.embedder._get_model")
    def test_embed_text_returns_vector(self, mock_get_model: MagicMock) -> None:
        mock_model = MagicMock()
        mock_model.encode.return_value = [0.1, 0.2, 0.3]
        mock_get_model.return_value = mock_model

        result = embed_text("test")
        assert result is not None
        assert len(result) == 3

    @patch("rag.embedder._get_model")
    def test_embed_text_failure_returns_none(self, mock_get_model: MagicMock) -> None:
        mock_get_model.return_value = None
        assert embed_text("test") is None

    @patch("rag.embedder._get_model")
    def test_embed_batch_returns_vectors(self, mock_get_model: MagicMock) -> None:
        mock_model = MagicMock()
        mock_model.encode.return_value = [[0.1, 0.2], [0.3, 0.4]]
        mock_get_model.return_value = mock_model

        result = embed_batch(["a", "b"])
        assert result is not None
        assert len(result) == 2
        assert result[0][1] == 0.2

    @patch("rag.embedder._get_model")
    def test_embed_batch_empty_list(self, mock_get_model: MagicMock) -> None:
        mock_model = MagicMock()
        mock_model.encode.return_value = []
        mock_get_model.return_value = mock_model

        result = embed_batch([])
        assert result is not None
        assert len(result) == 0


# ─── Retriever Tests ──────────────────────────────────────────────────────────

class TestRetriever:
    """Test suite for rag.retriever."""

    @patch("rag.retriever.embed_text")
    @patch("rag.retriever.search")
    def test_retrieve_returns_results(
        self, mock_search: MagicMock, mock_embed: MagicMock
    ) -> None:
        mock_embed.return_value = [0.1, 0.2, 0.3]
        mock_search.return_value = [
            {"id": "1", "document": "doc1", "metadata": {}, "distance": 0.1},
            {"id": "2", "document": "doc2", "metadata": {}, "distance": 0.2},
        ]

        results = retrieve("test query", top_k=2)
        assert len(results) == 2
        assert "score" in results[0]
        assert results[0]["score"] == pytest.approx(0.9)

    @patch("rag.retriever.embed_text")
    def test_retrieve_embedding_failure(self, mock_embed: MagicMock) -> None:
        mock_embed.return_value = None
        results = retrieve("test query")
        assert results == []

    def test_compute_confidence_empty(self) -> None:
        assert compute_confidence([]) == 0.0

    def test_compute_confidence_with_results(self) -> None:
        results = [
            {"score": 0.9},
            {"score": 0.8},
            {"score": 0.7},
        ]
        assert compute_confidence(results) == pytest.approx(0.8)

    def test_compute_confidence_handles_fewer_than_three(self) -> None:
        results = [{"score": 0.9}]
        assert compute_confidence(results) == pytest.approx(0.9)


# ─── Ingestion Loader Tests ───────────────────────────────────────────────────

class TestPDFLoader:
    """Test suite for ingestion.pdf_loader."""

    def test_load_pdf_file_not_found(self) -> None:
        from ingestion.pdf_loader import load_pdf
        result = load_pdf("nonexistent.pdf")
        assert result is None


class TestDocxLoader:
    """Test suite for ingestion.docx_loader."""

    def test_load_docx_file_not_found(self) -> None:
        from ingestion.docx_loader import load_docx
        result = load_docx("nonexistent.docx")
        assert result is None


class TestCSVLoader:
    """Test suite for ingestion.csv_loader."""

    def test_load_csv_file_not_found(self) -> None:
        from ingestion.csv_loader import load_csv
        result = load_csv("nonexistent.csv")
        assert result is None

    def test_load_csv_parses_content(self) -> None:
        from ingestion.csv_loader import load_csv
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("name,age\nAlice,30\nBob,25\n")
            tmp_path = f.name
        try:
            result = load_csv(tmp_path)
            assert result is not None
            assert "name | age" in result
            assert "Alice | 30" in result
            assert "Bob | 25" in result
        finally:
            os.unlink(tmp_path)

    def test_load_csv_empty(self) -> None:
        from ingestion.csv_loader import load_csv
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("")
            tmp_path = f.name
        try:
            result = load_csv(tmp_path)
            assert result is None
        finally:
            os.unlink(tmp_path)


class TestWebsiteLoader:
    """Test suite for ingestion.website_loader."""

    @patch("ingestion.website_loader.requests.get")
    def test_load_website_success(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>Hello world</p></body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        from ingestion.website_loader import load_website
        result = load_website("https://example.com")
        assert result is not None
        assert "Hello world" in result

    @patch("ingestion.website_loader.requests.get")
    def test_load_website_network_error(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = Exception("Connection error")

        from ingestion.website_loader import load_website
        result = load_website("https://example.com")
        assert result is None

    @patch("ingestion.website_loader.requests.get")
    def test_load_website_strips_tags(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.text = (
            "<html><body><nav>Nav</nav><article>Content</article><footer>Footer</footer></body></html>"
        )
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        from ingestion.website_loader import load_website
        result = load_website("https://example.com")
        assert result is not None
        assert "Content" in result
        assert "Nav" not in result
        assert "Footer" not in result


# ─── Vector Store Tests ───────────────────────────────────────────────────────

class TestVectorStore:
    """Test suite for rag.vector_store."""

    @patch("rag.vector_store._get_client")
    def test_count_zero_when_no_client(self, mock_get_client: MagicMock) -> None:
        mock_get_client.return_value = None
        from rag.vector_store import count_documents
        assert count_documents() == 0

    @patch("rag.vector_store._get_client")
    def test_list_empty_when_no_client(self, mock_get_client: MagicMock) -> None:
        mock_get_client.return_value = None
        from rag.vector_store import list_documents
        assert list_documents() == []

    @patch("rag.vector_store._get_client")
    def test_search_returns_empty_when_no_client(self, mock_get_client: MagicMock) -> None:
        mock_get_client.return_value = None
        from rag.vector_store import search
        assert search([0.1, 0.2]) == []
