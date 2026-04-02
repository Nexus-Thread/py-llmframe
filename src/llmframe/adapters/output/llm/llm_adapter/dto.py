"""DTOs returned by the shared LLM adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llmframe.adapters.output.llm.providers.openai import OpenAIResponseUsage
if TYPE_CHECKING:
    from llmframe.shared.json_types import JsonValue


@dataclass(frozen=True)
class StructuredLlmJsonCompletionResult:
    """Structured JSON result plus token-usage metadata."""

    payload: dict[str, JsonValue]
    usage: OpenAIResponseUsage | None


@dataclass(frozen=True)
class LlmTextCompletionResult:
    """Plain-text result plus token-usage metadata."""

    content: str
    usage: OpenAIResponseUsage | None
