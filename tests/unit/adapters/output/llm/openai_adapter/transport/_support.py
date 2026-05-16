"""Local support objects for OpenAI transport adapter tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias, cast

import httpx
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


def _build_client(  # noqa: PLR0913
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
