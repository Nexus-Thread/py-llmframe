"""Public helpers for extracting text content from OpenAI responses."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Never, cast

from llmframe.adapters.output.llm.providers.openai.dto import OpenAIResponseError


def extract_message_content(response: object) -> str:
    """Extract text content from a chat-completions or Responses API payload."""
    direct_output_text = _extract_direct_output_text(response)
    if direct_output_text is not None:
        return direct_output_text

    raw_choices = _extract_raw_choices(response)
    if not isinstance(raw_choices, list) or not raw_choices:
        _raise_response_error("LLM response did not include choices")

    choices = cast("list[object]", raw_choices)
    first_choice = choices[0]
    message = getattr(first_choice, "message", None)
    if message is None:
        _raise_response_error("LLM response did not include a message")

    content = getattr(message, "content", None)
    if content is None:
        _raise_response_error("LLM response did not include content")

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        extracted_text = _extract_text_from_content_parts(content)
        if extracted_text:
            return extracted_text

    return _raise_unsupported_content_shape()


def _extract_direct_output_text(response: object) -> str | None:
    """Return top-level output text when the payload exposes it directly."""
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text:
        return output_text

    if not isinstance(response, Mapping):
        return None

    mapped_output_text = response.get("output_text")
    if isinstance(mapped_output_text, str) and mapped_output_text:
        return mapped_output_text

    mapped_output = response.get("output")
    if not isinstance(mapped_output, list):
        return None

    extracted_output_text = _extract_text_from_output_items(mapped_output)
    return extracted_output_text or None


def _extract_raw_choices(response: object) -> object:
    """Return the raw choices collection from a response payload."""
    if isinstance(response, Mapping):
        return response.get("choices")
    return getattr(response, "choices", None)


def _raise_response_error(message: str) -> Never:
    """Raise a consistent response-shape error."""
    raise OpenAIResponseError(message)


def _raise_unsupported_content_shape() -> Never:
    """Raise the standard error for unsupported response content shapes."""
    msg = "LLM response content is not a supported text shape"
    raise OpenAIResponseError(msg)


def _extract_text_from_content_parts(parts: list[object]) -> str:
    """Join supported text fragments from structured content parts."""
    extracted_parts: list[str] = []
    for part in parts:
        part_text = _extract_content_part_text(part)
        if part_text is not None:
            extracted_parts.append(part_text)
    return "".join(extracted_parts)


def _extract_content_part_text(part: object) -> str | None:
    """Extract text from a structured content part."""
    if isinstance(part, str):
        return part

    if isinstance(part, dict):
        text = part.get("text")
        return text if isinstance(text, str) else None

    text = getattr(part, "text", None)
    if isinstance(text, str):
        return text

    nested_text = _extract_nested_text_value(part)
    if isinstance(nested_text, str):
        return nested_text

    return None


def _extract_text_from_output_items(items: list[object]) -> str:
    """Join text fragments from Responses API output items when available."""
    extracted_parts: list[str] = []
    for item in items:
        item_content = item.get("content") if isinstance(item, Mapping) else getattr(item, "content", None)
        if not isinstance(item_content, list):
            continue
        extracted_text = _extract_text_from_content_parts(item_content)
        if extracted_text:
            extracted_parts.append(extracted_text)
    return "".join(extracted_parts)


def _extract_nested_text_value(part: object) -> object:
    """Return nested text content from rich text objects when available."""
    text = getattr(part, "text", None)
    return None if text is None else getattr(text, "value", None)
