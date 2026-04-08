"""Public output-adapter namespaces and ergonomic re-exports."""

from . import llm, persistence
from .llm import (
    LlmAdapter,
    LlmBatchStructuredRequest,
    LlmBatchTextRequest,
    LlmTextCompletionResult,
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
from .persistence import JsonFileWriterAdapter

__all__ = [
    "JsonFileWriterAdapter",
    "LlmAdapter",
    "LlmBatchStructuredRequest",
    "LlmBatchTextRequest",
    "LlmTextCompletionResult",
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
