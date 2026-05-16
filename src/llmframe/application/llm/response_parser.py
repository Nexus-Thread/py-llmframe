"""Provider-neutral parsing helpers for structured LLM outputs."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

from llmframe.application.exceptions import StructuredLlmInvalidJsonError

if TYPE_CHECKING:
    from llmframe.shared.json_types import JsonValue


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
