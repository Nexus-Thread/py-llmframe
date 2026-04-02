"""Compatibility shim for the legacy OpenAI protocols module path."""

from llmframe.adapters.output.llm.providers.openai.transport.protocols import (
    ChatCompletionJsonProtocol,
    ChatCompletionStructuredProtocol,
    ChatCompletionTextProtocol,
    LlmResponseStructuredProtocol,
    LlmResponseTextProtocol,
    OpenAIClientProtocol,
    OpenAILlmProtocol,
    ResponseJsonProtocol,
    ResponseStructuredProtocol,
    ResponseTextProtocol,
)

__all__ = [
    "ChatCompletionJsonProtocol",
    "ChatCompletionStructuredProtocol",
    "ChatCompletionTextProtocol",
    "LlmResponseStructuredProtocol",
    "LlmResponseTextProtocol",
    "OpenAIClientProtocol",
    "OpenAILlmProtocol",
    "ResponseJsonProtocol",
    "ResponseStructuredProtocol",
    "ResponseTextProtocol",
]
