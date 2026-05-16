"""Batch file I/O helpers for the OpenAI transport."""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING, Any, cast

from llmframe.adapters.output.llm.providers.openai.batch import parse_batch_output_jsonl, serialize_batch_lines_to_jsonl
from llmframe.adapters.output.llm.providers.openai.dto import OpenAIBatchFileUpload, OpenAIBatchResultLine

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from llmframe.adapters.output.llm.providers.openai.dto import OpenAIBatchRequestLine


def upload_batch_file(
    *,
    lines: Sequence[OpenAIBatchRequestLine],
    upload: Callable[[object], object],
) -> OpenAIBatchFileUpload:
    """Serialize and upload a JSONL input file for the OpenAI Batch API."""
    payload = serialize_batch_lines_to_jsonl(lines=lines)
    file_response = cast("Any", upload(("responses-batch.jsonl", BytesIO(payload), "application/jsonl")))
    return OpenAIBatchFileUpload(file_id=cast("str", file_response.id), purpose=cast("str", file_response.purpose))


def download_batch_output(*, content: object) -> str:
    """Normalize SDK file content responses to text."""
    if isinstance(content, bytes):
        return content.decode("utf-8")
    if isinstance(content, str):
        return content

    resolved_content = _text_attribute_content(content)
    if resolved_content is not None:
        return resolved_content
    resolved_content = _read_method_content(content)
    if resolved_content is not None:
        return resolved_content
    return str(content)


def _text_attribute_content(content: object) -> str | None:
    """Return content exposed by a text attribute or text method."""
    text_value = getattr(content, "text", None)
    if isinstance(text_value, str):
        return text_value
    if callable(text_value):
        text_result = text_value()
        if isinstance(text_result, str):
            return text_result
    return None


def _read_method_content(content: object) -> str | None:
    """Return content exposed by a read method."""
    read_value = getattr(content, "read", None)
    if callable(read_value):
        read_result = read_value()
        if isinstance(read_result, bytes):
            return read_result.decode("utf-8")
        if isinstance(read_result, str):
            return read_result
    return None


def parse_output_jsonl(*, content: str) -> list[OpenAIBatchResultLine]:
    """Parse JSONL batch output content into normalized result lines."""
    return parse_batch_output_jsonl(content=content)


__all__ = ["download_batch_output", "parse_output_jsonl", "upload_batch_file"]
