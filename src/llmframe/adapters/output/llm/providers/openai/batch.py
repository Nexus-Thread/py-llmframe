"""Helpers for OpenAI Responses Batch API request and result handling."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

from llmframe.adapters.output.llm.llm_adapter.response_parser import parse_json_object

from .dto import OpenAIBatchRequestLine, OpenAIBatchResultLine
from .parsing import extract_message_content, extract_usage

if TYPE_CHECKING:
    from collections.abc import Sequence

    from llmframe.application.ports import LlmBatchRequestItem, LlmUsage
    from llmframe.application.ports.llm_provider import JsonSchema
    from llmframe.shared.json_types import JsonValue


def build_text_batch_request_line(*, request: LlmBatchRequestItem, model: str) -> OpenAIBatchRequestLine:
    """Build one JSONL request line for a plain-text Responses batch request."""
    body: dict[str, object] = {
        "model": model,
        "input": request.input_items,
        "text": {"format": {"type": "text"}},
    }
    if request.temperature is not None:
        body["temperature"] = request.temperature
    if request.reasoning_effort is not None:
        body["reasoning"] = {"effort": request.reasoning_effort}

    return OpenAIBatchRequestLine(
        custom_id=request.custom_id,
        method="POST",
        url="/v1/responses",
        body=body,
    )


def build_structured_batch_request_line(
    *,
    request: LlmBatchRequestItem,
    model: str,
    json_schema_name: str,
    schema: JsonSchema,
) -> OpenAIBatchRequestLine:
    """Build one JSONL request line for a structured Responses batch request."""
    body: dict[str, object] = {
        "model": model,
        "input": request.input_items,
        "temperature": request.temperature,
        "reasoning": {"effort": request.reasoning_effort} if request.reasoning_effort is not None else None,
        "text": {
            "format": {
                "type": "json_schema",
                "name": json_schema_name,
                "strict": True,
                "schema": cast("dict[str, object]", schema),
            }
        },
    }
    filtered_body = {key: value for key, value in body.items() if value is not None}
    return OpenAIBatchRequestLine(
        custom_id=request.custom_id,
        method="POST",
        url="/v1/responses",
        body=filtered_body,
    )


def serialize_batch_lines_to_jsonl(*, lines: Sequence[OpenAIBatchRequestLine]) -> bytes:
    """Serialize request lines to JSONL bytes for file upload."""
    content = "\n".join(
        json.dumps(
            {
                "custom_id": line.custom_id,
                "method": line.method,
                "url": line.url,
                "body": line.body,
            },
            sort_keys=True,
        )
        for line in lines
    )
    return f"{content}\n".encode()


def parse_batch_output_jsonl(*, content: str) -> list[OpenAIBatchResultLine]:
    """Parse a batch output JSONL document into normalized result lines."""
    result_lines: list[OpenAIBatchResultLine] = []
    for raw_line in content.splitlines():
        if not raw_line.strip():
            continue
        loaded = cast("dict[str, object]", json.loads(raw_line))
        response = loaded.get("response")
        response_body = None
        if isinstance(response, dict):
            response_body = response.get("body")
        error_value = loaded.get("error")
        error = None if error_value is None else json.dumps(error_value, sort_keys=True)
        result_lines.append(
            OpenAIBatchResultLine(
                custom_id=str(loaded["custom_id"]),
                response_body=response_body,
                error=error,
            )
        )
    return result_lines


def extract_batch_response_text(*, response_body: object) -> str:
    """Extract plain-text content from one batch result response body."""
    return extract_message_content(response_body)


def extract_batch_response_usage(*, response_body: object) -> LlmUsage | None:
    """Extract normalized token usage from one batch result response body."""
    return extract_usage(response_body)


def extract_batch_response_json_payload(*, response_body: object) -> dict[str, JsonValue]:
    """Extract and parse a structured JSON payload from one batch result response body."""
    return parse_json_object(extract_batch_response_text(response_body=response_body))
