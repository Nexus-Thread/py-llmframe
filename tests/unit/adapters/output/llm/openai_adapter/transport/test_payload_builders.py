"""Unit tests for OpenAI transport payload builders."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from llmframe.adapters.output.llm.providers.openai.transport.payload_builders import (
    OpenAIRequestConfigError,
    build_reasoning_config,
    build_structured_response_request_payload,
    build_structured_schema_definition,
    build_text_response_request_payload,
)

INPUT_ITEMS: list[dict[str, object]] = [{"role": "user", "content": "hello"}]
JSON_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {"ok": {"type": "boolean"}},
}


def test_build_structured_schema_definition_requires_schema_name() -> None:
    """Structured output schema builder fails fast when the schema name is missing."""
    with pytest.raises(OpenAIRequestConfigError, match="json_schema_name"):
        build_structured_schema_definition(json_schema_name=None, json_schema=JSON_SCHEMA)


def test_build_structured_schema_definition_requires_schema_body() -> None:
    """Structured output schema builder fails fast when the schema body is missing."""
    with pytest.raises(OpenAIRequestConfigError, match="json_schema"):
        build_structured_schema_definition(json_schema_name="ExampleSchema", json_schema=None)


def test_build_reasoning_config_rejects_unknown_reasoning_effort() -> None:
    """Reasoning config builder rejects unsupported provider reasoning values."""
    with pytest.raises(ValidationError, match="effort"):
        build_reasoning_config("extreme")  # type: ignore[arg-type]


def test_build_text_response_request_payload_serializes_wire_shape() -> None:
    """Text response payload builder emits the expected Responses API wire format."""
    payload = build_text_response_request_payload(
        model="gpt-test",
        input_items=INPUT_ITEMS,
        temperature=0.2,
        reasoning_effort="low",
    )

    assert payload == {
        "model": "gpt-test",
        "input": INPUT_ITEMS,
        "text": {"format": {"type": "text"}},
        "temperature": 0.2,
        "reasoning": {"effort": "low"},
    }


def test_build_structured_response_request_payload_serializes_json_schema_wire_shape() -> None:
    """Structured response payload builder emits strict JSON Schema text format."""
    structured_schema = build_structured_schema_definition(
        json_schema_name="ExampleSchema",
        json_schema=JSON_SCHEMA,
    )

    payload = build_structured_response_request_payload(
        model="gpt-test",
        input_items=INPUT_ITEMS,
        structured_schema=structured_schema,
        temperature=None,
        reasoning_effort=None,
    )

    assert payload == {
        "model": "gpt-test",
        "input": INPUT_ITEMS,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "ExampleSchema",
                "strict": True,
                "schema": JSON_SCHEMA,
            }
        },
    }
