"""Live integration test for batch status and result retrieval behavior."""

from __future__ import annotations

import pytest

from .helpers import (
    PYTEST_MARKS,
    build_live_adapter,
    read_batch_id_for_retrieval,
    wait_for_batch_completion,
)

pytestmark = PYTEST_MARKS


def test_get_text_batch_result_live_for_completed_batch() -> None:
    """The public adapter reads results for a previously submitted completed batch."""
    adapter, _ = build_live_adapter()
    batch_id = read_batch_id_for_retrieval()

    final_status = wait_for_batch_completion(adapter, batch_id=batch_id)
    if final_status != "completed":
        pytest.skip(
            f"Batch {batch_id} reached terminal status {final_status!r} instead of 'completed'.",
        )

    result = adapter.get_text_batch_result(batch_id=batch_id)

    assert result.batch_id == batch_id
    assert result.status == "completed"
    assert result.items
