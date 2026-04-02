"""Public exports for the shared LLM adapter."""

from .adapter import LlmAdapter
from .dto import LlmTextCompletionResult, StructuredLlmJsonCompletionResult
from .exceptions import (
    StructuredLlmError,
    StructuredLlmInvalidJsonError,
    StructuredLlmResponseError,
)

__all__ = [
    "LlmAdapter",
    "LlmTextCompletionResult",
    "StructuredLlmError",
    "StructuredLlmInvalidJsonError",
    "StructuredLlmJsonCompletionResult",
    "StructuredLlmResponseError",
]
