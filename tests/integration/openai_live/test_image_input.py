"""Live integration test for tiny multimodal image input."""

from __future__ import annotations

from llmframe import LlmImageUrlInputPart, LlmTextInputPart

from .helpers import PYTEST_MARKS, TINY_PNG_DATA_URL, build_live_adapter

pytestmark = PYTEST_MARKS


def test_generate_text_from_input_live_accepts_tiny_image() -> None:
    """The public adapter accepts a tiny inline image and returns a tiny response."""
    adapter, _ = build_live_adapter()

    result = adapter.generate_text_from_input(
        developer_prompt="Reply with exactly OK when the request includes an image input.",
        user_input_parts=[
            LlmTextInputPart(text="Return OK."),
            LlmImageUrlInputPart(url=TINY_PNG_DATA_URL),
        ],
        temperature=0,
    )

    assert result.content.strip() == "OK"
    assert result.usage is not None
    assert result.usage.total_tokens is None or result.usage.total_tokens > 0
