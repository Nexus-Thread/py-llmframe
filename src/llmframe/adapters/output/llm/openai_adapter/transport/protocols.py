"""Capability and SDK-shape protocols for the OpenAI transport package."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
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


class OpenAILlmProtocol(
    ChatCompletionStructuredProtocol,
    ResponseStructuredProtocol,
    ResponseTextProtocol,
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
    Protocol,
):
    """Protocol for the shared OpenAI transport."""
