"""Response parsing helpers for structured LLM outputs."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

from llmframe.adapters.output.llm.openai_adapter import (
    OpenAIResponseError,
    extract_message_content,
)

from .exceptions import StructuredLlmInvalidJsonError, StructuredLlmResponseError

if TYPE_CHECKING:
    from llmframe.json_types import JsonValue


def extract_structured_content(response: object) -> str:
    """Extract textual content from an OpenAI response object."""
    try:
        return extract_message_content(response)
    except OpenAIResponseError as err:
        msg = "LLM response is missing content or has an invalid shape"
        raise StructuredLlmResponseError(msg, suggestion=str(err)) from err


def parse_json_object(content: str) -> dict[str, JsonValue]:
    """Parse model content and require a top-level JSON object result."""
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as err:
        msg = "LLM returned invalid JSON payload"
        raise StructuredLlmInvalidJsonError(msg, suggestion="Inspect the model output and prompts") from err
    if not isinstance(payload, dict):
        msg = "LLM payload must be a JSON object"
        raise StructuredLlmInvalidJsonError(msg, suggestion="Ensure the prompt requests a top-level JSON object")
    return cast("dict[str, JsonValue]", payload)
