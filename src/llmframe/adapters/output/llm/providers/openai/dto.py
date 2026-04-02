"""Public DTOs and exceptions for shared OpenAI response handling."""

from __future__ import annotations

from dataclasses import dataclass

from .transport import DEFAULT_BACKOFF_FACTOR, DEFAULT_MAX_RETRIES


class OpenAIResponseError(ValueError):
    """Raised when the OpenAI response shape is invalid."""


@dataclass(frozen=True)
class OpenAIClientSettings:
    """Configuration for creating an OpenAI transport client."""

    base_url: str
    api_key: str
    max_retries: int = DEFAULT_MAX_RETRIES
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR
    verify_ssl: bool = True
    timeout_seconds: float = 30.0


@dataclass(frozen=True)
class OpenAIResponseUsage:
    """Normalized token usage metadata extracted from an OpenAI response."""

    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
