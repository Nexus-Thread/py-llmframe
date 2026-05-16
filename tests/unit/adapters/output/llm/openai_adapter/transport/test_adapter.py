"""Unit tests for shared OpenAI transport request shapes."""

from __future__ import annotations

from typing import cast

import pytest

from llmframe.adapters.output.llm.providers.openai.transport import OpenAIClient
from tests.unit.adapters.output.llm.openai_adapter.transport._support import (
    TEST_JSON_SCHEMA,
    TEST_MODEL,
    TEST_SCHEMA_NAME,
    TEST_USER_MESSAGE,
    _build_client,
    _StubDebugJsonWriter,
)


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
