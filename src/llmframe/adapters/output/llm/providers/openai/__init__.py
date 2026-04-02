"""Public exports for the shared OpenAI client and helpers."""

from .client import build_client
from .dto import (
    OpenAIClientSettings,
    OpenAIResponseError,
    OpenAIResponseUsage,
)
from .parsing import (
    extract_message_content,
    extract_usage,
)
from .transport import (
    ChatCompletionJsonProtocol,
    ChatCompletionStructuredProtocol,
    ChatCompletionTextProtocol,
    LlmResponseStructuredProtocol,
    LlmResponseTextProtocol,
    OpenAIClient,
    OpenAIClientProtocol,
    OpenAILlmProtocol,
    OpenAIRequestConfigError,
    ReasoningEffort,
    ResponseJsonProtocol,
    ResponseStructuredProtocol,
    ResponseTextProtocol,
    build_structured_schema_definition,
)

__all__ = [
    "ChatCompletionJsonProtocol",
    "ChatCompletionStructuredProtocol",
    "ChatCompletionTextProtocol",
    "LlmResponseStructuredProtocol",
    "LlmResponseTextProtocol",
    "OpenAIClient",
    "OpenAIClientProtocol",
    "OpenAIClientSettings",
    "OpenAILlmProtocol",
    "OpenAIRequestConfigError",
    "OpenAIResponseError",
    "OpenAIResponseUsage",
    "ReasoningEffort",
    "ResponseJsonProtocol",
    "ResponseStructuredProtocol",
    "ResponseTextProtocol",
    "build_client",
    "build_structured_schema_definition",
    "extract_message_content",
    "extract_usage",
]
