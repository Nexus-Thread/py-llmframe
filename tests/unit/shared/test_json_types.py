"""Tests for shared JSON type exports."""

from llmframe.shared import JsonArray, JsonObject, JsonScalar, JsonValue


def test_exports_shared_json_type_aliases() -> None:
    """Expose the shared JSON-compatible type aliases at package level."""
    assert JsonScalar is not None
    assert JsonArray is not None
    assert JsonObject is not None
    assert JsonValue is not None
