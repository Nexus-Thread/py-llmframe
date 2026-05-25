"""Live integration test for the complete batch flow."""

from __future__ import annotations

import pytest

from llmframe import LlmBatchTextRequest

from .helpers import PYTEST_MARKS, build_live_adapter, read_batch_request_output_dir, wait_for_batch_completion

pytestmark = PYTEST_MARKS

EXPECTED_REQUEST_COUNT = 2
EXPECTED_CUSTOM_IDS = {"tiny-text-1", "tiny-text-2"}


def test_text_batch_live_submits_waits_and_returns_results() -> None:
    """The public adapter submits a tiny batch and retrieves its completed results."""
    adapter, _ = build_live_adapter()

    submission = adapter.submit_text_batch(
        requests=[
            LlmBatchTextRequest(
                custom_id="tiny-text-1",
                developer_prompt="Reply with exactly OK.",
                user_prompt="Return OK.",
                temperature=0,
            ),
            LlmBatchTextRequest(
                custom_id="tiny-text-2",
                developer_prompt="Reply with exactly NOK.",
                user_prompt="Return NOK.",
                temperature=0,
            ),
        ]
    )

    assert submission.batch_id
    assert submission.request_count == EXPECTED_REQUEST_COUNT
    persisted_record = read_batch_request_output_dir() / f"{submission.batch_id}.json"
    assert persisted_record.exists()

    final_status = wait_for_batch_completion(adapter, batch_id=submission.batch_id)
    if final_status != "completed":
        pytest.skip(
            f"Batch {submission.batch_id} reached terminal status {final_status!r} instead of 'completed'.",
        )

    result = adapter.get_text_batch_result(batch_id=submission.batch_id)

    assert result.batch_id == submission.batch_id
    assert result.status == "completed"
    assert len(result.items) == EXPECTED_REQUEST_COUNT
    assert {item.custom_id for item in result.items} == EXPECTED_CUSTOM_IDS
    assert all(item.error is None for item in result.items)
    assert all(item.content for item in result.items)
