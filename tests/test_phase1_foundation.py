"""Tests for Phase 1: Foundation — prompts, Groq client, sidebar."""

import os
from unittest.mock import MagicMock, patch

import pytest

from chatbot.groq_client import get_groq_client, stream_response
from chatbot.prompts import build_prompt, SYSTEM_PROMPT


class TestPrompts:
    """Test suite for chatbot.prompts."""

    def test_system_prompt_has_required_sections(self) -> None:
        """System prompt must contain grounding, citation, and hallucination rules."""
        assert "GROUND YOUR ANSWERS IN THE PROVIDED CONTEXT" in SYSTEM_PROMPT
        assert "NEVER HALLUCINATE" in SYSTEM_PROMPT
        assert "ALWAYS CITE SOURCES" in SYSTEM_PROMPT
        assert "{context}" in SYSTEM_PROMPT
        assert "{history}" in SYSTEM_PROMPT
        assert "{question}" in SYSTEM_PROMPT

    def test_build_prompt_with_context(self) -> None:
        """build_prompt should insert context, history, and question."""
        result = build_prompt(
            question="What is the return policy?",
            context="Return policy: 30-day return window.",
            history=[{"role": "user", "content": "Hi"}],
        )
        assert "What is the return policy?" in result
        assert "Return policy: 30-day return window." in result
        assert "User: Hi" in result

    def test_build_prompt_no_context(self) -> None:
        """build_prompt should show fallback text when context is empty."""
        result = build_prompt(
            question="Test question",
            context="",
            history=[],
        )
        assert "No knowledge base context" in result

    def test_build_prompt_respects_history_limit(self) -> None:
        """Only the last 6 history messages should be included."""
        history = [{"role": "user", "content": f"msg{i}"} for i in range(10)]
        result = build_prompt(
            question="Q",
            context="Ctx",
            history=history,
        )
        for i in range(4):
            assert f"msg{i}" not in result
        for i in range(4, 10):
            assert f"msg{i}" in result


class TestGroqClient:
    """Test suite for chatbot.groq_client."""

    @patch.dict(os.environ, {"GROQ_API_KEY": ""}, clear=True)
    def test_missing_api_key_returns_none(self) -> None:
        """get_groq_client should return None when API key is missing."""
        assert get_groq_client() is None

    @patch.dict(os.environ, {"GROQ_API_KEY": "your-groq-api-key-here"}, clear=True)
    def test_placeholder_api_key_returns_none(self) -> None:
        """get_groq_client should return None when API key is the placeholder."""
        assert get_groq_client() is None

    @patch.dict(os.environ, {"GROQ_API_KEY": "gsk_test123"}, clear=True)
    @patch("chatbot.groq_client.Groq")
    def test_valid_api_key_creates_client(self, mock_groq: MagicMock) -> None:
        """get_groq_client should create a Groq client with the API key."""
        mock_groq.return_value = MagicMock()
        client = get_groq_client()
        assert client is not None
        mock_groq.assert_called_once_with(api_key="gsk_test123")

    @patch.dict(os.environ, {"GROQ_API_KEY": "gsk_test123", "GROQ_MODEL": "llama-3.3-70b-versatile"}, clear=True)
    def test_stream_response_returns_text(self) -> None:
        """stream_response should concatenate chunks from the stream."""
        mock_client = MagicMock()
        mock_chunk_1 = MagicMock()
        mock_chunk_1.choices[0].delta.content = "Hello"
        mock_chunk_2 = MagicMock()
        mock_chunk_2.choices[0].delta.content = " World"
        mock_client.chat.completions.create.return_value = [mock_chunk_1, mock_chunk_2]

        result = stream_response(mock_client, [{"role": "user", "content": "Hi"}])
        assert result == "Hello World"
        mock_client.chat.completions.create.assert_called_once()

    @patch.dict(os.environ, {"GROQ_API_KEY": "gsk_test123"}, clear=True)
    def test_stream_response_handles_empty_chunks(self) -> None:
        """stream_response should handle None content in chunks."""
        mock_client = MagicMock()
        mock_chunk = MagicMock()
        mock_chunk.choices[0].delta.content = None
        mock_client.chat.completions.create.return_value = [mock_chunk]

        result = stream_response(mock_client, [{"role": "user", "content": "Hi"}])
        assert result == ""

    @patch.dict(os.environ, {"GROQ_API_KEY": "gsk_test123"}, clear=True)
    def test_stream_response_raises_on_api_error(self) -> None:
        """stream_response should raise when Groq API fails."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            stream_response(mock_client, [{"role": "user", "content": "Hi"}])


class TestSidebar:
    """Test suite for sidebar."""

    def test_render_sidebar_is_callable(self) -> None:
        """render_sidebar should be a callable function."""
        from chatbot.sidebar import render_sidebar

        assert callable(render_sidebar)
