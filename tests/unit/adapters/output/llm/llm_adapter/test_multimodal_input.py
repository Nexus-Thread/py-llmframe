"""Unit tests for shared LLM adapter multimodal input formatting."""

from __future__ import annotations

import logging
from base64 import b64decode
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from llmframe.adapters.output.llm.llm_adapter import (
    LlmFileInputPart,
    LlmImageFileInputPart,
    LlmImageUrlInputPart,
    LlmTextCompletionResult,
    LlmTextInputPart,
    StructuredLlmError,
)

from ._support import (
    LOGGER_NAME,
    TINY_PNG_BASE64,
    _build_adapter,
    _find_record,
    _record_extra,
    _ResponsesApiResponse,
)


def test_generate_text_from_input_supports_image_url_parts() -> None:
    """Adapter builds one multimodal user message with text and image parts."""
    adapter, client = _build_adapter([_ResponsesApiResponse(output_text="hello")])

    result = adapter.generate_text_from_input(
        developer_prompt="developer",
        user_input_parts=[
            LlmTextInputPart(text="describe this image"),
            LlmImageUrlInputPart(url="https://example.com/cat.png"),
        ],
    )

    assert result == LlmTextCompletionResult(content="hello", usage=None)
    assert client.calls == [
        (
            "responses_plain",
            "gpt-test",
            [
                {"role": "developer", "content": "developer"},
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "describe this image"},
                        {"type": "input_image", "image_url": "https://example.com/cat.png"},
                    ],
                },
            ],
        )
    ]


def test_generate_text_from_input_supports_local_image_file_parts(tmp_path: Path) -> None:
    """Adapter converts a local image path into a data URL input image part."""
    image_path = tmp_path / "tiny.png"
    image_path.write_bytes(b64decode(TINY_PNG_BASE64))
    adapter, client = _build_adapter([_ResponsesApiResponse(output_text="hello")])

    result = adapter.generate_text_from_input(
        developer_prompt="developer",
        user_input_parts=[
            LlmTextInputPart(text="describe this image"),
            LlmImageFileInputPart(path=image_path),
        ],
    )

    assert result == LlmTextCompletionResult(content="hello", usage=None)
    assert client.calls == [
        (
            "responses_plain",
            "gpt-test",
            [
                {"role": "developer", "content": "developer"},
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "describe this image"},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{TINY_PNG_BASE64}",
                        },
                    ],
                },
            ],
        )
    ]


def test_generate_text_from_input_rejects_missing_local_image_file() -> None:
    """Adapter raises a shared error when the local image file does not exist."""
    adapter, _ = _build_adapter([_ResponsesApiResponse(output_text="hello")])

    with pytest.raises(StructuredLlmError, match="does not exist"):
        adapter.generate_text_from_input(
            developer_prompt="developer",
            user_input_parts=[LlmImageFileInputPart(path="missing.png")],
        )


def test_generate_text_from_input_rejects_non_image_local_file(tmp_path: Path) -> None:
    """Adapter raises a shared error for unsupported local file types."""
    file_path = tmp_path / "not-image.txt"
    file_path.write_text("not an image", encoding="utf-8")
    adapter, _ = _build_adapter([_ResponsesApiResponse(output_text="hello")])

    with pytest.raises(StructuredLlmError, match="Unsupported image file type"):
        adapter.generate_text_from_input(
            developer_prompt="developer",
            user_input_parts=[LlmImageFileInputPart(path=file_path)],
        )


def test_generate_text_from_input_supports_local_document_file_parts(tmp_path: Path) -> None:
    """Adapter converts a supported local document into an input-file content part."""
    file_path = tmp_path / "notes.txt"
    file_path.write_text("hello file", encoding="utf-8")
    adapter, client = _build_adapter([_ResponsesApiResponse(output_text="hello")])

    result = adapter.generate_text_from_input(
        developer_prompt="developer",
        user_input_parts=[
            LlmTextInputPart(text="summarize this file"),
            LlmFileInputPart(path=file_path),
        ],
    )

    assert result == LlmTextCompletionResult(content="hello", usage=None)
    assert client.calls == [
        (
            "responses_plain",
            "gpt-test",
            [
                {"role": "developer", "content": "developer"},
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "summarize this file"},
                        {
                            "type": "input_file",
                            "file_data": "data:text/plain;base64,aGVsbG8gZmlsZQ==",
                            "filename": "notes.txt",
                        },
                    ],
                },
            ],
        )
    ]


def test_generate_text_from_input_supports_multiple_local_file_extensions(tmp_path: Path) -> None:
    """Adapter accepts each supported non-image local file extension."""
    adapter, _ = _build_adapter([_ResponsesApiResponse(output_text="ok")] * 15)

    for extension in (
        ".pdf",
        ".txt",
        ".md",
        ".json",
        ".html",
        ".xml",
        ".doc",
        ".docx",
        ".rtf",
        ".odt",
        ".ppt",
        ".pptx",
        ".csv",
        ".xls",
        ".xlsx",
    ):
        file_path = tmp_path / f"sample{extension}"
        file_path.write_bytes(b"sample")

        result = adapter.generate_text_from_input(
            developer_prompt="developer",
            user_input_parts=[LlmFileInputPart(path=file_path)],
        )

        assert result == LlmTextCompletionResult(content="ok", usage=None)


def test_generate_text_from_input_rejects_unsupported_local_file_part(tmp_path: Path) -> None:
    """Adapter raises a shared error for unsupported document file types."""
    file_path = tmp_path / "archive.zip"
    file_path.write_bytes(b"zip")
    adapter, _ = _build_adapter([_ResponsesApiResponse(output_text="hello")])

    with pytest.raises(StructuredLlmError, match="Unsupported file type"):
        adapter.generate_text_from_input(
            developer_prompt="developer",
            user_input_parts=[LlmFileInputPart(path=file_path)],
        )


def test_generate_text_from_input_rejects_missing_local_file_part() -> None:
    """Adapter raises a shared error when a local document file does not exist."""
    adapter, _ = _build_adapter([_ResponsesApiResponse(output_text="hello")])

    with pytest.raises(StructuredLlmError, match="does not exist"):
        adapter.generate_text_from_input(
            developer_prompt="developer",
            user_input_parts=[LlmFileInputPart(path="missing.pdf")],
        )


def test_generate_text_from_input_supports_mixed_image_and_file_parts(tmp_path: Path) -> None:
    """Adapter preserves mixed text, image, and document content ordering."""
    image_path = tmp_path / "tiny.png"
    image_path.write_bytes(b64decode(TINY_PNG_BASE64))
    file_path = tmp_path / "notes.md"
    file_path.write_text("# Heading", encoding="utf-8")
    adapter, client = _build_adapter([_ResponsesApiResponse(output_text="hello")])

    result = adapter.generate_text_from_input(
        developer_prompt="developer",
        user_input_parts=[
            LlmTextInputPart(text="Use both inputs"),
            LlmImageFileInputPart(path=image_path),
            LlmFileInputPart(path=file_path),
        ],
    )

    assert result == LlmTextCompletionResult(content="hello", usage=None)
    assert client.calls == [
        (
            "responses_plain",
            "gpt-test",
            [
                {"role": "developer", "content": "developer"},
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Use both inputs"},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{TINY_PNG_BASE64}",
                        },
                        {
                            "type": "input_file",
                            "file_data": "data:text/markdown;base64,IyBIZWFkaW5n",
                            "filename": "notes.md",
                        },
                    ],
                },
            ],
        )
    ]


def test_generate_text_from_input_logs_multimodal_request_payload(caplog: pytest.LogCaptureFixture) -> None:
    """Adapter debug logging preserves multimodal request payload structure."""
    adapter, _ = _build_adapter([_ResponsesApiResponse(output_text="hello")])

    with caplog.at_level(logging.DEBUG, logger=LOGGER_NAME):
        result = adapter.generate_text_from_input(
            developer_prompt="developer",
            user_input_parts=[
                LlmTextInputPart(text="look"),
                LlmImageUrlInputPart(url="https://example.com/image.png"),
            ],
            temperature=0.1,
        )

    assert result == LlmTextCompletionResult(content="hello", usage=None)
    request_record_any = _record_extra(_find_record(caplog, "LLM request payload"))
    assert request_record_any.payload_keys == ["input", "model", "temperature", "text"]
