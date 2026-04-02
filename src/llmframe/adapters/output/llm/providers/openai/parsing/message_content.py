"""Public helpers for extracting text content from OpenAI responses."""

from __future__ import annotations

from typing import cast

from llmframe.adapters.output.llm.providers.openai.dto import OpenAIResponseError


def extract_message_content(response: object) -> str:
    """Extract text content from a chat-completions or Responses API payload."""
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text:
        return output_text

    raw_choices: object = getattr(response, "choices", None)
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

    _raise_response_error("LLM response content is not a supported text shape")
    return ""


def _raise_response_error(message: str) -> None:
    """Raise a consistent response-shape error."""
    raise OpenAIResponseError(message)


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


def _extract_nested_text_value(part: object) -> object:
    """Return nested text content from rich text objects when available."""
    text = getattr(part, "text", None)
    return None if text is None else getattr(text, "value", None)
