"""Unit tests for structured-output parsing and schema normalization helpers."""

from __future__ import annotations

from typing import cast

import pytest
from pydantic import BaseModel, ConfigDict, Field

from llmframe.adapters.output.llm.llm_adapter.exceptions import StructuredLlmInvalidJsonError
from llmframe.adapters.output.llm.llm_adapter.response_parser import parse_json_object
from llmframe.adapters.output.llm.llm_adapter.schema_normalizer import (
    build_response_schema,
    normalize_schema_node,
    normalize_schema_properties,
    schema_name,
)


class _NestedPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    public_note: str
    internal_note: str = Field(description="internal only", json_schema_extra={"internal": True})


class _StructuredPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    nested: _NestedPayload


@pytest.mark.parametrize(
    "content",
    [
        "{not-json",
        "",
    ],
)
def test_parse_json_object_rejects_invalid_json(content: str) -> None:
    with pytest.raises(StructuredLlmInvalidJsonError, match="invalid JSON payload") as exc_info:
        parse_json_object(content)

    assert exc_info.value.suggestion == "Inspect the model output and prompts"


@pytest.mark.parametrize(
    "content",
    [
        "[]",
        '"text"',
        "42",
        "null",
    ],
)
def test_parse_json_object_rejects_non_object_payloads(content: str) -> None:
    with pytest.raises(StructuredLlmInvalidJsonError, match="JSON object") as exc_info:
        parse_json_object(content)

    assert exc_info.value.suggestion == "Ensure the prompt requests a top-level JSON object"


def test_parse_json_object_accepts_nested_object_payload() -> None:
    result = parse_json_object('{"ok": true, "items": [{"name": "alpha"}], "count": 2}')

    assert result == {"ok": True, "items": [{"name": "alpha"}], "count": 2}


def test_schema_name_uses_pydantic_model_class_name() -> None:
    assert schema_name(_StructuredPayload) == "_StructuredPayload"


def test_normalize_schema_properties_drops_internal_fields_and_stringifies_keys() -> None:
    result = normalize_schema_properties(
        {
            "public": {"type": "string"},
            "secret": {"type": "string", "internal": True},
            123: {"type": "integer"},
        }
    )

    assert result == {
        "public": {"type": "string"},
        "123": {"type": "integer"},
    }


def test_normalize_schema_node_preserves_pure_reference_nodes() -> None:
    result = normalize_schema_node({"$ref": "#/$defs/Nested", "description": "ignored near ref"})

    assert result == {"$ref": "#/$defs/Nested"}


def test_normalize_schema_node_recurses_through_lists_and_preserves_scalars() -> None:
    schema = {
        "anyOf": [
            {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok", "missing"]},
            "literal-value",
        ],
        "default": None,
    }

    result = normalize_schema_node(schema)

    assert result == {
        "anyOf": [
            {
                "type": "object",
                "properties": {"ok": {"type": "boolean"}},
                "required": ["ok"],
                "additionalProperties": False,
            },
            "literal-value",
        ],
        "default": None,
    }


def test_build_response_schema_closes_nested_objects_and_prunes_internal_required_fields() -> None:
    schema = build_response_schema(_StructuredPayload)

    assert schema["additionalProperties"] is False
    assert schema["required"] == ["ok", "nested"]

    defs = cast("dict[str, object]", schema["$defs"])
    nested_schema = cast("dict[str, object]", defs["_NestedPayload"])
    nested_properties = cast("dict[str, object]", nested_schema["properties"])

    assert nested_schema["additionalProperties"] is False
    assert nested_schema["required"] == ["public_note"]
    assert "internal_note" not in nested_properties
    assert cast("dict[str, object]", cast("dict[str, object]", schema["properties"])["nested"]) == {
        "$ref": "#/$defs/_NestedPayload"
    }
