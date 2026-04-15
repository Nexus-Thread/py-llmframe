"""Unit tests for shared OpenAI transport retry behavior."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias, cast

import httpx
import pytest
from openai import APIError

from llmframe.adapters.output.llm.providers.openai.transport import OpenAIClient

LOGGER_NAME = "llmframe.adapters.output.llm.providers.openai.transport.adapter"
TEST_MODEL = "gpt-test"
TEST_USER_MESSAGE: list[dict[str, object]] = [{"role": "user", "content": "hello"}]
JsonSchemaDict: TypeAlias = dict[str, object]
TEST_JSON_SCHEMA: JsonSchemaDict = {
    "type": "object",
    "properties": {"ok": {"type": "boolean"}},
    "required": ["ok"],
}
TEST_SCHEMA_NAME = "ExampleSchema"


class _StubDebugJsonWriter:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def write_json(self, *, label: str, payload: object) -> Path:
        self.calls.append((label, payload))
        return Path(f"debug/{label}.json")


@dataclass(frozen=True)
class _CreateCall:
    model: str
    messages: list[dict[str, str]]
    temperature: float | None
    response_format: dict[str, object] | None
    reasoning: dict[str, str] | None


@dataclass(frozen=True)
class _ResponsesCreateCall:
    model: str
    input: list[dict[str, object]]
    text: dict[str, object]
    temperature: float | None
    reasoning: dict[str, str] | None


class _StubCompletions:
    """Stub chat completions endpoint for deterministic transport tests."""

    def __init__(self, outcomes: list[object]) -> None:
        self._outcomes = list(outcomes)
        self.calls: list[_CreateCall] = []

    def create(self, **kwargs: object) -> object:
        self.calls.append(
            _CreateCall(
                model=cast("str", kwargs["model"]),
                messages=cast("list[dict[str, str]]", kwargs["messages"]),
                temperature=cast("float | None", kwargs.get("temperature")),
                response_format=cast("dict[str, object] | None", kwargs.get("response_format")),
                reasoning=cast("dict[str, str] | None", kwargs.get("reasoning")),
            )
        )
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class _StubResponses:
    """Stub responses endpoint for deterministic transport tests."""

    def __init__(self, outcomes: list[object]) -> None:
        self._outcomes = list(outcomes)
        self.calls: list[_ResponsesCreateCall] = []

    def create(self, **kwargs: object) -> object:
        self.calls.append(
            _ResponsesCreateCall(
                model=cast("str", kwargs["model"]),
                input=cast("list[dict[str, object]]", kwargs["input"]),
                text=cast("dict[str, object]", kwargs["text"]),
                temperature=cast("float | None", kwargs.get("temperature")),
                reasoning=cast("dict[str, str] | None", kwargs.get("reasoning")),
            )
        )
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


@dataclass
class _StubChatNamespace:
    completions: _StubCompletions


@dataclass
class _StubSdkClient:
    chat: _StubChatNamespace
    responses: _StubResponses


def _build_client(
    *,
    completion_outcomes: list[object] | None = None,
    response_outcomes: list[object] | None = None,
    max_retries: int,
    backoff_factor: float,
    sleeps: list[float],
    debug_json_writer: _StubDebugJsonWriter | None = None,
    debug_json_enabled: bool = False,
) -> tuple[OpenAIClient, _StubCompletions, _StubResponses]:
    completions = _StubCompletions(completion_outcomes or [])
    responses = _StubResponses(response_outcomes or [])
    sdk_client = _StubSdkClient(
        chat=_StubChatNamespace(completions=completions),
        responses=responses,
    )
    client = OpenAIClient(
        sdk_client=sdk_client,
        max_retries=max_retries,
        backoff_factor=backoff_factor,
        sleep=sleeps.append,
        debug_json_writer=debug_json_writer,
        debug_json_enabled=debug_json_enabled,
    )
    return client, completions, responses


def _api_error() -> APIError:
    request = httpx.Request("POST", "https://example.invalid/v1/chat/completions")
    return APIError("boom", request=request, body=None)


def test_create_json_chat_completion_passes_json_response_format() -> None:
    """Transport passes OpenAI JSON mode options to the SDK."""
    sleeps: list[float] = []
    expected_response = object()
    client, completions, _ = _build_client(
        completion_outcomes=[expected_response],
        max_retries=0,
        backoff_factor=2.0,
        sleeps=sleeps,
    )

    response = client.create_json_chat_completion(model=TEST_MODEL, messages=TEST_USER_MESSAGE)

    assert response is expected_response
    assert len(completions.calls) == 1
    assert completions.calls[0].temperature is None
    assert completions.calls[0].response_format == {"type": "json_object"}
    assert sleeps == []


def test_create_chat_completion_omits_response_format() -> None:
    """Transport sends plain chat completion options when JSON mode is not requested."""
    sleeps: list[float] = []
    expected_response = object()
    client, completions, _ = _build_client(
        completion_outcomes=[expected_response],
        max_retries=0,
        backoff_factor=2.0,
        sleeps=sleeps,
    )

    response = client.create_chat_completion(model=TEST_MODEL, messages=TEST_USER_MESSAGE)

    assert response is expected_response
    assert len(completions.calls) == 1
    assert completions.calls[0].temperature is None
    assert completions.calls[0].response_format is None
    assert sleeps == []


def test_create_chat_completion_omits_temperature_when_overridden_to_none() -> None:
    """Transport omits temperature when a chat-completion call overrides it to ``None``."""
    sleeps: list[float] = []
    expected_response = object()
    client, completions, _ = _build_client(
        completion_outcomes=[expected_response],
        max_retries=0,
        backoff_factor=2.0,
        sleeps=sleeps,
    )

    response = client.create_chat_completion(
        model=TEST_MODEL,
        messages=TEST_USER_MESSAGE,
        temperature=None,
    )

    assert response is expected_response
    assert completions.calls[0].temperature is None


def test_create_structured_response_passes_reasoning_effort_when_provided() -> None:
    """Transport includes per-call reasoning effort for Responses API requests."""
    sleeps: list[float] = []
    expected_response = object()
    client, _, responses = _build_client(
        response_outcomes=[expected_response],
        max_retries=0,
        backoff_factor=2.0,
        sleeps=sleeps,
    )

    response = client.create_structured_response(
        model=TEST_MODEL,
        input_items=TEST_USER_MESSAGE,
        json_schema_name=TEST_SCHEMA_NAME,
        schema=TEST_JSON_SCHEMA,
        reasoning_effort="low",
    )

    assert response is expected_response
    assert responses.calls[0].reasoning == {"effort": "low"}


def test_create_json_chat_completion_passes_reasoning_effort_when_provided() -> None:
    """Transport includes reasoning effort for chat-completions requests when provided."""
    sleeps: list[float] = []
    expected_response = object()
    client, completions, _ = _build_client(
        completion_outcomes=[expected_response],
        max_retries=0,
        backoff_factor=2.0,
        sleeps=sleeps,
    )

    response = client.create_json_chat_completion(
        model=TEST_MODEL,
        messages=TEST_USER_MESSAGE,
        reasoning_effort="medium",
    )

    assert response is expected_response
    assert completions.calls[0].reasoning == {"effort": "medium"}


def test_create_json_response_passes_temperature_when_provided() -> None:
    """Transport includes temperature for Responses API requests when provided."""
    sleeps: list[float] = []
    expected_response = object()
    client, _, responses = _build_client(
        response_outcomes=[expected_response],
        max_retries=0,
        backoff_factor=2.0,
        sleeps=sleeps,
    )

    response = client.create_json_response(
        model=TEST_MODEL,
        input_items=TEST_USER_MESSAGE,
        temperature=0.2,
    )

    assert response is expected_response
    assert responses.calls[0].temperature == 0.2


def test_create_response_passes_multimodal_input_items() -> None:
    """Transport forwards OpenAI Responses multimodal input content unchanged."""
    sleeps: list[float] = []
    expected_response = object()
    client, _, responses = _build_client(
        response_outcomes=[expected_response],
        max_retries=0,
        backoff_factor=2.0,
        sleeps=sleeps,
    )

    multimodal_input: list[dict[str, object]] = [
        {"role": "developer", "content": "developer"},
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "what is shown?"},
                {"type": "input_image", "image_url": "https://example.com/cat.png"},
            ],
        },
    ]

    response = client.create_response(model=TEST_MODEL, input_items=multimodal_input)

    assert response is expected_response
    assert responses.calls[0].input == multimodal_input


def test_create_chat_completion_retries_and_then_succeeds() -> None:
    """Transport retries API errors up to the configured retry count."""
    sleeps: list[float] = []
    expected_response = object()
    client, completions, _ = _build_client(
        completion_outcomes=[_api_error(), expected_response],
        max_retries=2,
        backoff_factor=3.0,
        sleeps=sleeps,
    )

    response = client.create_chat_completion(model=TEST_MODEL, messages=TEST_USER_MESSAGE)

    assert response is expected_response
    assert len(completions.calls) == 2
    assert sleeps == [3.0]


def test_create_chat_completion_logs_retry_metadata(caplog: pytest.LogCaptureFixture) -> None:
    """Transport logs actionable retry metadata for transient API failures."""
    sleeps: list[float] = []
    expected_response = object()
    client, _, _ = _build_client(
        completion_outcomes=[_api_error(), expected_response],
        max_retries=2,
        backoff_factor=3.0,
        sleeps=sleeps,
    )

    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        response = client.create_chat_completion(model=TEST_MODEL, messages=TEST_USER_MESSAGE)

    assert response is expected_response
    warning_record = caplog.records[0]
    assert warning_record.getMessage() == "OpenAI completion attempt failed; retrying"
    warning_record_any = cast("Any", warning_record)
    assert warning_record_any.attempt == 1
    assert warning_record_any.attempts_remaining == 2
    assert warning_record_any.total_attempts == 3
    assert warning_record_any.retry_delay_seconds == 3.0


def test_create_chat_completion_with_zero_retries_still_attempts_once() -> None:
    """Transport performs one initial request when retries are configured to zero."""
    sleeps: list[float] = []
    client, completions, _ = _build_client(
        completion_outcomes=[_api_error()],
        max_retries=0,
        backoff_factor=2.0,
        sleeps=sleeps,
    )

    with pytest.raises(APIError):
        client.create_chat_completion(model=TEST_MODEL, messages=TEST_USER_MESSAGE)

    assert len(completions.calls) == 1
    assert sleeps == []


def test_create_chat_completion_raises_after_exhausting_retries() -> None:
    """Transport raises APIError after all retry attempts are exhausted."""
    sleeps: list[float] = []
    client, completions, _ = _build_client(
        completion_outcomes=[_api_error(), _api_error(), _api_error()],
        max_retries=2,
        backoff_factor=2.0,
        sleeps=sleeps,
    )

    with pytest.raises(APIError):
        client.create_chat_completion(model=TEST_MODEL, messages=TEST_USER_MESSAGE)

    assert len(completions.calls) == 3
    assert sleeps == [2.0, 4.0]


def test_create_chat_completion_logs_final_exception_once(caplog: pytest.LogCaptureFixture) -> None:
    """Transport logs one final exception with retry context when exhausted."""
    sleeps: list[float] = []
    client, _, _ = _build_client(
        completion_outcomes=[_api_error(), _api_error()],
        max_retries=1,
        backoff_factor=2.0,
        sleeps=sleeps,
    )

    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME), pytest.raises(APIError):
        client.create_chat_completion(model=TEST_MODEL, messages=TEST_USER_MESSAGE)

    exception_record = next(record for record in caplog.records if record.levelno == logging.ERROR)
    assert exception_record.getMessage() == "OpenAI completion failed after exhausting retries"
    exception_record_any = cast("Any", exception_record)
    assert exception_record_any.attempt == 2
    assert exception_record_any.total_attempts == 2
    assert exception_record.exc_info is not None


def test_init_rejects_invalid_retry_configuration() -> None:
    """Transport validates retry and backoff constructor arguments."""
    with pytest.raises(ValueError, match="max_retries"):
        OpenAIClient(sdk_client=object(), max_retries=-1)

    with pytest.raises(ValueError, match="backoff_factor"):
        OpenAIClient(sdk_client=object(), backoff_factor=0.5)


def test_create_json_response_passes_responses_json_format() -> None:
    """Transport passes Responses API JSON mode options to the SDK."""
    sleeps: list[float] = []
    expected_response = object()
    client, _, responses = _build_client(
        response_outcomes=[expected_response],
        max_retries=0,
        backoff_factor=2.0,
        sleeps=sleeps,
    )

    response = client.create_json_response(model=TEST_MODEL, input_items=TEST_USER_MESSAGE)

    assert response is expected_response
    assert len(responses.calls) == 1
    assert responses.calls[0].input == TEST_USER_MESSAGE
    assert responses.calls[0].text == {"format": {"type": "json_object"}}
    assert sleeps == []


def test_create_json_response_retries_and_then_succeeds() -> None:
    """Responses API calls retry API errors up to the configured retry count."""
    sleeps: list[float] = []
    expected_response = object()
    client, _, responses = _build_client(
        response_outcomes=[_api_error(), expected_response],
        max_retries=2,
        backoff_factor=3.0,
        sleeps=sleeps,
    )

    response = client.create_json_response(model=TEST_MODEL, input_items=TEST_USER_MESSAGE)

    assert response is expected_response
    assert len(responses.calls) == 2
    assert sleeps == [3.0]


def test_create_response_passes_plain_text_format() -> None:
    """Transport passes plain Responses API text mode options to the SDK."""
    sleeps: list[float] = []
    expected_response = object()
    client, _, responses = _build_client(
        response_outcomes=[expected_response],
        max_retries=0,
        backoff_factor=2.0,
        sleeps=sleeps,
    )

    response = client.create_response(model=TEST_MODEL, input_items=TEST_USER_MESSAGE)

    assert response is expected_response
    assert responses.calls[0].text == {"format": {"type": "text"}}


def test_create_structured_chat_completion_passes_json_schema_response_format() -> None:
    """Transport passes Structured Outputs JSON Schema options to the SDK."""
    sleeps: list[float] = []
    expected_response = object()
    client, completions, _ = _build_client(
        completion_outcomes=[expected_response],
        max_retries=0,
        backoff_factor=2.0,
        sleeps=sleeps,
    )

    response = client.create_structured_chat_completion(
        model=TEST_MODEL,
        messages=TEST_USER_MESSAGE,
        json_schema_name=TEST_SCHEMA_NAME,
        schema=TEST_JSON_SCHEMA,
    )

    assert response is expected_response
    assert len(completions.calls) == 1
    assert completions.calls[0].response_format == {
        "type": "json_schema",
        "json_schema": {
            "name": TEST_SCHEMA_NAME,
            "strict": True,
            "schema": TEST_JSON_SCHEMA,
        },
    }


def test_create_structured_response_passes_json_schema_text_format() -> None:
    """Transport passes Structured Outputs JSON Schema options to the Responses API."""
    sleeps: list[float] = []
    expected_response = object()
    client, _, responses = _build_client(
        response_outcomes=[expected_response],
        max_retries=0,
        backoff_factor=2.0,
        sleeps=sleeps,
    )

    response = client.create_structured_response(
        model=TEST_MODEL,
        input_items=TEST_USER_MESSAGE,
        json_schema_name=TEST_SCHEMA_NAME,
        schema=TEST_JSON_SCHEMA,
    )

    assert response is expected_response
    assert responses.calls[0].text == {
        "format": {
            "type": "json_schema",
            "name": TEST_SCHEMA_NAME,
            "strict": True,
            "schema": TEST_JSON_SCHEMA,
        }
    }


def test_create_structured_chat_completion_requires_schema_name() -> None:
    """Transport fails fast when structured chat calls omit the schema name."""
    sleeps: list[float] = []
    client, completions, _ = _build_client(
        completion_outcomes=[object()],
        max_retries=0,
        backoff_factor=2.0,
        sleeps=sleeps,
    )

    with pytest.raises(ValueError, match="json_schema_name"):
        client.create_structured_chat_completion(
            model=TEST_MODEL,
            messages=TEST_USER_MESSAGE,
            json_schema_name=None,  # type: ignore[arg-type]
            schema={"type": "object"},
        )

    assert completions.calls == []


def test_create_structured_response_requires_schema_body() -> None:
    """Transport fails fast when structured response calls omit the schema body."""
    sleeps: list[float] = []
    client, _, responses = _build_client(
        response_outcomes=[object()],
        max_retries=0,
        backoff_factor=2.0,
        sleeps=sleeps,
    )

    with pytest.raises(ValueError, match="json_schema"):
        client.create_structured_response(
            model=TEST_MODEL,
            input_items=TEST_USER_MESSAGE,
            json_schema_name=TEST_SCHEMA_NAME,
            schema=None,  # type: ignore[arg-type]
        )

    assert responses.calls == []


def test_create_json_response_writes_consistent_debug_request_and_response_labels() -> None:
    """Transport writes stable request and response debug labels."""
    sleeps: list[float] = []
    expected_response = {"id": "resp_123", "output_text": "hello"}
    debug_writer = _StubDebugJsonWriter()
    client, _, _ = _build_client(
        response_outcomes=[expected_response],
        max_retries=0,
        backoff_factor=2.0,
        sleeps=sleeps,
        debug_json_writer=debug_writer,
        debug_json_enabled=True,
    )

    response = client.create_json_response(model=TEST_MODEL, input_items=TEST_USER_MESSAGE)

    assert response == expected_response
    assert [label for label, _ in debug_writer.calls] == ["request_payload", "response_payload"]
    assert cast("dict[str, object]", debug_writer.calls[0][1])["model"] == TEST_MODEL
    assert debug_writer.calls[1][1] == expected_response
