"""Application exceptions for provider-neutral LLM use cases."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StructuredLlmError(Exception):
    """Base exception for structured LLM application failures."""

    message: str
    suggestion: str | None = None

    def __str__(self) -> str:
        """Return the user-facing error message."""
        return self.message


class StructuredLlmResponseError(StructuredLlmError):
    """Raised when an LLM response is missing required content."""


class StructuredLlmInvalidJsonError(StructuredLlmError):
    """Raised when the LLM response cannot be parsed as a JSON object."""


class StructuredLlmBatchError(StructuredLlmError):
    """Raised when an asynchronous batch request cannot be processed safely."""


__all__ = [
    "StructuredLlmBatchError",
    "StructuredLlmError",
    "StructuredLlmInvalidJsonError",
    "StructuredLlmResponseError",
]
