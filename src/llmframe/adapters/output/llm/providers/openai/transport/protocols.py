"""Capability and SDK-shape protocols for the OpenAI transport package."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence

    from llmframe.adapters.output.llm.providers.openai.dto import (
        OpenAIBatchFileUpload,
        OpenAIBatchRequestLine,
        OpenAIBatchResultLine,
    )

    from .payload_builders import JsonSchema, Message, ReasoningEffort


class ChatCompletionTextProtocol(Protocol):
    """Capability protocol for plain chat-completions calls."""

    def create_chat_completion(
        self,
        *,
        model: str,
        messages: list[Message],
        temperature: float | None = ...,
        reasoning_effort: ReasoningEffort | None = ...,
    ) -> object:
        """Create a plain chat completion without enforced response format."""


class ChatCompletionJsonProtocol(Protocol):
    """Capability protocol for chat-completions JSON mode calls."""

    def create_json_chat_completion(
        self,
        *,
        model: str,
        messages: list[Message],
        temperature: float | None = ...,
        reasoning_effort: ReasoningEffort | None = ...,
    ) -> object:
        """Create a chat completion response in JSON mode."""


class ChatCompletionStructuredProtocol(Protocol):
    """Capability protocol for chat-completions structured-output calls."""

    def create_structured_chat_completion(
        self,
        *,
        model: str,
        messages: list[Message],
        json_schema_name: str,
        schema: JsonSchema,
        temperature: float | None = ...,
        reasoning_effort: ReasoningEffort | None = ...,
    ) -> object:
        """Create a structured chat completion using JSON Schema mode."""


class ResponseTextProtocol(Protocol):
    """Capability protocol for plain Responses API calls."""

    def create_response(
        self,
        *,
        model: str,
        input_items: list[Message],
        temperature: float | None = ...,
        reasoning_effort: ReasoningEffort | None = ...,
    ) -> object:
        """Create a plain text response through the Responses API."""


class ResponseJsonProtocol(Protocol):
    """Capability protocol for Responses API JSON mode calls."""

    def create_json_response(
        self,
        *,
        model: str,
        input_items: list[Message],
        temperature: float | None = ...,
        reasoning_effort: ReasoningEffort | None = ...,
    ) -> object:
        """Create a JSON-formatted response through the Responses API."""


class ResponseStructuredProtocol(Protocol):
    """Capability protocol for Responses API structured-output calls."""

    def create_structured_response(
        self,
        *,
        model: str,
        input_items: list[Message],
        json_schema_name: str,
        schema: JsonSchema,
        temperature: float | None = ...,
        reasoning_effort: ReasoningEffort | None = ...,
    ) -> object:
        """Create a structured response through the Responses API."""


class ResponseBatchProtocol(Protocol):
    """Capability protocol for Responses Batch API calls."""

    def upload_batch_file(self, *, lines: Sequence[OpenAIBatchRequestLine]) -> OpenAIBatchFileUpload:
        """Upload one JSONL input file for batch processing."""
        ...

    def create_response_batch(self, *, input_file_id: str, metadata: dict[str, str] | None = ...) -> object:
        """Create a Responses batch from an uploaded input file."""
        ...

    def retrieve_batch(self, *, batch_id: str) -> object:
        """Retrieve one previously submitted batch."""
        ...

    def cancel_batch(self, *, batch_id: str) -> object:
        """Cancel one previously submitted batch."""
        ...

    def download_batch_output(self, *, file_id: str) -> str:
        """Download the content of one batch output file."""
        ...

    def parse_batch_output_jsonl(self, *, content: str) -> list[OpenAIBatchResultLine]:
        """Parse JSONL batch output content into normalized result lines."""
        ...


class LlmResponseTextProtocol(ResponseTextProtocol, Protocol):
    """Provider-neutral protocol for plain-text LLM responses."""


class LlmResponseStructuredProtocol(ResponseStructuredProtocol, ResponseTextProtocol, Protocol):
    """Provider-neutral protocol for structured and plain-text LLM responses."""


class OpenAILlmProtocol(
    ChatCompletionStructuredProtocol,
    LlmResponseStructuredProtocol,
    Protocol,
):
    """Capability protocol for transports that support structured and response text surfaces."""


class OpenAIClientProtocol(
    ChatCompletionTextProtocol,
    ChatCompletionJsonProtocol,
    ChatCompletionStructuredProtocol,
    ResponseTextProtocol,
    ResponseJsonProtocol,
    ResponseStructuredProtocol,
    ResponseBatchProtocol,
    Protocol,
):
    """Protocol for the shared OpenAI transport."""
