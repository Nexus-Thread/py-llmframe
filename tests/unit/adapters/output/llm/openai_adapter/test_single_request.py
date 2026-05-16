"""Unit tests for OpenAI provider single-request façade behavior."""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from llmframe.adapters.output.llm.llm_adapter.exceptions import StructuredLlmResponseError
from llmframe.adapters.output.llm.providers.openai.provider_adapter import OpenAIProviderAdapter
from llmframe.application.ports import LlmUsage

if TYPE_CHECKING:
    from llmframe.adapters.output.llm.providers.openai.transport import OpenAIClientProtocol
    from llmframe.application.ports.llm_provider import JsonSchema, LlmInputItem
    from llmframe.shared.json_types import JsonValue


TEXT_INPUT_ITEMS: list[LlmInputItem] = [{"role": "user", "content": "hello"}]
STRUCTURED_SCHEMA: JsonSchema = {
    "type": "object",
    "properties": {"ok": {"type": "boolean"}},
    "required": ["ok"],
}
PROMPT_TOKENS = 2
COMPLETION_TOKENS = 3
TOTAL_TOKENS = 5


@dataclass(frozen=True)
class _CreateResponseCall:
    model: str
    input_items: list[LlmInputItem]
    temperature: float | None
    reasoning_effort: str | None


@dataclass(frozen=True)
class _CreateStructuredResponseCall:
    model: str
    input_items: list[LlmInputItem]
    json_schema_name: str
    schema: dict[str, JsonValue]
    temperature: float | None
    reasoning_effort: str | None


@dataclass(frozen=True)
class _Usage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass(frozen=True)
class _Response:
    output_text: str
    usage: _Usage | None = None


class _StubTransport:
    """Minimal transport stub for provider single-request tests."""

    def __init__(self) -> None:
        self.response = object()
        self.structured_response = object()
        self.create_response_calls: list[_CreateResponseCall] = []
        self.create_structured_response_calls: list[_CreateStructuredResponseCall] = []

    def create_response(
        self,
        *,
        model: str,
        input_items: list[LlmInputItem],
        temperature: float | None = None,
        reasoning_effort: str | None = None,
    ) -> object:
        self.create_response_calls.append(
            _CreateResponseCall(
                model=model,
                input_items=input_items,
                temperature=temperature,
                reasoning_effort=reasoning_effort,
            )
        )
        return self.response

    def create_structured_response(  # noqa: PLR0913
        self,
        *,
        model: str,
        input_items: list[LlmInputItem],
        json_schema_name: str,
        schema: dict[str, JsonValue],
        temperature: float | None = None,
        reasoning_effort: str | None = None,
    ) -> object:
        self.create_structured_response_calls.append(
            _CreateStructuredResponseCall(
                model=model,
                input_items=input_items,
                json_schema_name=json_schema_name,
                schema=schema,
                temperature=temperature,
                reasoning_effort=reasoning_effort,
            )
        )
        return self.structured_response


def _build_provider_and_transport() -> tuple[OpenAIProviderAdapter, _StubTransport]:
    """Build the provider façade with an observable transport stub."""
    transport = _StubTransport()
    return OpenAIProviderAdapter(transport=cast("OpenAIClientProtocol", transport)), transport


def test_create_response_forwards_single_request_options_to_transport() -> None:
    """Provider forwards plain Responses API options without altering caller inputs."""
    provider, transport = _build_provider_and_transport()

    response = provider.create_response(
        model="gpt-test",
        input_items=TEXT_INPUT_ITEMS,
        temperature=0.4,
        reasoning_effort="low",
    )

    assert response is transport.response
    assert transport.create_response_calls == [
        _CreateResponseCall(
            model="gpt-test",
            input_items=TEXT_INPUT_ITEMS,
            temperature=0.4,
            reasoning_effort="low",
        )
    ]


def test_create_structured_response_forwards_schema_options_to_transport() -> None:
    """Provider forwards structured Responses API options to the transport boundary."""
    provider, transport = _build_provider_and_transport()

    response = provider.create_structured_response(
        model="gpt-test",
        input_items=TEXT_INPUT_ITEMS,
        json_schema_name="ExampleSchema",
        schema=STRUCTURED_SCHEMA,
        temperature=0.1,
        reasoning_effort="medium",
    )

    assert response is transport.structured_response
    assert transport.create_structured_response_calls == [
        _CreateStructuredResponseCall(
            model="gpt-test",
            input_items=TEXT_INPUT_ITEMS,
            json_schema_name="ExampleSchema",
            schema=STRUCTURED_SCHEMA,
            temperature=0.1,
            reasoning_effort="medium",
        )
    ]


def test_extract_text_translates_invalid_provider_content_shape() -> None:
    """Provider exposes parser shape failures as the adapter response error type."""
    provider, _ = _build_provider_and_transport()

    with pytest.raises(StructuredLlmResponseError, match="missing content or has an invalid shape") as exc_info:
        provider.extract_text({"choices": []})

    assert "choices" in str(exc_info.value.suggestion)


@pytest.mark.parametrize(
    ("response", "suggestion_fragment"),
    [
        (
            SimpleNamespace(choices=[SimpleNamespace(message=None)]),
            "message",
        ),
        (
            SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=None))]),
            "content",
        ),
        (
            SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=[{"type": "output_image"}]))]),
            "supported text shape",
        ),
    ],
)
def test_extract_text_translates_provider_parser_errors_with_original_suggestion(
    *,
    response: object,
    suggestion_fragment: str,
) -> None:
    """Provider preserves parser details while translating response-shape failures."""
    provider, _ = _build_provider_and_transport()

    with pytest.raises(StructuredLlmResponseError, match="missing content or has an invalid shape") as exc_info:
        provider.extract_text(response)

    assert suggestion_fragment in str(exc_info.value.suggestion)


def test_extract_text_returns_responses_api_output_text() -> None:
    """Provider extracts plain text from Responses API response objects."""
    provider, _ = _build_provider_and_transport()

    assert provider.extract_text(_Response(output_text="hello")) == "hello"


def test_extract_usage_returns_normalized_provider_usage() -> None:
    """Provider maps provider token usage into the application usage DTO."""
    provider, _ = _build_provider_and_transport()
    response = _Response(
        output_text="hello",
        usage=_Usage(
            prompt_tokens=PROMPT_TOKENS,
            completion_tokens=COMPLETION_TOKENS,
            total_tokens=TOTAL_TOKENS,
        ),
    )

    assert provider.extract_usage(response) == LlmUsage(
        input_tokens=PROMPT_TOKENS,
        output_tokens=COMPLETION_TOKENS,
        total_tokens=TOTAL_TOKENS,
    )
