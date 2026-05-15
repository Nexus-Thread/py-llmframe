"""Persist submitted LLM batch request metadata as addressable JSON files."""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING, cast

from llmframe.application.ports.batch_request_store import StoredLlmBatchRequest

if TYPE_CHECKING:
    from pathlib import Path

    from llmframe.application.ports.llm_provider import LlmBatchId
    from llmframe.shared.json_types import JsonValue

LOGGER = logging.getLogger(__name__)
_BATCH_ID_PATTERN = re.compile(r"[^a-zA-Z0-9_-]+")


class JsonFileBatchRequestStoreAdapter:
    """Store one JSON document per batch ID for durable later lookup."""

    def __init__(self, *, base_dir: Path) -> None:
        """Initialize the adapter with the base directory for batch records."""
        self._base_dir = base_dir

    def save_batch_request(self, *, batch_request: StoredLlmBatchRequest) -> Path:
        """Persist one batch request record and return the written file path."""
        file_path = self._build_file_path(batch_id=batch_request.batch_id)
        payload = self._serialize_batch_request(batch_request=batch_request)
        self._write_payload(file_path=file_path, payload=payload)
        LOGGER.debug(
            "Stored LLM batch request metadata",
            extra={
                "component": self.__class__.__name__,
                "batch_id": batch_request.batch_id,
                "file_path": str(file_path),
            },
        )
        return file_path

    def get_batch_request(self, *, batch_id: LlmBatchId) -> StoredLlmBatchRequest | None:
        """Load one persisted batch request record when it exists."""
        file_path = self._build_file_path(batch_id=batch_id)
        if not file_path.exists():
            return None
        with file_path.open("r", encoding="utf-8") as file_handle:
            payload = cast("dict[str, JsonValue]", json.load(file_handle))
        return self._deserialize_batch_request(payload=payload)

    @staticmethod
    def _sanitize_batch_id(batch_id: str) -> str:
        """Normalize a batch ID into a safe file name component."""
        sanitized = _BATCH_ID_PATTERN.sub("_", batch_id.strip()).strip("_")
        return sanitized or "batch"

    def _build_file_path(self, *, batch_id: str) -> Path:
        """Return the stable storage path for one batch ID."""
        sanitized_batch_id = self._sanitize_batch_id(batch_id)
        return self._base_dir / f"{sanitized_batch_id}.json"

    @staticmethod
    def _write_payload(*, file_path: Path, payload: dict[str, JsonValue]) -> None:
        """Write one normalized JSON payload to disk."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as file_handle:
            json.dump(payload, file_handle, ensure_ascii=False, indent=2, sort_keys=True)
            file_handle.write("\n")

    @staticmethod
    def _serialize_batch_request(*, batch_request: StoredLlmBatchRequest) -> dict[str, JsonValue]:
        """Convert one stored batch record into a JSON-compatible payload."""
        payload: dict[str, JsonValue] = {
            "batch_id": batch_request.batch_id,
            "submitted_at": batch_request.submitted_at.astimezone(UTC).isoformat(),
            "model": batch_request.model,
            "request_kind": batch_request.request_kind,
            "input_file_id": batch_request.input_file_id,
            "endpoint": batch_request.endpoint,
            "status": batch_request.status,
            "request_count": batch_request.request_count,
        }
        if batch_request.metadata is not None:
            payload["metadata"] = batch_request.metadata
        return payload

    @staticmethod
    def _deserialize_batch_request(*, payload: dict[str, JsonValue]) -> StoredLlmBatchRequest:
        """Convert a JSON payload back into a stored batch record."""
        batch_id = str(payload["batch_id"])
        submitted_at = datetime.fromisoformat(str(payload["submitted_at"])).astimezone(UTC)
        model = str(payload["model"])
        request_kind = str(payload["request_kind"])
        input_file_id = str(payload["input_file_id"])
        endpoint = str(payload["endpoint"])
        status = str(payload["status"])
        request_count = int(cast("int | float | str", payload["request_count"]))
        metadata = cast("dict[str, JsonValue] | None", payload.get("metadata"))
        return StoredLlmBatchRequest(
            batch_id=batch_id,
            submitted_at=submitted_at,
            model=model,
            request_kind=request_kind,
            input_file_id=input_file_id,
            endpoint=endpoint,
            status=status,
            request_count=request_count,
            metadata=metadata,
        )
