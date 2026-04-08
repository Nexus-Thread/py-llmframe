"""Live integration test for batch submission behavior."""

from __future__ import annotations

from llmframe import LlmBatchTextRequest

from .helpers import PYTEST_MARKS, build_live_adapter, read_batch_request_output_dir

pytestmark = PYTEST_MARKS

EXPECTED_REQUEST_COUNT = 2


def test_submit_text_batch_live_persists_submission_metadata() -> None:
    """The public adapter submits a tiny batch and persists its metadata for later retrieval."""
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
