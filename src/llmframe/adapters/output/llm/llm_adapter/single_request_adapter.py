"""Single-request operations for the public LLM adapter façade."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from .base import (
    PARSED_RESPONSE_DEBUG_LABEL,
    REQUEST_DEBUG_LABEL,
    RESPONSE_TEXT_DEBUG_LABEL,
    STRUCTURED_REASONING_EFFORT,
    STRUCTURED_TEMPERATURE,
    BaseLlmAdapter,
)
from .dto import LlmTextCompletionResult, StructuredLlmJsonCompletionResult
from .response_parser import parse_json_object

if TYPE_CHECKING:
    from llmframe.application.ports import StructuredOutputSchema
    from llmframe.application.ports.llm_provider import JsonSchema


class SingleRequestLlmAdapter(BaseLlmAdapter):
    """Internal mixin for synchronous single-request LLM operations."""

    def generate_text(
        self,
        *,
        developer_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        reasoning_effort: str | None = None,
    ) -> LlmTextCompletionResult:
        inputs = self._build_inputs(developer_prompt=developer_prompt, user_prompt=user_prompt)
        self._log_json_stage(
            label=REQUEST_DEBUG_LABEL,
            payload=self._build_text_request_payload(
                inputs=inputs,
                temperature=temperature,
                reasoning_effort=reasoning_effort,
            ),
            message="LLM request payload",
        )
        response = self._client.create_response(
            model=self._model,
            input_items=inputs,
            temperature=temperature,
            reasoning_effort=reasoning_effort,
        )
        content = self._client.extract_text(response)
        usage = self._client.extract_usage(response)
        self._log_text_stage(
            label=RESPONSE_TEXT_DEBUG_LABEL,
            content=content,
            message="LLM response content",
        )
        return LlmTextCompletionResult(content=content, usage=usage)

    def extract_json(
        self,
        *,
        developer_prompt: str,
        user_prompt: str,
        response_schema: StructuredOutputSchema | None = None,
    ) -> StructuredLlmJsonCompletionResult:
        inputs = self._build_inputs(developer_prompt=developer_prompt, user_prompt=user_prompt)
        schema_model = self._require_response_schema(response_schema)
        schema_name = self._schema_name(schema_model)
        schema = self._build_response_schema(schema_model)
        self._log_json_stage(
            label=REQUEST_DEBUG_LABEL,
            payload=self._build_structured_request_payload(
                inputs=inputs,
                schema_name=schema_name,
                schema=schema,
            ),
            message="LLM request payload",
        )
        response = self._client.create_structured_response(
            model=self._model,
            input_items=inputs,
            json_schema_name=schema_name,
            schema=cast("JsonSchema", schema),
            temperature=STRUCTURED_TEMPERATURE,
            reasoning_effort=STRUCTURED_REASONING_EFFORT,
        )
        content = self._client.extract_text(response)
        usage = self._client.extract_usage(response)
        self._log_text_stage(
            label=RESPONSE_TEXT_DEBUG_LABEL,
            content=content,
            message="LLM response content",
        )
        payload = parse_json_object(content)
        self._log_json_stage(
            label=PARSED_RESPONSE_DEBUG_LABEL,
            payload=payload,
            message="LLM parsed JSON payload",
            extra={"payload_keys": list(payload.keys())},
        )
        return StructuredLlmJsonCompletionResult(payload=payload, usage=usage)
