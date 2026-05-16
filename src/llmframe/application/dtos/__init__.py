"""Application-owned DTOs for use-case boundaries."""

from .llm import (
    LlmBatchStructuredRequest,
    LlmBatchTextRequest,
    LlmFileInputPart,
    LlmImageFileInputPart,
    LlmImageUrlInputPart,
    LlmTextCompletionResult,
    LlmTextInputPart,
    StructuredLlmJsonCompletionResult,
)

__all__ = [
    "LlmBatchStructuredRequest",
    "LlmBatchTextRequest",
    "LlmFileInputPart",
    "LlmImageFileInputPart",
    "LlmImageUrlInputPart",
    "LlmTextCompletionResult",
    "LlmTextInputPart",
    "StructuredLlmJsonCompletionResult",
]
