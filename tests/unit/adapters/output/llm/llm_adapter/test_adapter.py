"""Unit tests for the shared LLM adapter."""

from __future__ import annotations

import json
import logging
from typing import cast

import pytest
from pydantic import BaseModel, ConfigDict, Field

from llmframe.adapters.output.llm.llm_adapter import (
    LlmTextCompletionResult,
    StructuredLlmError,
    StructuredLlmInvalidJsonError,
    StructuredLlmJsonCompletionResult,
    StructuredLlmResponseError,
)
from llmframe.application.ports import LlmUsage

from ._support import (
    EXPECTED_INPUTS,
    LOGGER_NAME,
    _build_adapter,
    _Choice,
    _ExampleStructuredPayload,
    _FailingDebugJsonWriter,
    _find_record,
    _Message,
    _record_extra,
    _Response,
    _ResponsesApiResponse,
    _StubDebugJsonWriter,
    _Usage,
)


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
            EXPECTED_INPUTS,
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
    request_record_any = _record_extra(request_record)
    response_record_any = _record_extra(response_record)
    parsed_record_any = _record_extra(parsed_record)

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
    request_record_any = _record_extra(request_record)
    response_record_any = _record_extra(response_record)
    parsed_record_any = _record_extra(parsed_record)

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

    request_record = next(
        record for record in written_records if _record_extra(record).debug_label == "request_payload"
    )
    request_record_any = _record_extra(request_record)
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
    nested_schema = cast("dict[str, object]", cast("dict[str, object]", schema["$defs"])["_NestedPayload"])
    assert nested_schema["additionalProperties"] is False
    assert "internal_note" not in cast("dict[str, object]", nested_schema["properties"])
    nested_ref = cast("dict[str, object]", cast("dict[str, object]", schema["properties"])["nested"])
    assert nested_ref == {"$ref": "#/$defs/_NestedPayload"}


def test_extract_json_uses_responses_api_for_structured_output() -> None:
    """Adapter uses the Responses API structured-output surface."""
    adapter, client = _build_adapter([_ResponsesApiResponse(output_text='{"ok": true}')])

    result = adapter.extract_json(
        developer_prompt="developer", user_prompt="user", response_schema=_ExampleStructuredPayload
    )

    assert result.payload == {"ok": True}
    assert client.calls == [
        (
            "responses_structured",
            "gpt-test",
            EXPECTED_INPUTS,
        )
    ]


def test_extract_json_logs_responses_api_surface_metadata(caplog: pytest.LogCaptureFixture) -> None:
    """Adapter logs the fixed Responses API surface in metadata."""
    response = _ResponsesApiResponse(output_text='{"ok": true}')
    adapter, _ = _build_adapter([response])

    with caplog.at_level(logging.DEBUG, logger=LOGGER_NAME):
        result = adapter.extract_json(
            developer_prompt="developer", user_prompt="user", response_schema=_ExampleStructuredPayload
        )

    assert result.payload == {"ok": True}
    request_record = _find_record(caplog, "LLM request payload")
    request_record_any = _record_extra(request_record)
    assert request_record_any.api_surface == "responses"
    assert request_record_any.payload_keys == ["input", "model", "reasoning", "temperature", "text"]


def test_generate_text_returns_result_object_and_uses_response_surface() -> None:
    """Text completions use the Responses API plain-text surface."""
    adapter, client = _build_adapter([_ResponsesApiResponse(output_text="hello")])

    result = adapter.generate_text(developer_prompt="developer", user_prompt="user", reasoning_effort="low")

    assert result == LlmTextCompletionResult(content="hello", usage=None)
    assert client.calls == [
        (
            "responses_plain",
            "gpt-test",
            EXPECTED_INPUTS,
        )
    ]


def test_generate_text_returns_named_result_object() -> None:
    """Text completions return content and usage through a result DTO."""
    adapter, _ = _build_adapter(
        [
            _ResponsesApiResponse(
                output_text="hello",
                usage=_Usage(prompt_tokens=11, completion_tokens=7, total_tokens=18),
            )
        ]
    )

    result = adapter.generate_text(developer_prompt="developer", user_prompt="user")

    assert result == LlmTextCompletionResult(
        content="hello",
        usage=LlmUsage(input_tokens=11, output_tokens=7, total_tokens=18),
    )


def test_generate_text_logs_request_payload_omitting_none_options(caplog: pytest.LogCaptureFixture) -> None:
    """Text request logging omits optional fields delegated as ``None`` to transport."""
    adapter, _ = _build_adapter([_ResponsesApiResponse(output_text="hello")])

    with caplog.at_level(logging.DEBUG, logger=LOGGER_NAME):
        result = adapter.generate_text(developer_prompt="developer", user_prompt="user")

    assert result == LlmTextCompletionResult(content="hello", usage=None)
    request_record_any = _record_extra(_find_record(caplog, "LLM request payload"))
    assert request_record_any.api_surface == "responses"
    assert request_record_any.payload_keys == ["input", "model", "text"]


def test_generate_text_logs_request_payload_including_configured_options(caplog: pytest.LogCaptureFixture) -> None:
    """Text request logging includes optional fields when explicitly configured."""
    adapter, _ = _build_adapter([_ResponsesApiResponse(output_text="hello")])

    with caplog.at_level(logging.DEBUG, logger=LOGGER_NAME):
        result = adapter.generate_text(
            developer_prompt="developer",
            user_prompt="user",
            temperature=0.2,
            reasoning_effort="low",
        )

    assert result == LlmTextCompletionResult(content="hello", usage=None)
    request_record_any = _record_extra(_find_record(caplog, "LLM request payload"))
    assert request_record_any.payload_keys == ["input", "model", "reasoning", "temperature", "text"]
