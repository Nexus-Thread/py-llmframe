"""Exception types for the shared LLM adapter."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StructuredLlmError(Exception):
    """Base exception for shared LLM adapter failures."""

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
