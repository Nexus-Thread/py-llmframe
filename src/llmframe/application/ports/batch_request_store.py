"""Application port contracts for persistent LLM batch submission storage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from datetime import datetime
    from pathlib import Path

    from llmframe.application.ports.llm_provider import LlmBatchId
    from llmframe.shared.json_types import JsonValue


@dataclass(frozen=True, slots=True)
class StoredLlmBatchRequest:
    """Persistent metadata for one submitted LLM batch request.

    Attributes:
        batch_id: Provider batch identifier used for later polling and retrieval.
        submitted_at: UTC timestamp when the batch submission was persisted.
        model: Model identifier used for the batch submission.
        request_kind: High-level request kind, for example ``text`` or ``structured``.
        input_file_id: Provider input file identifier associated with the batch.
        endpoint: Provider endpoint used for the batch.
        status: Provider-reported submission status at persistence time.
        request_count: Number of request items included in the batch.
        metadata: Optional provider metadata preserved for later inspection.
    """

    batch_id: LlmBatchId
    submitted_at: datetime
    model: str
    request_kind: str
    input_file_id: str
    endpoint: str
    status: str
    request_count: int
    metadata: dict[str, JsonValue] | None = None


class BatchRequestStorePort(Protocol):
    """Port for durable storage of submitted LLM batch metadata."""

    def save_batch_request(self, *, batch_request: StoredLlmBatchRequest) -> Path:
        """Persist a batch request record and return its storage location."""
        ...

    def get_batch_request(self, *, batch_id: LlmBatchId) -> StoredLlmBatchRequest | None:
        """Return a persisted batch request record when available."""
        ...


__all__ = ["BatchRequestStorePort", "StoredLlmBatchRequest"]
