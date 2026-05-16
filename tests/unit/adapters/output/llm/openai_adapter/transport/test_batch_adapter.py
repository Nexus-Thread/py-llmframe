"""Unit tests for OpenAI batch transport behavior."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast

import pytest

from llmframe.adapters.output.llm.providers.openai.dto import OpenAIBatchRequestLine
from llmframe.adapters.output.llm.providers.openai.transport import OpenAIClient


@dataclass(frozen=True)
class _Batch:
    id: str


@dataclass
class _StubFiles:
    created: list[tuple[object, str]]
    content_calls: list[str]
    content_response: object = '{"custom_id":"row-1","response":{"body":{"output_text":"hello"}}}\n'

    def create(self, *, file: object, purpose: str) -> object:
        self.created.append((file, purpose))
        return type("FileObject", (), {"id": "file_1", "purpose": purpose})()

    def content(self, file_id: str) -> object:
        self.content_calls.append(file_id)
        return self.content_response


@dataclass
class _StubBatches:
    created: list[tuple[str, str, str]]
    retrieved: list[str]
    cancelled: list[str]

    def create(
        self,
        *,
        completion_window: str,
        endpoint: str,
        input_file_id: str,
        metadata: dict[str, str] | None = None,
    ) -> _Batch:
        del metadata
        self.created.append((completion_window, endpoint, input_file_id))
        return _Batch(id="batch_1")

    def retrieve(self, batch_id: str) -> _Batch:
        self.retrieved.append(batch_id)
        return _Batch(id=batch_id)

    def cancel(self, batch_id: str) -> _Batch:
        self.cancelled.append(batch_id)
        return _Batch(id=batch_id)


@dataclass
class _StubSdkClient:
    chat: object
    responses: object
    files: _StubFiles
    batches: _StubBatches


class _TextPropertyContent:
    text = "property content"


class _TextMethodContent:
    def text(self) -> str:
        return "method content"


class _ReadMethodContent:
    def __init__(self, value: bytes | str) -> None:
        self._value = value

    def read(self) -> bytes | str:
        return self._value


def _build_batch_client(
    *,
    files: _StubFiles | None = None,
    batches: _StubBatches | None = None,
) -> tuple[OpenAIClient, _StubFiles, _StubBatches]:
    resolved_files = files or _StubFiles(created=[], content_calls=[])
    resolved_batches = batches or _StubBatches(created=[], retrieved=[], cancelled=[])
    client = OpenAIClient(
        sdk_client=_StubSdkClient(
            chat=object(),
            responses=object(),
            files=resolved_files,
            batches=resolved_batches,
        ),
        max_retries=0,
    )
    return client, resolved_files, resolved_batches


def test_upload_batch_file_uses_batch_purpose() -> None:
    client, _, _ = _build_batch_client()

    upload = client.upload_batch_file(
        lines=[
            OpenAIBatchRequestLine(
                custom_id="row-1",
                method="POST",
                url="/v1/responses",
                body={"model": "gpt-test", "input": [{"role": "user", "content": "hello"}]},
            )
        ]
    )

    assert upload.file_id == "file_1"
    assert upload.purpose == "batch"


def test_create_response_batch_uses_responses_endpoint() -> None:
    batches = _StubBatches(created=[], retrieved=[], cancelled=[])
    client, _, _ = _build_batch_client(batches=batches)

    client.create_response_batch(input_file_id="file_1")

    assert batches.created == [("24h", "/v1/responses", "file_1")]


def test_retrieve_batch_delegates_to_batch_namespace() -> None:
    client, _, batches = _build_batch_client()

    batch = cast("_Batch", client.retrieve_batch(batch_id="batch_1"))

    assert batch.id == "batch_1"
    assert batches.retrieved == ["batch_1"]


def test_cancel_batch_delegates_to_batch_namespace() -> None:
    client, _, batches = _build_batch_client()

    batch = cast("_Batch", client.cancel_batch(batch_id="batch_1"))

    assert batch.id == "batch_1"
    assert batches.cancelled == ["batch_1"]


@pytest.mark.parametrize(
    ("content_response", "expected"),
    [
        (b"byte content", "byte content"),
        ("string content", "string content"),
        (_TextPropertyContent(), "property content"),
        (_TextMethodContent(), "method content"),
        (_ReadMethodContent(b"read bytes"), "read bytes"),
        (_ReadMethodContent("read string"), "read string"),
    ],
)
def test_download_batch_output_normalizes_sdk_content_shapes(content_response: object, expected: str) -> None:
    files = _StubFiles(created=[], content_calls=[], content_response=content_response)
    client, _, _ = _build_batch_client(files=files)

    content = client.download_batch_output(file_id="file_out")

    assert content == expected
    assert files.content_calls == ["file_out"]


@pytest.mark.parametrize(
    ("raw_jsonl", "expected_error"),
    [
        (
            '{"custom_id":"row-1","response":{"body":{"output_text":"hello"}}}\n',
            None,
        ),
        (
            '{"custom_id":"row-2","error":{"code":"rate_limit","message":"try later"}}\n',
            '{"code": "rate_limit", "message": "try later"}',
        ),
    ],
)
def test_parse_batch_output_jsonl_normalizes_result_and_error_lines(
    raw_jsonl: str,
    expected_error: Literal['{"code": "rate_limit", "message": "try later"}'] | None,
) -> None:
    client, _, _ = _build_batch_client()

    lines = client.parse_batch_output_jsonl(content=raw_jsonl)

    assert len(lines) == 1
    assert lines[0].error == expected_error
    if expected_error is None:
        assert lines[0].custom_id == "row-1"
        assert lines[0].response_body == {"output_text": "hello"}
    else:
        assert lines[0].custom_id == "row-2"
        assert lines[0].response_body is None
