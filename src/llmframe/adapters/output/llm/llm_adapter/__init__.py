"""Public exports for the shared LLM adapter."""

from .adapter import LlmAdapter
from .dto import (
    LlmBatchStructuredRequest,
    LlmBatchTextRequest,
    LlmTextCompletionResult,
    StructuredLlmJsonCompletionResult,
)
from .exceptions import (
    StructuredLlmBatchError,
    StructuredLlmError,
    StructuredLlmInvalidJsonError,
    StructuredLlmResponseError,
)

__all__ = [
    "LlmAdapter",
    "LlmBatchStructuredRequest",
    "LlmBatchTextRequest",
    "LlmTextCompletionResult",
    "StructuredLlmBatchError",
    "StructuredLlmError",
    "StructuredLlmInvalidJsonError",
    "StructuredLlmJsonCompletionResult",
    "StructuredLlmResponseError",
]
