"""Tests for shared JSON type exports."""

from llmframe import shared
from llmframe.shared import json_types


def test_exports_shared_json_type_aliases() -> None:
    """Expose the shared JSON-compatible type aliases at package level."""
    assert shared.JsonScalar is json_types.JsonScalar
    assert shared.JsonArray is json_types.JsonArray
    assert shared.JsonObject is json_types.JsonObject
    assert shared.JsonValue is json_types.JsonValue
