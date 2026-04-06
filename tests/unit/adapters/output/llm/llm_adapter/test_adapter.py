"""Unit tests for the shared LLM adapter."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pytest
from pydantic import BaseModel, ConfigDict, Field

from llmframe.adapters.output.llm.llm_adapter import (
    LlmAdapter,
    LlmTextCompletionResult,
    StructuredLlmError,
    StructuredLlmInvalidJsonError,
    StructuredLlmJsonCompletionResult,
    StructuredLlmResponseError,
)
from llmframe.application.ports import LlmUsage

LOGGER_NAME = "llmframe.adapters.output.llm.llm_adapter.adapter"

if TYPE_CHECKING:
    from collections.abc import Mapping as MappingType

    from llmframe.application.ports.llm_provider import JsonSchema
    from llmframe.shared.json_types import JsonValue


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


class _StubClient:
    """Stub provider implementation for LLM adapter tests."""

    def __init__(self, responses: list[object]) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, str, list[dict[str, str]]]] = []
        self.structured_schemas: list[MappingType[str, object]] = []

    def create_response(
        self,
        *,
        model: str,
        input_items: list[dict[str, str]],
        temperature: float | None = None,
        reasoning_effort: str | None = None,
    ) -> object:
        del temperature, reasoning_effort
        self.calls.append(("responses_plain", model, input_items))
        return self._responses.pop(0)

    def create_structured_response(
        self,
        *,
        model: str,
        input_items: list[dict[str, str]],
        json_schema_name: str,
        schema: JsonSchema,
        temperature: float | None = None,
        reasoning_effort: str | None = None,
    ) -> object:
        del temperature, reasoning_effort, json_schema_name
        self.calls.append(("responses_structured", model, input_items))
        self.structured_schemas.append(schema)
        return self._responses.pop(0)

    def create_structured_chat_completion(
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
        self.calls.append(("chat_completions_structured", model, messages))
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


def test_extract_json_returns_payload_and_usage_and_formats_inputs() -> None:
    """Adapter returns parsed JSON result and sends expected inputs."""
    adapter, client = _build_adapter([_Response(choices=[_Choice(message=_Message(content='{"ok": true}'))])])

    result = adapter.extract_json(
        developer_prompt="developer", user_prompt="user", response_schema=_ExampleStructuredPayload
    )

    assert result == StructuredLlmJsonCompletionResult(
        payload={"ok": True},
        usage=None,
    )
    assert client.calls == [
        (
            "responses_structured",
            "gpt-test",
            [
                {"role": "developer", "content": "developer"},
                {"role": "user", "content": "user"},
            ],
        )
    ]


def test_extract_json_returns_payload_and_usage() -> None:
    """Adapter returns parsed payload plus response usage metadata."""
    adapter, _ = _build_adapter(
        [
            _Response(
                choices=[_Choice(message=_Message(content='{"ok": true}'))],
                usage=_Usage(prompt_tokens=11, completion_tokens=7, total_tokens=18),
            )
        ]
    )

    result = adapter.extract_json(
        developer_prompt="developer",
        user_prompt="user",
        response_schema=_ExampleStructuredPayload,
    )

    assert result == StructuredLlmJsonCompletionResult(
        payload={"ok": True},
        usage=LlmUsage(input_tokens=11, output_tokens=7, total_tokens=18),
    )


def test_extract_json_raises_on_invalid_json() -> None:
    """Adapter raises a shared invalid-JSON error."""
    adapter, _ = _build_adapter([_Response(choices=[_Choice(message=_Message(content="{not-json"))])])

    with pytest.raises(StructuredLlmInvalidJsonError, match="invalid JSON payload"):
        adapter.extract_json(
            developer_prompt="developer", user_prompt="user", response_schema=_ExampleStructuredPayload
        )


def test_extract_json_raises_when_payload_is_not_object() -> None:
    """Adapter requires a top-level JSON object payload."""
    adapter, _ = _build_adapter([_Response(choices=[_Choice(message=_Message(content="[]"))])])

    with pytest.raises(StructuredLlmInvalidJsonError, match="JSON object"):
        adapter.extract_json(
            developer_prompt="developer", user_prompt="user", response_schema=_ExampleStructuredPayload
        )


def test_extract_json_raises_when_message_content_missing() -> None:
    """Adapter raises a shared response-shape error."""
    adapter, _ = _build_adapter([_Response(choices=[_Choice(message=None)])])

    with pytest.raises(StructuredLlmResponseError, match="missing content"):
        adapter.extract_json(
            developer_prompt="developer", user_prompt="user", response_schema=_ExampleStructuredPayload
        )


def test_extract_json_logs_request_response_and_payload(caplog: pytest.LogCaptureFixture) -> None:
    """Adapter emits metadata-only debug logs for request lifecycle."""
    adapter, _ = _build_adapter([_Response(choices=[_Choice(message=_Message(content='{"ok": true}'))])])

    with caplog.at_level(logging.DEBUG, logger=LOGGER_NAME):
        result = adapter.extract_json(
            developer_prompt="developer", user_prompt="user", response_schema=_ExampleStructuredPayload
        )

    assert result.payload == {"ok": True}

    request_record = _find_record(caplog, "LLM request payload")
    response_record = _find_record(caplog, "LLM response content")
    parsed_record = _find_record(caplog, "LLM parsed JSON payload")
    request_record_any = cast("Any", request_record)
    response_record_any = cast("Any", response_record)
    parsed_record_any = cast("Any", parsed_record)

    assert request_record_any.model == "gpt-test"
    assert request_record_any.api_surface == "responses"
    assert request_record_any.debug_label == "request_payload"
    assert request_record_any.payload_preview_omitted is True
    assert request_record_any.payload_kind == "dict"
    assert request_record_any.payload_keys == ["input", "model", "reasoning", "temperature", "text"]
    assert response_record_any.debug_label == "response_text"
    assert response_record_any.payload_preview_omitted is True
    assert response_record_any.payload_kind == "text"
    assert parsed_record_any.debug_label == "parsed_response_payload"
    assert parsed_record_any.payload_preview_omitted is True
    assert parsed_record_any.payload_kind == "dict"
    assert parsed_record_any.payload_keys == ["ok"]
    assert "system" not in caplog.text
    assert '"ok": true' not in caplog.text


def test_extract_json_logs_payload_lengths_without_raw_content(caplog: pytest.LogCaptureFixture) -> None:
    """Adapter logs payload sizes without logging raw content."""
    long_text = "x" * 2_100_000
    content = json.dumps({"summary": long_text})
    adapter, _ = _build_adapter([_Response(choices=[_Choice(message=_Message(content=content))])])

    with caplog.at_level(logging.DEBUG, logger=LOGGER_NAME):
        result = adapter.extract_json(
            developer_prompt="developer", user_prompt=long_text, response_schema=_ExampleStructuredPayload
        )

    assert result.payload == {"summary": long_text}

    request_record = _find_record(caplog, "LLM request payload")
    response_record = _find_record(caplog, "LLM response content")
    parsed_record = _find_record(caplog, "LLM parsed JSON payload")
    request_record_any = cast("Any", request_record)
    response_record_any = cast("Any", response_record)
    parsed_record_any = cast("Any", parsed_record)

    assert request_record_any.payload_length > 2_000_000
    assert request_record_any.api_surface == "responses"
    assert response_record_any.payload_length > 2_000_000
    assert parsed_record_any.payload_length > 2_000_000
    assert request_record_any.payload_preview_omitted is True
    assert response_record_any.payload_preview_omitted is True
    assert parsed_record_any.payload_preview_omitted is True
    assert long_text not in caplog.text


def test_extract_json_writes_debug_files_when_enabled() -> None:
    """Adapter writes request/response/parsed payloads when debug is enabled."""
    debug_writer = _StubDebugJsonWriter()
    adapter, _ = _build_adapter(
        [_Response(choices=[_Choice(message=_Message(content='{"ok": true}'))])],
        debug_json_writer=debug_writer,
        debug_json_enabled=True,
    )

    result = adapter.extract_json(
        developer_prompt="developer", user_prompt="user", response_schema=_ExampleStructuredPayload
    )

    assert result.payload == {"ok": True}
    assert [label for label, _ in debug_writer.calls] == [
        "request_payload",
        "response_text",
        "parsed_response_payload",
    ]


def test_extract_json_skips_debug_files_when_disabled() -> None:
    """Adapter does not write debug files when debug is disabled."""
    debug_writer = _StubDebugJsonWriter()
    adapter, _ = _build_adapter(
        [_Response(choices=[_Choice(message=_Message(content='{"ok": true}'))])],
        debug_json_writer=debug_writer,
        debug_json_enabled=False,
    )

    result = adapter.extract_json(
        developer_prompt="developer", user_prompt="user", response_schema=_ExampleStructuredPayload
    )

    assert result.payload == {"ok": True}
    assert debug_writer.calls == []


def test_extract_json_continues_when_debug_write_fails(caplog: pytest.LogCaptureFixture) -> None:
    """Adapter continues when optional debug payload persistence fails."""
    debug_writer = _FailingDebugJsonWriter(OSError("disk full"))
    adapter, _ = _build_adapter(
        [_Response(choices=[_Choice(message=_Message(content='{"ok": true}'))])],
        debug_json_writer=debug_writer,
        debug_json_enabled=True,
    )

    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        result = adapter.extract_json(
            developer_prompt="developer", user_prompt="user", response_schema=_ExampleStructuredPayload
        )

    assert result.payload == {"ok": True}
    assert [label for label, _ in debug_writer.calls] == [
        "request_payload",
        "response_text",
        "parsed_response_payload",
    ]
    warning_messages = [record.getMessage() for record in caplog.records]
    assert warning_messages == [
        "Failed to write LLM debug payload",
        "Failed to write LLM debug payload",
        "Failed to write LLM debug payload",
    ]
    assert all(record.exc_info is not None for record in caplog.records)


def test_extract_json_logs_written_debug_file_as_structured_context(caplog: pytest.LogCaptureFixture) -> None:
    """Adapter logs written debug-file metadata via extra fields."""
    debug_writer = _StubDebugJsonWriter()
    adapter, _ = _build_adapter(
        [_Response(choices=[_Choice(message=_Message(content='{"ok": true}'))])],
        debug_json_writer=debug_writer,
        debug_json_enabled=True,
    )

    with caplog.at_level(logging.DEBUG, logger=LOGGER_NAME):
        result = adapter.extract_json(
            developer_prompt="developer", user_prompt="user", response_schema=_ExampleStructuredPayload
        )

    assert result.payload == {"ok": True}
    written_records = [record for record in caplog.records if record.getMessage() == "LLM debug payload written"]
    assert len(written_records) == 3

    request_record = next(record for record in written_records if cast("Any", record).debug_label == "request_payload")
    request_record_any = cast("Any", request_record)
    assert request_record_any.file_path == "debug/request_payload.json"
    assert request_record_any.model == "gpt-test"


def test_extract_json_raises_when_structured_outputs_schema_missing() -> None:
    """Structured outputs mode requires an explicit schema."""
    adapter, _ = _build_adapter([_Response(choices=[_Choice(message=_Message(content='{"ok": true}'))])])

    with pytest.raises(StructuredLlmError, match="require a response schema"):
        adapter.extract_json(developer_prompt="developer", user_prompt="user")


def test_build_response_schema_filters_internal_fields_and_closes_objects() -> None:
    """Schema normalization removes internal fields and closes object schemas."""

    class _NestedPayload(BaseModel):
        model_config = ConfigDict(extra="allow")

        ok: bool
        internal_note: str = Field(description="internal only", json_schema_extra={"internal": True})

    class _OuterPayload(BaseModel):
        model_config = ConfigDict(extra="forbid")

        nested: _NestedPayload

    adapter, client = _build_adapter([_Response(choices=[_Choice(message=_Message(content='{"ok": true}'))])])

    adapter.extract_json(
        developer_prompt="developer",
        user_prompt="user",
        response_schema=_OuterPayload,
    )

    schema = client.structured_schemas[0]

    assert schema["additionalProperties"] is False
    nested_schema = cast("dict[str, Any]", cast("dict[str, Any]", schema["$defs"])["_NestedPayload"])
    assert nested_schema["additionalProperties"] is False
    assert "internal_note" not in cast("dict[str, Any]", nested_schema["properties"])
    nested_ref = cast("dict[str, Any]", cast("dict[str, Any]", schema["properties"])["nested"])
    assert nested_ref == {"$ref": "#/$defs/_NestedPayload"}


def test_extract_json_uses_responses_api_for_structured_output() -> None:
    """Adapter uses the Responses API structured-output surface."""
    adapter, client = _build_adapter([type("ResponseObj", (), {"output_text": '{"ok": true}', "usage": None})()])

    result = adapter.extract_json(
        developer_prompt="developer", user_prompt="user", response_schema=_ExampleStructuredPayload
    )

    assert result.payload == {"ok": True}
    assert client.calls == [
        (
            "responses_structured",
            "gpt-test",
            [
                {"role": "developer", "content": "developer"},
                {"role": "user", "content": "user"},
            ],
        )
    ]


def test_extract_json_logs_responses_api_surface_metadata(caplog: pytest.LogCaptureFixture) -> None:
    """Adapter logs the fixed Responses API surface in metadata."""
    response = type("ResponseObj", (), {"output_text": '{"ok": true}', "usage": None})()
    adapter, _ = _build_adapter([response])

    with caplog.at_level(logging.DEBUG, logger=LOGGER_NAME):
        result = adapter.extract_json(
            developer_prompt="developer", user_prompt="user", response_schema=_ExampleStructuredPayload
        )

    assert result.payload == {"ok": True}
    request_record = _find_record(caplog, "LLM request payload")
    request_record_any = cast("Any", request_record)
    assert request_record_any.api_surface == "responses"
    assert request_record_any.payload_keys == ["input", "model", "reasoning", "temperature", "text"]


def test_generate_text_returns_result_object_and_uses_response_surface() -> None:
    """Text completions use the Responses API plain-text surface."""
    adapter, client = _build_adapter([type("ResponseObj", (), {"output_text": "hello", "usage": None})()])

    result = adapter.generate_text(developer_prompt="developer", user_prompt="user", reasoning_effort="low")

    assert result == LlmTextCompletionResult(content="hello", usage=None)
    assert client.calls == [
        (
            "responses_plain",
            "gpt-test",
            [
                {"role": "developer", "content": "developer"},
                {"role": "user", "content": "user"},
            ],
        )
    ]


def test_generate_text_returns_named_result_object() -> None:
    """Text completions return content and usage through a result DTO."""
    adapter, _ = _build_adapter(
        [
            type(
                "ResponseObj",
                (),
                {"output_text": "hello", "usage": _Usage(prompt_tokens=11, completion_tokens=7, total_tokens=18)},
            )()
        ]
    )

    result = adapter.generate_text(developer_prompt="developer", user_prompt="user")

    assert result == LlmTextCompletionResult(
        content="hello",
        usage=LlmUsage(input_tokens=11, output_tokens=7, total_tokens=18),
    )


def test_generate_text_logs_request_payload_omitting_none_options(caplog: pytest.LogCaptureFixture) -> None:
    """Text request logging omits optional fields delegated as ``None`` to transport."""
    adapter, _ = _build_adapter([type("ResponseObj", (), {"output_text": "hello", "usage": None})()])

    with caplog.at_level(logging.DEBUG, logger=LOGGER_NAME):
        result = adapter.generate_text(developer_prompt="developer", user_prompt="user")

    assert result == LlmTextCompletionResult(content="hello", usage=None)
    request_record_any = cast("Any", _find_record(caplog, "LLM request payload"))
    assert request_record_any.api_surface == "responses"
    assert request_record_any.payload_keys == ["input", "model", "text"]


def test_generate_text_logs_request_payload_including_configured_options(caplog: pytest.LogCaptureFixture) -> None:
    """Text request logging includes optional fields when explicitly configured."""
    adapter, _ = _build_adapter([type("ResponseObj", (), {"output_text": "hello", "usage": None})()])

    with caplog.at_level(logging.DEBUG, logger=LOGGER_NAME):
        result = adapter.generate_text(
            developer_prompt="developer",
            user_prompt="user",
            temperature=0.2,
            reasoning_effort="low",
        )

    assert result == LlmTextCompletionResult(content="hello", usage=None)
    request_record_any = cast("Any", _find_record(caplog, "LLM request payload"))
    assert request_record_any.payload_keys == ["input", "model", "reasoning", "temperature", "text"]
