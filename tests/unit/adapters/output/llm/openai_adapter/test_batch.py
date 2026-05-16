"""Unit tests for OpenAI provider batch behavior."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

import pytest

from llmframe.adapters.output.llm.llm_adapter.exceptions import StructuredLlmResponseError
from llmframe.adapters.output.llm.providers.openai.provider_adapter import OpenAIProviderAdapter
from llmframe.application.ports import LlmBatchRequestItem

if TYPE_CHECKING:
    from llmframe.adapters.output.llm.providers.openai.dto import OpenAIBatchRequestLine
    from llmframe.adapters.output.llm.providers.openai.transport import OpenAIClientProtocol

TEXT_RESULT_TOTAL_TOKENS = 5
STRUCTURED_RESULT_TOTAL_TOKENS = 7
CREATED_AT = 10
IN_PROGRESS_AT = 20
COMPLETED_AT = 30
CANCELLED_AT = 40


@dataclass(frozen=True)
class _Batch:
    id: str
    input_file_id: str
    endpoint: str
    status: str
    output_file_id: str | None = None
    error_file_id: str | None = None
    created_at: int | None = None
    in_progress_at: int | None = None
    completed_at: int | None = None
    failed_at: int | None = None
    expired_at: int | None = None
    cancelling_at: int | None = None
    cancelled_at: int | None = None
    request_counts: object | None = None
    metadata: dict[str, str] | None = None


@dataclass(frozen=True)
class _RequestCounts:
    completed: int
    failed: int
    total: int


@dataclass(frozen=True)
class _Usage:
    input_tokens: int
    output_tokens: int
    total_tokens: int


@dataclass(frozen=True)
class _ParsedBatchLine:
    custom_id: str
    response_body: object | None
    error: str | None = None


class _StubTransport:
    def __init__(self) -> None:
        self.uploaded_lines: list[OpenAIBatchRequestLine] = []
        self.downloaded_file_ids: list[str] = []
        self.batch = _Batch(
            id="batch_1",
            input_file_id="file_1",
            endpoint="/v1/responses",
            status="completed",
            output_file_id="file_out",
            request_counts=_RequestCounts(completed=1, failed=0, total=1),
        )
        response = type("Response", (), {"output_text": "hello", "usage": _Usage(3, 2, TEXT_RESULT_TOTAL_TOKENS)})()
        self.parsed_lines: list[object] = [_ParsedBatchLine(custom_id="row-1", response_body=response)]

    def upload_batch_file(self, *, lines: list[OpenAIBatchRequestLine]) -> object:
        self.uploaded_lines = lines
        return type("Upload", (), {"file_id": "file_1", "purpose": "batch"})()

    def create_response_batch(self, *, input_file_id: str, metadata: dict[str, str] | None = None) -> object:
        del input_file_id, metadata
        return self.batch

    def retrieve_batch(self, *, batch_id: str) -> object:
        assert batch_id == "batch_1"
        return self.batch

    def cancel_batch(self, *, batch_id: str) -> object:
        assert batch_id == "batch_1"
        return self.batch

    def download_batch_output(self, *, file_id: str) -> str:
        assert file_id == "file_out"
        self.downloaded_file_ids.append(file_id)
        return (
            '{"custom_id":"row-1","response":{"body":{"output_text":"hello","usage":{"input_tokens":3,'
            '"output_tokens":2,"total_tokens":5}}}}\n'
        )

    def parse_batch_output_jsonl(self, *, content: str) -> list[object]:
        del content
        return self.parsed_lines


def _build_provider_and_transport(*, batch: _Batch | None = None) -> tuple[OpenAIProviderAdapter, _StubTransport]:
    """Build a provider backed by the stub transport."""
    transport = _StubTransport()
    if batch is not None:
        transport.batch = batch
    return OpenAIProviderAdapter(transport=cast("OpenAIClientProtocol", transport)), transport


def _build_provider(*, batch: _Batch | None = None) -> OpenAIProviderAdapter:
    """Build a provider backed by the stub transport."""
    provider, _ = _build_provider_and_transport(batch=batch)
    return provider


def test_submit_text_batch_returns_normalized_submission() -> None:
    provider = _build_provider()

    result = provider.submit_text_batch(
        model="gpt-test",
        requests=[
            LlmBatchRequestItem(
                custom_id="row-1",
                input_items=[{"role": "user", "content": "hello"}],
            )
        ],
    )

    assert result.batch_id == "batch_1"
    assert result.request_count == 1


def test_submit_structured_batch_builds_structured_request_line() -> None:
    provider, transport = _build_provider_and_transport()

    result = provider.submit_structured_batch(
        model="gpt-test",
        requests=[
            LlmBatchRequestItem(
                custom_id="row-1",
                input_items=[{"role": "user", "content": "hello"}],
                temperature=0.2,
                reasoning_effort="low",
            )
        ],
        json_schema_name="ExampleSchema",
        schema={"type": "object", "properties": {"ok": {"type": "boolean"}}},
    )

    assert result.batch_id == "batch_1"
    assert len(transport.uploaded_lines) == 1
    line = transport.uploaded_lines[0]
    assert line.custom_id == "row-1"
    assert line.body == {
        "model": "gpt-test",
        "input": [{"role": "user", "content": "hello"}],
        "temperature": 0.2,
        "reasoning": {"effort": "low"},
        "text": {
            "format": {
                "type": "json_schema",
                "name": "ExampleSchema",
                "strict": True,
                "schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}},
            }
        },
    }


def test_get_text_batch_result_returns_items() -> None:
    provider = _build_provider()

    result = provider.get_text_batch_result(batch_id="batch_1")

    assert result.batch_id == "batch_1"
    assert result.items[0].content == "hello"
    assert result.items[0].usage is not None
    assert result.items[0].usage.total_tokens == TEXT_RESULT_TOTAL_TOKENS


def test_get_text_batch_result_preserves_provider_error_lines() -> None:
    provider, transport = _build_provider_and_transport()
    transport.parsed_lines = [_ParsedBatchLine(custom_id="row-1", response_body=None, error='{"code": "rate_limit"}')]

    result = provider.get_text_batch_result(batch_id="batch_1")

    assert result.status == "completed"
    assert result.items[0].custom_id == "row-1"
    assert result.items[0].content is None
    assert result.items[0].usage is None
    assert result.items[0].error == '{"code": "rate_limit"}'


def test_get_structured_batch_result_parses_json_payload_and_usage() -> None:
    provider, transport = _build_provider_and_transport()
    response = type(
        "Response",
        (),
        {"output_text": '{"ok": true}', "usage": _Usage(4, 3, STRUCTURED_RESULT_TOTAL_TOKENS)},
    )()
    transport.parsed_lines = [_ParsedBatchLine(custom_id="row-1", response_body=response)]

    result = provider.get_structured_batch_result(batch_id="batch_1")

    assert result.batch_id == "batch_1"
    assert result.items[0].payload == {"ok": True}
    assert result.items[0].usage is not None
    assert result.items[0].usage.total_tokens == STRUCTURED_RESULT_TOTAL_TOKENS


def test_get_structured_batch_result_preserves_provider_error_lines() -> None:
    provider, transport = _build_provider_and_transport()
    transport.parsed_lines = [_ParsedBatchLine(custom_id="row-1", response_body=None, error='{"code": "invalid"}')]

    result = provider.get_structured_batch_result(batch_id="batch_1")

    assert result.status == "completed"
    assert result.items[0].custom_id == "row-1"
    assert result.items[0].payload is None
    assert result.items[0].usage is None
    assert result.items[0].error == '{"code": "invalid"}'


def test_get_structured_batch_result_returns_empty_items_for_empty_provider_output() -> None:
    provider, transport = _build_provider_and_transport()
    transport.parsed_lines = []

    result = provider.get_structured_batch_result(batch_id="batch_1")

    assert result.batch_id == "batch_1"
    assert result.status == "completed"
    assert result.items == []


def test_get_batch_status_includes_request_counts() -> None:
    provider = _build_provider()

    result = provider.get_batch_status(batch_id="batch_1")

    assert result.request_counts == {"completed": 1, "failed": 0, "total": 1}


def test_get_batch_status_preserves_metadata_and_timestamps() -> None:
    provider = _build_provider(
        batch=_Batch(
            id="batch_1",
            input_file_id="file_1",
            endpoint="/v1/responses",
            status="completed",
            output_file_id="file_out",
            created_at=CREATED_AT,
            in_progress_at=IN_PROGRESS_AT,
            completed_at=COMPLETED_AT,
            metadata={"source": "unit-test"},
        )
    )

    result = provider.get_batch_status(batch_id="batch_1")

    assert result.created_at == CREATED_AT
    assert result.in_progress_at == IN_PROGRESS_AT
    assert result.completed_at == COMPLETED_AT
    assert result.metadata == {"source": "unit-test"}


def test_cancel_batch_returns_normalized_status() -> None:
    provider = _build_provider(
        batch=_Batch(
            id="batch_1",
            input_file_id="file_1",
            endpoint="/v1/responses",
            status="cancelled",
            cancelled_at=CANCELLED_AT,
        )
    )

    result = provider.cancel_batch(batch_id="batch_1")

    assert result.batch_id == "batch_1"
    assert result.status == "cancelled"
    assert result.cancelled_at == CANCELLED_AT


def test_get_text_batch_result_requires_output_file() -> None:
    provider = _build_provider(
        batch=_Batch(
            id="batch_1",
            input_file_id="file_1",
            endpoint="/v1/responses",
            status="in_progress",
            output_file_id=None,
        )
    )

    with pytest.raises(StructuredLlmResponseError, match="Batch output file is not available"):
        provider.get_text_batch_result(batch_id="batch_1")


def test_get_structured_batch_result_requires_output_file() -> None:
    provider = _build_provider(
        batch=_Batch(
            id="batch_1",
            input_file_id="file_1",
            endpoint="/v1/responses",
            status="failed",
            output_file_id=None,
        )
    )

    with pytest.raises(StructuredLlmResponseError, match="Batch output file is not available") as exc_info:
        provider.get_structured_batch_result(batch_id="batch_1")

    assert "failed" in str(exc_info.value.suggestion)
