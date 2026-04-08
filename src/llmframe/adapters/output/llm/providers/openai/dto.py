"""Public DTOs and exceptions for shared OpenAI response handling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 2.0


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


OpenAIBatchEndpoint = Literal["/v1/responses"]
OpenAIBatchStatus = Literal[
    "validating",
    "failed",
    "in_progress",
    "finalizing",
    "completed",
    "expired",
    "cancelling",
    "cancelled",
]


@dataclass(frozen=True, slots=True)
class OpenAIBatchRequestLine:
    """One OpenAI Batch JSONL request line."""

    custom_id: str
    method: Literal["POST"]
    url: OpenAIBatchEndpoint
    body: dict[str, object]


@dataclass(frozen=True, slots=True)
class OpenAIBatchFileUpload:
    """Metadata about the uploaded JSONL input file used by one batch."""

    file_id: str
    purpose: str


@dataclass(frozen=True, slots=True)
class OpenAIBatchResultLine:
    """One parsed OpenAI Batch output line."""

    custom_id: str
    response_body: object | None
    error: str | None
