"""DTOs returned by the shared LLM adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llmframe.application.ports import (
        LlmUsage,
    )
    from llmframe.shared.json_types import JsonValue


@dataclass(frozen=True)
class StructuredLlmJsonCompletionResult:
    """Structured JSON result plus token-usage metadata."""

    payload: dict[str, JsonValue]
    usage: LlmUsage | None


@dataclass(frozen=True)
class LlmTextCompletionResult:
    """Plain-text result plus token-usage metadata."""

    content: str
    usage: LlmUsage | None


@dataclass(frozen=True)
class LlmBatchTextRequest:
    """One high-level plain-text batch request item."""

    custom_id: str
    developer_prompt: str
    user_prompt: str
    temperature: float | None = None
    reasoning_effort: str | None = None


@dataclass(frozen=True)
class LlmBatchStructuredRequest:
    """One high-level structured-output batch request item."""

    custom_id: str
    developer_prompt: str
    user_prompt: str


__all__ = [
    "LlmBatchStructuredRequest",
    "LlmBatchTextRequest",
    "LlmTextCompletionResult",
    "StructuredLlmJsonCompletionResult",
]
