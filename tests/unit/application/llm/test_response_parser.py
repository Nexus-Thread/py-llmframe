"""Unit tests for application-owned structured-output parsing."""

from __future__ import annotations

import pytest

from llmframe.application.exceptions import StructuredLlmInvalidJsonError
from llmframe.application.llm import parse_json_object


def test_parse_json_object_returns_top_level_object() -> None:
    """Parser returns valid top-level JSON objects."""
    assert parse_json_object('{"ok": true}') == {"ok": True}


@pytest.mark.parametrize("content", ["[]", '"value"', "1", "true"])
def test_parse_json_object_rejects_non_object_payloads(content: str) -> None:
    """Parser rejects arrays and scalars because callers expect objects."""
    with pytest.raises(StructuredLlmInvalidJsonError, match="JSON object"):
        parse_json_object(content)


def test_parse_json_object_rejects_malformed_json() -> None:
    """Parser raises an application exception for malformed JSON."""
    with pytest.raises(StructuredLlmInvalidJsonError, match="invalid JSON"):
        parse_json_object("{not-json")
