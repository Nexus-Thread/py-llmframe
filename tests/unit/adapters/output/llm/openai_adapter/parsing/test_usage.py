"""Unit tests for shared OpenAI usage parsing helpers."""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from llmframe.adapters.output.llm.openai_adapter.dto import OpenAIResponseUsage
from llmframe.adapters.output.llm.openai_adapter.parsing import extract_usage


@dataclass(frozen=True)
class _Usage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True)
class _Response:
    usage: _Usage | None = None


def test_extract_usage_returns_none_when_usage_missing() -> None:
    """Response helper returns None when token usage is absent."""
    response = _Response(usage=None)

    assert extract_usage(response) is None


def test_extract_usage_returns_usage_dataclass() -> None:
    """Response helper maps usage fields into stable dataclass shape."""
    response = _Response(usage=_Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15))

    assert extract_usage(response) == OpenAIResponseUsage(
        input_tokens=10,
        output_tokens=5,
        total_tokens=15,
    )


def test_extract_usage_supports_responses_api_usage_fields() -> None:
    """Response helper maps Responses API usage fields into stable dataclass shape."""
    response = SimpleNamespace(
        usage=SimpleNamespace(
            input_tokens=12,
            output_tokens=8,
            total_tokens=20,
        )
    )

    assert extract_usage(response) == OpenAIResponseUsage(
        input_tokens=12,
        output_tokens=8,
        total_tokens=20,
    )


def test_extract_usage_ignores_non_integer_token_values() -> None:
    """Response helper ignores token counts that are not exposed as integers."""
    response = SimpleNamespace(
        usage=SimpleNamespace(
            prompt_tokens="12",
            completion_tokens=5.5,
            total_tokens=20,
        )
    )

    assert extract_usage(response) == OpenAIResponseUsage(
        input_tokens=None,
        output_tokens=None,
        total_tokens=20,
    )
