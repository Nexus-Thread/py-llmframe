"""Live integration tests for tiny multimodal image and file input."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from llmframe import LlmFileInputPart, LlmImageFileInputPart, LlmImageUrlInputPart, LlmTextInputPart

from .helpers import (
    PYTEST_MARKS,
    TINY_TEST_IMAGE_BYTES,
    TINY_TEST_IMAGE_DATA_URL,
    TINY_TEST_IMAGE_URL,
    TINY_TEST_PDF_PATH,
    build_live_adapter,
)

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


def test_generate_text_from_input_live_accepts_local_tiny_image_file(tmp_path: Path) -> None:
    """The public adapter accepts a tiny local image file input."""
    adapter, _ = build_live_adapter()
    image_path = tmp_path / "tiny.png"
    image_path.write_bytes(TINY_TEST_IMAGE_BYTES)

    result = adapter.generate_text_from_input(
        developer_prompt="Reply with exactly OK when the request includes an image input.",
        user_input_parts=[
            LlmTextInputPart(text="Return OK."),
            LlmImageFileInputPart(path=image_path),
        ],
        temperature=0,
    )

    assert result.content.strip() == "OK"
    assert result.usage is not None
    assert result.usage.total_tokens is None or result.usage.total_tokens > 0


def test_generate_text_from_input_live_accepts_local_tiny_pdf_file(tmp_path: Path) -> None:
    """The public adapter accepts a tiny local PDF file input."""
    adapter, _ = build_live_adapter()
    pdf_path = tmp_path / "tiny.pdf"
    pdf_path.write_bytes(TINY_TEST_PDF_PATH.read_bytes())

    result = adapter.generate_text_from_input(
        developer_prompt="Reply with exactly OK when the request includes a PDF file input.",
        user_input_parts=[
            LlmTextInputPart(text="Return OK."),
            LlmFileInputPart(path=pdf_path),
        ],
        temperature=0,
    )

    assert result.content.strip() == "OK"
    assert result.usage is not None
    assert result.usage.total_tokens is None or result.usage.total_tokens > 0
