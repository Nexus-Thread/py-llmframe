"""Application port contracts for provider-backed LLM response generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeAlias

from pydantic import BaseModel

from llmframe.shared.json_types import JsonValue

StructuredOutputSchema: TypeAlias = type[BaseModel]
"""Pydantic model type used to define a structured-output response shape."""

LlmInputItem: TypeAlias = dict[str, str]
"""One normalized chat input item passed from the application to a provider."""

JsonSchema: TypeAlias = dict[str, JsonValue]
"""JSON Schema payload passed to providers that support structured outputs."""

LlmBatchId: TypeAlias = str
"""Stable identifier of one asynchronously processed LLM batch."""


@dataclass(frozen=True, slots=True)
class LlmUsage:
    """Normalized token usage metadata returned by any LLM provider.

    Attributes:
        input_tokens: Prompt or input token count when the provider exposes it.
        output_tokens: Completion or output token count when the provider exposes it.
        total_tokens: Total token count when the provider exposes it.
    """

    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None


@dataclass(frozen=True, slots=True)
class LlmBatchRequestItem:
    """One normalized provider-facing batch request item."""

    custom_id: str
    input_items: list[LlmInputItem]
    temperature: float | None = None
    reasoning_effort: str | None = None


@dataclass(frozen=True, slots=True)
class LlmBatchSubmission:
    """Metadata returned after a batch is submitted."""

    batch_id: LlmBatchId
    input_file_id: str
    endpoint: str
    status: str
    request_count: int
    metadata: dict[str, JsonValue] | None = None


@dataclass(frozen=True, slots=True)
class LlmBatchStatus:
    """Normalized lifecycle snapshot of one batch."""

    batch_id: LlmBatchId
    status: str
    output_file_id: str | None
    error_file_id: str | None
    request_counts: dict[str, int] | None
    created_at: int | None
    in_progress_at: int | None
    completed_at: int | None
    failed_at: int | None
    expired_at: int | None
    cancelling_at: int | None
    cancelled_at: int | None
    metadata: dict[str, JsonValue] | None = None


@dataclass(frozen=True, slots=True)
class LlmBatchTextResultItem:
    """One plain-text batch result item."""

    custom_id: str
    content: str | None
    usage: LlmUsage | None
    error: str | None


@dataclass(frozen=True, slots=True)
class LlmBatchStructuredResultItem:
    """One structured-output batch result item."""

    custom_id: str
    payload: dict[str, JsonValue] | None
    usage: LlmUsage | None
    error: str | None


@dataclass(frozen=True, slots=True)
class LlmBatchTextResult:
    """Aggregated plain-text batch result."""

    batch_id: LlmBatchId
    status: str
    items: list[LlmBatchTextResultItem]


@dataclass(frozen=True, slots=True)
class LlmBatchStructuredResult:
    """Aggregated structured-output batch result."""

    batch_id: LlmBatchId
    status: str
    items: list[LlmBatchStructuredResultItem]


class LlmProviderPort(Protocol):
    """Output port for providers that support text and structured responses.

    Implementations hide provider-specific transport details behind a small,
    provider-neutral contract used by the shared LLM adapter.
    """

    def create_response(
        self,
        *,
        model: str,
        input_items: list[LlmInputItem],
        temperature: float | None = ...,
        reasoning_effort: str | None = ...,
    ) -> object:
        """Create a provider-native plain-text response for the supplied input items."""
        ...

    def create_structured_response(  # noqa: PLR0913
        self,
        *,
        model: str,
        input_items: list[LlmInputItem],
        json_schema_name: str,
        schema: JsonSchema,
        temperature: float | None = ...,
        reasoning_effort: str | None = ...,
    ) -> object:
        """Create a provider-native structured response constrained by the given JSON Schema."""
        ...

    def extract_text(self, response: object) -> str:
        """Extract plain-text content from a provider-native response object."""
        ...

    def extract_usage(self, response: object) -> LlmUsage | None:
        """Extract normalized usage metadata from a provider-native response object."""
        ...

    def submit_text_batch(
        self,
        *,
        model: str,
        requests: list[LlmBatchRequestItem],
    ) -> LlmBatchSubmission:
        """Submit a plain-text batch request to the provider."""
        ...

    def submit_structured_batch(
        self,
        *,
        model: str,
        requests: list[LlmBatchRequestItem],
        json_schema_name: str,
        schema: JsonSchema,
    ) -> LlmBatchSubmission:
        """Submit a structured-output batch request to the provider."""
        ...

    def get_batch_status(self, *, batch_id: LlmBatchId) -> LlmBatchStatus:
        """Return the current lifecycle status of a submitted batch."""
        ...

    def cancel_batch(self, *, batch_id: LlmBatchId) -> LlmBatchStatus:
        """Cancel a submitted batch and return the updated lifecycle status."""
        ...

    def get_text_batch_result(self, *, batch_id: LlmBatchId) -> LlmBatchTextResult:
        """Return parsed plain-text results for a completed batch."""
        ...

    def get_structured_batch_result(self, *, batch_id: LlmBatchId) -> LlmBatchStructuredResult:
        """Return parsed structured-output results for a completed batch."""
        ...


__all__ = [
    "JsonSchema",
    "LlmBatchId",
    "LlmBatchRequestItem",
    "LlmBatchStatus",
    "LlmBatchStructuredResult",
    "LlmBatchStructuredResultItem",
    "LlmBatchSubmission",
    "LlmBatchTextResult",
    "LlmBatchTextResultItem",
    "LlmInputItem",
    "LlmProviderPort",
    "LlmUsage",
    "StructuredOutputSchema",
]
