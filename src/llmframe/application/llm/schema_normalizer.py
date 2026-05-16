"""Schema normalization for structured LLM outputs."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from pydantic import BaseModel


def schema_name(schema_model: type[BaseModel]) -> str:
    """Return the provider schema name for a Pydantic model."""
    return schema_model.__name__


def build_response_schema(schema_model: type[BaseModel]) -> dict[str, object]:
    """Build a provider-ready schema from a Pydantic model schema."""
    raw_schema = cast("dict[str, object]", schema_model.model_json_schema())
    return cast("dict[str, object]", normalize_schema_node(raw_schema))


def normalize_schema_properties(properties: dict[object, object]) -> dict[str, object]:
    """Normalize object properties and drop fields marked as internal."""
    normalized_properties: dict[str, object] = {}
    for field_name, field_schema in properties.items():
        if isinstance(field_schema, dict) and field_schema.get("internal") is True:
            continue
        normalized_properties[str(field_name)] = normalize_schema_node(field_schema)
    return normalized_properties


def finalize_normalized_schema_object(normalized: dict[str, object]) -> dict[str, object]:
    """Close object schemas while preserving pure references."""
    if "$ref" in normalized:
        return {"$ref": normalized["$ref"]}

    properties = normalized.get("properties")
    if isinstance(properties, dict):
        normalized["additionalProperties"] = False
        required_fields = normalized.get("required")
        if isinstance(required_fields, list):
            normalized["required"] = [field_name for field_name in required_fields if field_name in properties]
    return normalized


def normalize_schema_node(node: object) -> object:
    """Recursively normalize a JSON-schema node for strict structured outputs."""
    if isinstance(node, list):
        return [normalize_schema_node(item) for item in node]
    if not isinstance(node, dict):
        return node

    normalized: dict[str, object] = {}
    for key, value in node.items():
        if key == "properties" and isinstance(value, dict):
            normalized[key] = normalize_schema_properties(value)
            continue
        normalized[key] = normalize_schema_node(value)
    return finalize_normalized_schema_object(normalized)
