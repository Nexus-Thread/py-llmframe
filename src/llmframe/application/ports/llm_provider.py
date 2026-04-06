"""Application port for provider-backed LLM response generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeAlias

from pydantic import BaseModel

from llmframe.shared.json_types import JsonValue

StructuredOutputSchema: TypeAlias = type[BaseModel]
LlmInputItem: TypeAlias = dict[str, str]
JsonSchema: TypeAlias = dict[str, JsonValue]


@dataclass(frozen=True, slots=True)
class LlmUsage:
    """Normalized token usage metadata returned by any LLM provider.

    Attributes:
        input_tokens: Prompt or input token count when the provider exposes it.
        output_tokens: Completion or output token count when the provider exposes it.
        total_tokens: Total token count when the provider exposes it.
    """

    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None


class LlmProviderPort(Protocol):
    """Output port for providers that support text and structured responses.

    Implementations hide provider-specific transport details behind a small,
    provider-neutral contract used by the shared LLM adapter.
    """

    def create_response(
        self,
        *,
        model: str,
        input_items: list[LlmInputItem],
        temperature: float | None = ...,
        reasoning_effort: str | None = ...,
    ) -> object:
        """Create a plain-text response for the supplied input items."""
        ...

    def create_structured_response(  # noqa: PLR0913
        self,
        *,
        model: str,
        input_items: list[LlmInputItem],
        json_schema_name: str,
        schema: JsonSchema,
        temperature: float | None = ...,
        reasoning_effort: str | None = ...,
    ) -> object:
        """Create a structured response constrained by the provided JSON Schema."""
        ...

    def extract_text(self, response: object) -> str:
        """Extract plain-text content from a provider-native response object."""
        ...

    def extract_usage(self, response: object) -> LlmUsage | None:
        """Extract normalized usage metadata from a provider-native response object."""
        ...


__all__ = ["JsonSchema", "LlmInputItem", "LlmProviderPort", "LlmUsage", "StructuredOutputSchema"]
