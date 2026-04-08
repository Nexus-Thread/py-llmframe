"""Unit tests for OpenAI batch transport behavior."""

from __future__ import annotations

from dataclasses import dataclass

from llmframe.adapters.output.llm.providers.openai.dto import OpenAIBatchRequestLine
from llmframe.adapters.output.llm.providers.openai.transport import OpenAIClient


@dataclass
class _StubFiles:
    created: list[tuple[object, str]]
    content_calls: list[str]

    def create(self, *, file: object, purpose: str) -> object:
        self.created.append((file, purpose))
        return type("FileObject", (), {"id": "file_1", "purpose": purpose})()

    def content(self, file_id: str) -> str:
        self.content_calls.append(file_id)
        return '{"custom_id":"row-1","response":{"body":{"output_text":"hello"}}}\n'


@dataclass
class _StubBatches:
    created: list[tuple[str, str, str]]
    retrieved: list[str]

    def create(
        self,
        *,
        completion_window: str,
        endpoint: str,
        input_file_id: str,
        metadata: dict[str, str] | None = None,
    ) -> object:
        del metadata
        self.created.append((completion_window, endpoint, input_file_id))
        return type("Batch", (), {"id": "batch_1"})()

    def retrieve(self, batch_id: str) -> object:
        self.retrieved.append(batch_id)
        return type("Batch", (), {"id": batch_id})()

    def cancel(self, batch_id: str) -> object:
        self.retrieved.append(batch_id)
        return type("Batch", (), {"id": batch_id})()


@dataclass
class _StubSdkClient:
    chat: object
    responses: object
    files: _StubFiles
    batches: _StubBatches


def test_upload_batch_file_uses_batch_purpose() -> None:
    client = OpenAIClient(
        sdk_client=_StubSdkClient(
            chat=object(),
            responses=object(),
            files=_StubFiles(created=[], content_calls=[]),
            batches=_StubBatches(created=[], retrieved=[]),
        ),
        max_retries=0,
    )

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
    batches = _StubBatches(created=[], retrieved=[])
    client = OpenAIClient(
        sdk_client=_StubSdkClient(
            chat=object(),
            responses=object(),
            files=_StubFiles(created=[], content_calls=[]),
            batches=batches,
        ),
        max_retries=0,
    )

    client.create_response_batch(input_file_id="file_1")

    assert batches.created == [("24h", "/v1/responses", "file_1")]
