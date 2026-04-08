"""Live integration test for plain-text generation."""

from __future__ import annotations

import os

from .helpers import DEFAULT_MODEL, PYTEST_MARKS, build_live_adapter

pytestmark = PYTEST_MARKS


def test_generate_text_live_returns_tiny_response() -> None:
    """The public adapter returns a tiny plain-text response from the live provider."""
    adapter, model = build_live_adapter()

    result = adapter.generate_text(
        developer_prompt="Reply with exactly OK.",
        user_prompt="Return OK.",
        temperature=0,
    )

    assert result.content.strip() == "OK"
    assert result.usage is not None
    assert result.usage.total_tokens is None or result.usage.total_tokens > 0
    assert model == os.getenv("LLMFRAME_OPENAI_MODEL", DEFAULT_MODEL)
