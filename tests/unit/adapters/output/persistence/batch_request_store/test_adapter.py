"""Unit tests for the JSON-file batch request store adapter."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from llmframe.adapters.output.persistence import JsonFileBatchRequestStoreAdapter
from llmframe.application import StoredLlmBatchRequest

if TYPE_CHECKING:
    from pathlib import Path


def test_save_batch_request_writes_addressable_json_record(tmp_path: Path) -> None:
    """Persist batch metadata under a stable batch-ID-based file name."""
    adapter = JsonFileBatchRequestStoreAdapter(base_dir=tmp_path)

    written_path = adapter.save_batch_request(
        batch_request=StoredLlmBatchRequest(
            batch_id="batch/123",
            submitted_at=datetime(2026, 4, 8, 10, 0, tzinfo=UTC),
            model="gpt-test",
            request_kind="text",
            input_file_id="file_123",
            endpoint="/v1/responses",
            status="validating",
            request_count=2,
            metadata={"provider": "openai"},
        )
    )

    assert written_path == tmp_path / "batch_123.json"
    assert written_path.read_text(encoding="utf-8").endswith("\n")


def test_get_batch_request_returns_persisted_record(tmp_path: Path) -> None:
    """Load back a previously stored batch metadata record."""
    adapter = JsonFileBatchRequestStoreAdapter(base_dir=tmp_path)
    expected = StoredLlmBatchRequest(
        batch_id="batch_123",
        submitted_at=datetime(2026, 4, 8, 10, 0, tzinfo=UTC),
        model="gpt-test",
        request_kind="structured",
        input_file_id="file_123",
        endpoint="/v1/responses",
        status="in_progress",
        request_count=4,
        metadata={"source": "test"},
    )
    adapter.save_batch_request(batch_request=expected)

    loaded = adapter.get_batch_request(batch_id="batch_123")

    assert loaded == expected


def test_get_batch_request_returns_none_for_missing_record(tmp_path: Path) -> None:
    """Return None when no persisted batch metadata exists for the batch ID."""
    adapter = JsonFileBatchRequestStoreAdapter(base_dir=tmp_path)

    assert adapter.get_batch_request(batch_id="missing") is None
