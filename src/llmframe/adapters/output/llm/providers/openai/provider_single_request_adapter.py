"""Single-request operations for the public OpenAI provider adapter façade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .provider_base import OpenAIProviderBase

if TYPE_CHECKING:
    from llmframe.application.ports.llm_provider import JsonSchema, LlmInputItem


class OpenAIProviderSingleRequestAdapter(OpenAIProviderBase):
    """Internal mixin for synchronous OpenAI provider operations."""

    def create_response(
        self,
        *,
        model: str,
        input_items: list[LlmInputItem],
        temperature: float | None = None,
        reasoning_effort: str | None = None,
    ) -> object:
        """Create a plain-text response via the OpenAI Responses API."""
        return self._transport.create_response(
            model=model,
            input_items=input_items,
            temperature=temperature,
            reasoning_effort=self._to_reasoning_effort(reasoning_effort),
        )

    def create_structured_response(  # noqa: PLR0913
        self,
        *,
        model: str,
        input_items: list[LlmInputItem],
        json_schema_name: str,
        schema: JsonSchema,
        temperature: float | None = None,
        reasoning_effort: str | None = None,
    ) -> object:
        """Create a structured response via the OpenAI Responses API."""
        return self._transport.create_structured_response(
            model=model,
            input_items=input_items,
            json_schema_name=json_schema_name,
            schema=self._to_transport_schema(schema),
            temperature=temperature,
            reasoning_effort=self._to_reasoning_effort(reasoning_effort),
        )
