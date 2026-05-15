"""Request payload builders for shared LLM adapter logging and batch submission."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llmframe.application.ports import LlmBatchRequestItem, LlmInputItem

RESPONSES_ENDPOINT = "/v1/responses"
STRUCTURED_TEMPERATURE = 0
STRUCTURED_REASONING_EFFORT = "none"


def build_text_request_payload(
    *,
    model: str,
    inputs: list[LlmInputItem],
    temperature: float | None,
    reasoning_effort: str | None,
) -> dict[str, object]:
    """Build a plain-text Responses API request payload."""
    payload: dict[str, object] = {
        "model": model,
        "input": inputs,
        "text": {"format": {"type": "text"}},
    }
    if temperature is not None:
        payload["temperature"] = temperature
    if reasoning_effort is not None:
        payload["reasoning"] = {"effort": reasoning_effort}
    return payload


def build_structured_request_payload(
    *,
    model: str,
    inputs: list[LlmInputItem],
    schema_name: str,
    schema: dict[str, object],
) -> dict[str, object]:
    """Build a structured-output Responses API request payload."""
    return {
        "model": model,
        "input": inputs,
        "reasoning": {"effort": STRUCTURED_REASONING_EFFORT},
        "temperature": STRUCTURED_TEMPERATURE,
        "text": {
            "format": {
                "type": "json_schema",
                "name": schema_name,
                "strict": True,
                "schema": schema,
            }
        },
    }


def build_batch_text_request_payload(*, model: str, requests: list[LlmBatchRequestItem]) -> dict[str, object]:
    """Build a metadata-safe batch text payload for debug logging."""
    return {
        "endpoint": RESPONSES_ENDPOINT,
        "request_count": len(requests),
        "requests": [
            {
                "custom_id": request.custom_id,
                "body": build_text_request_payload(
                    model=model,
                    inputs=request.input_items,
                    temperature=request.temperature,
                    reasoning_effort=request.reasoning_effort,
                ),
            }
            for request in requests
        ],
    }


def build_batch_structured_request_payload(
    *,
    model: str,
    requests: list[LlmBatchRequestItem],
    schema_name: str,
    schema: dict[str, object],
) -> dict[str, object]:
    """Build a metadata-safe batch structured-output payload for debug logging."""
    return {
        "endpoint": RESPONSES_ENDPOINT,
        "request_count": len(requests),
        "requests": [
            {
                "custom_id": request.custom_id,
                "body": build_structured_request_payload(
                    model=model,
                    inputs=request.input_items,
                    schema_name=schema_name,
                    schema=schema,
                ),
            }
            for request in requests
        ],
    }
