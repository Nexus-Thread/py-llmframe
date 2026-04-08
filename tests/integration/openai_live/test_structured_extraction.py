"""Live integration test for structured JSON extraction."""

from __future__ import annotations

from .helpers import PYTEST_MARKS, TinyStructuredResponse, build_live_adapter

pytestmark = PYTEST_MARKS


def test_extract_json_live_returns_tiny_payload() -> None:
    """The public adapter returns a minimal structured JSON payload from the live provider."""
    adapter, _ = build_live_adapter()

    result = adapter.extract_json(
        developer_prompt="Return JSON only.",
        user_prompt='Return an object with exactly one field: {"ok": true}.',
        response_schema=TinyStructuredResponse,
    )

    assert result.payload == {"ok": True}
    assert result.usage is not None
    assert result.usage.total_tokens is None or result.usage.total_tokens > 0
