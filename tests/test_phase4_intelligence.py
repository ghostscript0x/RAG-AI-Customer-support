"""Tests for Phase 4: Intelligence — memory, prompts, response builder."""

import os
from unittest.mock import MagicMock, patch

import pytest

from chatbot.memory import resolve_pronouns, get_recent_history, _extract_noun_phrases
from chatbot.prompts import build_prompt, SYSTEM_PROMPT
from chatbot.response_builder import (
    build_sources_section,
    parse_sources_from_response,
    assemble_response,
)


class TestMemory:
    """Test suite for chatbot.memory."""

    def test_resolve_pronouns_no_pronouns(self) -> None:
        question = "What is the return policy?"
        history = [{"role": "assistant", "content": "The return policy is 30 days."}]
        result = resolve_pronouns(question, history)
        assert result == question

    def test_resolve_pronouns_with_it(self) -> None:
        question = "How long does it take to process?"
        history = [{"role": "assistant", "content": "Premium subscriptions include priority support."}]
        result = resolve_pronouns(question, history)
        assert "Premium" in result or result != question

    def test_resolve_pronouns_no_history(self) -> None:
        question = "How does it work?"
        result = resolve_pronouns(question, [])
        assert result == question

    def test_extract_noun_phrases_capitalized(self) -> None:
        text = "The Premium Subscription includes 24/7 support."
        result = _extract_noun_phrases(text)
        assert any("Premium" in p for p in result)

    def test_extract_noun_phrases_empty(self) -> None:
        assert _extract_noun_phrases("hello world") == []

    def test_get_recent_history_returns_all_if_under_limit(self) -> None:
        history = [{"role": "user", "content": "hi"}] * 3
        result = get_recent_history(history, limit=6)
        assert len(result) == 3

    def test_get_recent_history_truncates(self) -> None:
        history = [{"role": "user", "content": f"msg{i}"} for i in range(10)]
        result = get_recent_history(history, limit=6)
        assert len(result) == 6
        assert result[0]["content"] == "msg4"


class TestPrompts:
    """Test suite for chatbot.prompts."""

    def test_system_prompt_has_grounding_rule(self) -> None:
        assert "GROUND YOUR ANSWERS IN THE PROVIDED CONTEXT" in SYSTEM_PROMPT

    def test_system_prompt_has_citation_rule(self) -> None:
        assert "ALWAYS CITE SOURCES" in SYSTEM_PROMPT

    def test_system_prompt_has_anti_hallucination_rule(self) -> None:
        assert "NEVER HALLUCINATE" in SYSTEM_PROMPT

    def test_system_prompt_has_conversational_quality_rules(self) -> None:
        assert "ACKNOWLEDGE FRUSTRATION" in SYSTEM_PROMPT
        assert "NO FALSE ACTIONS" in SYSTEM_PROMPT
        assert "BE DIRECT AND CONVERSATIONAL" in SYSTEM_PROMPT
        assert "Never start with a generic greeting" in SYSTEM_PROMPT
        assert "NO PADDING" in SYSTEM_PROMPT

    def test_build_prompt_includes_all_sections(self) -> None:
        result = build_prompt(
            question="What is the price?",
            context="Price is $10.",
            history=[{"role": "user", "content": "Hello"}],
        )
        assert "What is the price?" in result
        assert "Price is $10." in result
        assert "Hello" in result

    def test_build_prompt_empty_context(self) -> None:
        result = build_prompt("Q", "", [])
        assert "No knowledge base context" in result

    def test_build_prompt_empty_history(self) -> None:
        result = build_prompt("Q", "Ctx", [])
        assert "No prior conversation history" in result


class TestResponseBuilder:
    """Test suite for chatbot.response_builder."""

    def test_build_sources_section_empty(self) -> None:
        assert build_sources_section([]) == ""

    def test_build_sources_section_deduplicates(self) -> None:
        result = build_sources_section(["doc1", "doc1", "doc2"])
        assert "doc1" in result
        assert "doc2" in result
        assert result.count("doc1") == 1

    def test_build_sources_section_limits_to_five(self) -> None:
        sources = [f"doc{i}" for i in range(10)]
        result = build_sources_section(sources)
        assert result.count("- doc") == 5

    def test_parse_sources_from_response(self) -> None:
        text = "The policy is 30 days (Source: Policy PDF). Call for details (Source: FAQ)."
        result = parse_sources_from_response(text)
        assert "Policy PDF" in result
        assert "FAQ" in result

    def test_parse_sources_from_response_no_sources(self) -> None:
        assert parse_sources_from_response("Just a normal answer.") == []

    @patch.dict(os.environ, {"CONFIDENCE_THRESHOLD": "0.65"}, clear=True)
    def test_assemble_response_low_confidence_no_sources(self) -> None:
        result = assemble_response("Answer text", [], 0.3)
        assert "don't have enough information" in result
        assert "support team" in result

    @patch.dict(os.environ, {"CONFIDENCE_THRESHOLD": "0.65"}, clear=True)
    def test_assemble_response_high_confidence(self) -> None:
        result = assemble_response("Answer text.", ["doc1"], 0.9)
        assert "Answer text." in result
        assert "Source" in result
        assert "doc1" in result

    @patch.dict(os.environ, {"CONFIDENCE_THRESHOLD": "0.65"}, clear=True)
    def test_assemble_response_low_confidence_with_sources(self) -> None:
        result = assemble_response("Partial answer.", ["doc1"], 0.5)
        assert "Partial answer." in result
        assert "doc1" in result
