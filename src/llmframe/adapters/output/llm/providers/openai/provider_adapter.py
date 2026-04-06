"""Application-facing OpenAI provider adapter."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from llmframe.adapters.output.llm.llm_adapter.exceptions import StructuredLlmResponseError

from .parsing import extract_message_content, extract_usage

if TYPE_CHECKING:
    from llmframe.application.ports import LlmUsage
    from llmframe.application.ports.llm_provider import JsonSchema, LlmInputItem

    from .transport import OpenAIClient, ReasoningEffort


class OpenAIProviderAdapter:
    """Adapt the OpenAI transport to the application-level provider contract."""

    def __init__(self, *, transport: OpenAIClient) -> None:
        """Store the lower-level OpenAI transport."""
        self._transport = transport

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
            reasoning_effort=cast("ReasoningEffort | None", reasoning_effort),
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
            schema=cast("dict[str, object]", schema),
            temperature=temperature,
            reasoning_effort=cast("ReasoningEffort | None", reasoning_effort),
        )

    def extract_text(self, response: object) -> str:
        """Extract text content from an OpenAI response object."""
        try:
            return extract_message_content(response)
        except ValueError as err:
            msg = "LLM response is missing content or has an invalid shape"
            raise StructuredLlmResponseError(msg, suggestion=str(err)) from err

    def extract_usage(self, response: object) -> LlmUsage | None:
        """Extract normalized usage metadata from an OpenAI response object."""
        return extract_usage(response)
