"""Unit tests for OpenAI provider batch behavior."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from llmframe.adapters.output.llm.providers.openai.provider_adapter import OpenAIProviderAdapter
from llmframe.application.ports import LlmBatchRequestItem

if TYPE_CHECKING:
    from llmframe.adapters.output.llm.providers.openai.transport import OpenAIClientProtocol


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


class _StubTransport:
    def __init__(self) -> None:
        self.uploaded_lines: list[object] = []
        self.batch = _Batch(
            id="batch_1",
            input_file_id="file_1",
            endpoint="/v1/responses",
            status="completed",
            output_file_id="file_out",
            request_counts=_RequestCounts(completed=1, failed=0, total=1),
        )

    def upload_batch_file(self, *, lines: list[object]) -> object:
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
        return (
            '{"custom_id":"row-1","response":{"body":{"output_text":"hello","usage":{"input_tokens":3,'
            '"output_tokens":2,"total_tokens":5}}}}\n'
        )

    def parse_batch_output_jsonl(self, *, content: str) -> list[object]:
        del content
        usage = type("Usage", (), {"input_tokens": 3, "output_tokens": 2, "total_tokens": 5})()
        response = type("Response", (), {"output_text": "hello", "usage": usage})()
        line = type("Line", (), {"custom_id": "row-1", "response_body": response, "error": None})()
        return [line]


def test_submit_text_batch_returns_normalized_submission() -> None:
    provider = OpenAIProviderAdapter(transport=cast("OpenAIClientProtocol", _StubTransport()))

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


def test_get_text_batch_result_returns_items() -> None:
    provider = OpenAIProviderAdapter(transport=cast("OpenAIClientProtocol", _StubTransport()))

    result = provider.get_text_batch_result(batch_id="batch_1")

    assert result.batch_id == "batch_1"
    assert result.items[0].content == "hello"
