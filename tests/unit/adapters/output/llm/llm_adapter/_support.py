"""Shared local test doubles for LLM adapter unit tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast

from pydantic import BaseModel, ConfigDict

from llmframe.adapters.output.llm.llm_adapter import LlmAdapter, StructuredLlmResponseError
from llmframe.application.ports import LlmUsage

if TYPE_CHECKING:
    import logging
    from collections.abc import Mapping as MappingType

    import pytest

    from llmframe.application.ports import (
        LlmBatchRequestItem,
        LlmBatchStatus,
        LlmBatchStructuredResult,
        LlmBatchSubmission,
        LlmBatchTextResult,
        LlmInputItem,
    )
    from llmframe.application.ports.llm_provider import JsonSchema
    from llmframe.shared.json_types import JsonValue

LOGGER_NAME = "llmframe.adapters.output.llm.llm_adapter.base"
TINY_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFElEQVQImWP8z8Dwn4GBgYGJAQoAHxcCAr7cGDwAAAAASUVORK5CYII="
)
EXPECTED_INPUTS = [
    {"role": "developer", "content": "developer"},
    {"role": "user", "content": "user"},
]


class _StructuredLogRecord(Protocol):
    model: str
    api_surface: str
    debug_label: str
    payload_preview_omitted: bool
    payload_kind: str
    payload_keys: list[str]
    payload_length: int
    file_path: str


@dataclass(frozen=True)
class _Message:
    content: str | None


@dataclass(frozen=True)
class _Choice:
    message: _Message | None


@dataclass(frozen=True)
class _Response:
    choices: list[_Choice] | None
    usage: object | None = None


@dataclass(frozen=True)
class _Usage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True)
class _ResponsesApiResponse:
    output_text: str
    usage: object | None = None


class _StubClient:
    """Stub provider implementation for LLM adapter tests."""

    def __init__(self, responses: list[object]) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, str, list[LlmInputItem]]] = []
        self.structured_schemas: list[MappingType[str, object]] = []

    def create_response(
        self,
        *,
        model: str,
        input_items: list[LlmInputItem],
        temperature: float | None = None,
        reasoning_effort: str | None = None,
    ) -> object:
        del temperature, reasoning_effort
        self.calls.append(("responses_plain", model, input_items))
        return self._responses.pop(0)

    def create_structured_response(  # noqa: PLR0913
        self,
        *,
        model: str,
        input_items: list[LlmInputItem],
        json_schema_name: str,
        schema: JsonSchema,
        temperature: float | None = None,
        reasoning_effort: str | None = None,
    ) -> object:
        del temperature, reasoning_effort, json_schema_name
        self.calls.append(("responses_structured", model, input_items))
        self.structured_schemas.append(schema)
        return self._responses.pop(0)

    def create_structured_chat_completion(  # noqa: PLR0913
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        json_schema_name: str,
        schema: JsonSchema,
        temperature: float | None = None,
        reasoning_effort: str | None = None,
    ) -> object:
        """Provide the full protocol surface expected by the shared adapter type."""
        del temperature, reasoning_effort, json_schema_name
        self.calls.append(("chat_completions_structured", model, cast("list[LlmInputItem]", messages)))
        self.structured_schemas.append(schema)
        return self._responses.pop(0)

    def extract_text(self, response: object) -> str:
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str):
            return output_text

        choices = getattr(response, "choices", None)
        if not isinstance(choices, list) or not choices:
            msg = "LLM response did not include choices"
            raise StructuredLlmResponseError(msg, suggestion=msg)

        message = getattr(choices[0], "message", None)
        content = None if message is None else getattr(message, "content", None)
        if not isinstance(content, str):
            msg = "LLM response is missing content"
            raise StructuredLlmResponseError(msg, suggestion=msg)
        return content

    def extract_usage(self, response: object) -> LlmUsage | None:
        usage = getattr(response, "usage", None)
        if usage is None:
            return None

        input_tokens = getattr(usage, "input_tokens", None)
        output_tokens = getattr(usage, "output_tokens", None)
        if isinstance(input_tokens, int) or isinstance(output_tokens, int):
            return LlmUsage(
                input_tokens=input_tokens if isinstance(input_tokens, int) else None,
                output_tokens=output_tokens if isinstance(output_tokens, int) else None,
                total_tokens=getattr(usage, "total_tokens", None)
                if isinstance(getattr(usage, "total_tokens", None), int)
                else None,
            )

        prompt_tokens = getattr(usage, "prompt_tokens", None)
        completion_tokens = getattr(usage, "completion_tokens", None)
        total_tokens = getattr(usage, "total_tokens", None)
        return LlmUsage(
            input_tokens=prompt_tokens if isinstance(prompt_tokens, int) else None,
            output_tokens=completion_tokens if isinstance(completion_tokens, int) else None,
            total_tokens=total_tokens if isinstance(total_tokens, int) else None,
        )

    def submit_text_batch(self, *, model: str, requests: list[LlmBatchRequestItem]) -> LlmBatchSubmission:
        del model, requests
        msg = "Batch API not expected in this test"
        raise AssertionError(msg)

    def submit_structured_batch(
        self,
        *,
        model: str,
        requests: list[LlmBatchRequestItem],
        json_schema_name: str,
        schema: JsonSchema,
    ) -> LlmBatchSubmission:
        del model, requests, json_schema_name, schema
        msg = "Batch API not expected in this test"
        raise AssertionError(msg)

    def get_batch_status(self, *, batch_id: str) -> LlmBatchStatus:
        del batch_id
        msg = "Batch API not expected in this test"
        raise AssertionError(msg)

    def cancel_batch(self, *, batch_id: str) -> LlmBatchStatus:
        del batch_id
        msg = "Batch API not expected in this test"
        raise AssertionError(msg)

    def get_text_batch_result(self, *, batch_id: str) -> LlmBatchTextResult:
        del batch_id
        msg = "Batch API not expected in this test"
        raise AssertionError(msg)

    def get_structured_batch_result(self, *, batch_id: str) -> LlmBatchStructuredResult:
        del batch_id
        msg = "Batch API not expected in this test"
        raise AssertionError(msg)


class _ExampleStructuredPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


class _StubDebugJsonWriter:
    def __init__(self) -> None:
        self.calls: list[tuple[str, JsonValue]] = []

    def write_json(self, *, label: str, payload: JsonValue) -> Path:
        self.calls.append((label, payload))
        return Path(f"debug/{label}.json")


class _FailingDebugJsonWriter:
    def __init__(self, exception: Exception) -> None:
        self._exception = exception
        self.calls: list[tuple[str, JsonValue]] = []

    def write_json(self, *, label: str, payload: JsonValue) -> Path:
        self.calls.append((label, payload))
        raise self._exception


def _build_adapter(
    responses: list[object],
    *,
    debug_json_writer: _StubDebugJsonWriter | _FailingDebugJsonWriter | None = None,
    debug_json_enabled: bool = False,
) -> tuple[LlmAdapter, _StubClient]:
    """Build an adapter with a stub client for one test scenario."""
    client = _StubClient(responses)
    adapter = LlmAdapter(
        client=client,
        model="gpt-test",
        debug_json_writer=debug_json_writer,
        debug_json_enabled=debug_json_enabled,
    )
    return adapter, client


def _find_record(caplog: pytest.LogCaptureFixture, prefix: str) -> logging.LogRecord:
    """Return the first captured record whose message starts with the prefix."""
    return next(record for record in caplog.records if record.getMessage().startswith(prefix))


def _record_extra(record: logging.LogRecord) -> _StructuredLogRecord:
    """Return a log record cast for structured ``extra`` attribute assertions."""
    return cast("_StructuredLogRecord", record)
