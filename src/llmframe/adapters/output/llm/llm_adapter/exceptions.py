"""Compatibility re-exports for LLM application exceptions."""

from __future__ import annotations

from llmframe.application.exceptions import (
    StructuredLlmBatchError,
    StructuredLlmError,
    StructuredLlmInvalidJsonError,
    StructuredLlmResponseError,
)

__all__ = [
    "StructuredLlmBatchError",
    "StructuredLlmError",
    "StructuredLlmInvalidJsonError",
    "StructuredLlmResponseError",
]
