"""Unit tests for shared OpenAI transport retry behavior."""

from __future__ import annotations

import logging
from typing import Any, cast

import pytest
from openai import APIError

from tests.unit.adapters.output.llm.openai_adapter.transport._support import (
    LOGGER_NAME,
    TEST_MODEL,
    TEST_USER_MESSAGE,
    _api_error,
    _build_client,
)

FIRST_RETRY_ATTEMPT = 1
TWO_ATTEMPTS = 2
THREE_ATTEMPTS = 3
INITIAL_RETRY_DELAY_SECONDS = 3.0


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
    assert len(completions.calls) == TWO_ATTEMPTS
    assert sleeps == [INITIAL_RETRY_DELAY_SECONDS]


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
    assert warning_record_any.attempt == FIRST_RETRY_ATTEMPT
    assert warning_record_any.attempts_remaining == TWO_ATTEMPTS
    assert warning_record_any.total_attempts == THREE_ATTEMPTS
    assert warning_record_any.retry_delay_seconds == INITIAL_RETRY_DELAY_SECONDS


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

    assert len(completions.calls) == THREE_ATTEMPTS
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
    assert exception_record_any.attempt == TWO_ATTEMPTS
    assert exception_record_any.total_attempts == TWO_ATTEMPTS
    assert exception_record.exc_info is not None


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
    assert len(responses.calls) == TWO_ATTEMPTS
    assert sleeps == [INITIAL_RETRY_DELAY_SECONDS]
