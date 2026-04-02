"""Provider-neutral protocols used by the shared LLM adapter."""

from __future__ import annotations

from typing import Protocol, TypeAlias

from pydantic import BaseModel

StructuredOutputSchema: TypeAlias = type[BaseModel]


class LlmStructuredOutputProtocol(Protocol):
    """Capability protocol for providers that support text and structured responses."""

    def create_response(
        self,
        *,
        model: str,
        input_items: list[dict[str, str]],
        temperature: float | None = ...,
        reasoning_effort: str | None = ...,
    ) -> object:
        """Create a plain-text response."""

    def create_structured_response(  # noqa: PLR0913
        self,
        *,
        model: str,
        input_items: list[dict[str, str]],
        json_schema_name: str,
        schema: dict[str, object],
        temperature: float | None = ...,
        reasoning_effort: str | None = ...,
    ) -> object:
        """Create a structured response."""


__all__ = [
    "LlmStructuredOutputProtocol",
    "StructuredOutputSchema",
]
