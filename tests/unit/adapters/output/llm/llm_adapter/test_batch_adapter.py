"""Unit tests for shared LLM adapter batch behavior."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pytest

from llmframe.adapters.output.llm.llm_adapter import (
    LlmAdapter,
    LlmBatchStructuredRequest,
    LlmBatchTextRequest,
    StructuredLlmBatchError,
)

if TYPE_CHECKING:
    from llmframe.application.ports import LlmProviderPort, StoredLlmBatchRequest


@dataclass(frozen=True)
class _BatchSubmission:
    batch_id: str
    input_file_id: str
    endpoint: str
    status: str
    request_count: int
    metadata: dict[str, object] | None = None


class _StubBatchClient:
    def __init__(self) -> None:
        self.text_batch_calls: list[tuple[str, list[object]]] = []
        self.structured_batch_calls: list[tuple[str, list[object], str, dict[str, object]]] = []

    def submit_text_batch(self, *, model: str, requests: list[object]) -> _BatchSubmission:
        self.text_batch_calls.append((model, requests))
        return _BatchSubmission(
            batch_id="batch_123",
            input_file_id="file_123",
            endpoint="/v1/responses",
            status="validating",
            request_count=len(requests),
        )

    def submit_structured_batch(
        self,
        *,
        model: str,
        requests: list[object],
        json_schema_name: str,
        schema: dict[str, object],
    ) -> _BatchSubmission:
        self.structured_batch_calls.append((model, requests, json_schema_name, schema))
        return _BatchSubmission(
            batch_id="batch_456",
            input_file_id="file_456",
            endpoint="/v1/responses",
            status="validating",
            request_count=len(requests),
        )

    def create_response(self, **kwargs: object) -> object:
        raise AssertionError(kwargs)

    def create_structured_response(self, **kwargs: object) -> object:
        raise AssertionError(kwargs)

    def extract_text(self, response: object) -> str:
        raise AssertionError(response)

    def extract_usage(self, response: object) -> object | None:
        raise AssertionError(response)

    def get_batch_status(self, *, batch_id: str) -> object:
        raise AssertionError(batch_id)

    def cancel_batch(self, *, batch_id: str) -> object:
        raise AssertionError(batch_id)

    def get_text_batch_result(self, *, batch_id: str) -> object:
        raise AssertionError(batch_id)

    def get_structured_batch_result(self, *, batch_id: str) -> object:
        raise AssertionError(batch_id)


class _StubBatchRequestStore:
    def __init__(self) -> None:
        self.saved_records: list[StoredLlmBatchRequest] = []

    def save_batch_request(self, *, batch_request: StoredLlmBatchRequest) -> Path:
        self.saved_records.append(batch_request)
        return Path(f"batches/{batch_request.batch_id}.json")

    def get_batch_request(self, *, batch_id: str) -> StoredLlmBatchRequest | None:
        return next((record for record in self.saved_records if record.batch_id == batch_id), None)


def test_submit_text_batch_normalizes_prompt_pairs() -> None:
    client = _StubBatchClient()
    store = _StubBatchRequestStore()
    adapter = LlmAdapter(client=cast("LlmProviderPort", client), model="gpt-test", batch_request_store=store)

    result = adapter.submit_text_batch(
        requests=[
            LlmBatchTextRequest(
                custom_id="row-1",
                developer_prompt="dev",
                user_prompt="user",
                temperature=0.2,
                reasoning_effort="low",
            )
        ]
    )

    assert result.batch_id == "batch_123"
    assert len(client.text_batch_calls) == 1
    _, requests = client.text_batch_calls[0]
    first_request = cast("Any", requests[0])
    assert first_request.custom_id == "row-1"
    assert first_request.input_items == [
        {"role": "developer", "content": "dev"},
        {"role": "user", "content": "user"},
    ]
    assert len(store.saved_records) == 1
    assert store.saved_records[0].batch_id == "batch_123"
    assert store.saved_records[0].model == "gpt-test"
    assert store.saved_records[0].request_kind == "text"


def test_submit_structured_batch_persists_submission_metadata() -> None:
    client = _StubBatchClient()
    store = _StubBatchRequestStore()
    adapter = LlmAdapter(client=cast("LlmProviderPort", client), model="gpt-test", batch_request_store=store)

    class _SchemaModel:
        @staticmethod
        def model_json_schema() -> dict[str, object]:
            return {
                "type": "object",
                "properties": {"answer": {"type": "string"}},
                "required": ["answer"],
            }

    result = adapter.submit_structured_batch(
        requests=[LlmBatchStructuredRequest(custom_id="row-1", developer_prompt="dev", user_prompt="user")],
        response_schema=cast("Any", _SchemaModel),
    )

    assert result.batch_id == "batch_456"
    assert len(store.saved_records) == 1
    assert store.saved_records[0].batch_id == "batch_456"
    assert store.saved_records[0].request_kind == "structured"
    assert store.saved_records[0].submitted_at.tzinfo == UTC


def test_submit_text_batch_rejects_duplicate_custom_ids() -> None:
    adapter = LlmAdapter(client=cast("LlmProviderPort", _StubBatchClient()), model="gpt-test")

    with pytest.raises(StructuredLlmBatchError, match="custom_id"):
        adapter.submit_text_batch(
            requests=[
                LlmBatchTextRequest(custom_id="dup", developer_prompt="a", user_prompt="b"),
                LlmBatchTextRequest(custom_id="dup", developer_prompt="c", user_prompt="d"),
            ]
        )


def test_submit_structured_batch_requires_schema() -> None:
    adapter = LlmAdapter(client=cast("LlmProviderPort", _StubBatchClient()), model="gpt-test")

    with pytest.raises(Exception, match="response schema"):
        adapter.submit_structured_batch(
            requests=[LlmBatchStructuredRequest(custom_id="row-1", developer_prompt="dev", user_prompt="user")]
        )
