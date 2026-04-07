"""Tests for root package exports."""

import llmframe


def test_exports_top_level_openai_entrypoints() -> None:
    """Expose the ergonomic OpenAI-first entrypoints at package level."""
    assert llmframe.build_openai_llm_adapter is not None
    assert llmframe.OpenAIClientSettings is not None
