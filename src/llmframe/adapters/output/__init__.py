"""Public output-adapter namespaces and ergonomic re-exports."""

from . import llm, persistence
from .llm import (
    LlmAdapter,
    LlmBatchStructuredRequest,
    LlmBatchTextRequest,
    LlmImageFileInputPart,
    LlmImageUrlInputPart,
    LlmTextCompletionResult,
    LlmTextInputPart,
    LlmUsageSummary,
    LlmUsageTracker,
    LlmUsageTrackerConfig,
    StructuredLlmBatchError,
    StructuredLlmError,
    StructuredLlmInvalidJsonError,
    StructuredLlmJsonCompletionResult,
    StructuredLlmResponseError,
    build_openai_llm_adapter,
)
from .persistence import JsonFileBatchRequestStoreAdapter, JsonFileWriterAdapter

__all__ = [
    "JsonFileBatchRequestStoreAdapter",
    "JsonFileWriterAdapter",
    "LlmAdapter",
    "LlmBatchStructuredRequest",
    "LlmBatchTextRequest",
    "LlmImageFileInputPart",
    "LlmImageUrlInputPart",
    "LlmTextCompletionResult",
    "LlmTextInputPart",
    "LlmUsageSummary",
    "LlmUsageTracker",
    "LlmUsageTrackerConfig",
    "StructuredLlmBatchError",
    "StructuredLlmError",
    "StructuredLlmInvalidJsonError",
    "StructuredLlmJsonCompletionResult",
    "StructuredLlmResponseError",
    "build_openai_llm_adapter",
    "llm",
    "persistence",
]
