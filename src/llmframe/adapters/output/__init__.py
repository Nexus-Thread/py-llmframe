"""Public output-adapter namespaces and ergonomic re-exports."""

from . import llm, persistence
from .llm import (
    LlmAdapter,
    LlmTextCompletionResult,
    LlmUsageSummary,
    LlmUsageTracker,
    LlmUsageTrackerConfig,
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
    "LlmTextCompletionResult",
    "LlmUsageSummary",
    "LlmUsageTracker",
    "LlmUsageTrackerConfig",
    "StructuredLlmError",
    "StructuredLlmInvalidJsonError",
    "StructuredLlmJsonCompletionResult",
    "StructuredLlmResponseError",
    "build_openai_llm_adapter",
    "llm",
    "persistence",
]
