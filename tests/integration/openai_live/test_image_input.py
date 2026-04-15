"""Live integration test for tiny multimodal image input."""

from __future__ import annotations

import pytest

from llmframe import LlmImageUrlInputPart, LlmTextInputPart

from .helpers import PYTEST_MARKS, TINY_TEST_IMAGE_DATA_URL, TINY_TEST_IMAGE_URL, build_live_adapter

pytestmark = PYTEST_MARKS


@pytest.mark.parametrize(
    "image_url",
    [
        pytest.param(TINY_TEST_IMAGE_URL, id="hosted_url"),
        pytest.param(TINY_TEST_IMAGE_DATA_URL, id="data_url"),
    ],
)
def test_generate_text_from_input_live_accepts_tiny_image(image_url: str) -> None:
    """The public adapter accepts tiny hosted and inline image inputs."""
    adapter, _ = build_live_adapter()

    result = adapter.generate_text_from_input(
        developer_prompt="Reply with exactly OK when the request includes an image input.",
        user_input_parts=[
            LlmTextInputPart(text="Return OK."),
            LlmImageUrlInputPart(url=image_url),
        ],
        temperature=0,
    )

    assert result.content.strip() == "OK"
    assert result.usage is not None
    assert result.usage.total_tokens is None or result.usage.total_tokens > 0
