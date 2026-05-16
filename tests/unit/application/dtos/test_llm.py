"""Unit tests for LLM application DTOs."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from llmframe.application import LlmTextCompletionResult, LlmTextInputPart, LlmUsage


def test_llm_text_completion_result_is_immutable() -> None:
    """LLM result DTOs are immutable application boundary values."""
    result = LlmTextCompletionResult(content="hello", usage=LlmUsage(1, 2, 3))

    with pytest.raises(FrozenInstanceError):
        result.content = "changed"  # type: ignore[misc]


def test_llm_input_part_exports_value_equality() -> None:
    """Input DTOs use dataclass value equality."""
    assert LlmTextInputPart(text="hello") == LlmTextInputPart(text="hello")
