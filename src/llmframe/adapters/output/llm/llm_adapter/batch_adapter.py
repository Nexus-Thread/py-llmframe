"""Batch operations for the public LLM adapter façade."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from llmframe.application.ports import LlmBatchRequestItem

from .base import REQUEST_DEBUG_LABEL, BaseLlmAdapter
from .input_builders import build_inputs
from .payload_builders import (
    STRUCTURED_REASONING_EFFORT,
    STRUCTURED_TEMPERATURE,
    build_batch_structured_request_payload,
    build_batch_text_request_payload,
)
from .schema_normalizer import build_response_schema, schema_name

if TYPE_CHECKING:
    from llmframe.application.ports import (
        LlmBatchId,
        LlmBatchStatus,
        LlmBatchStructuredResult,
        LlmBatchSubmission,
        LlmBatchTextResult,
        StructuredOutputSchema,
    )
    from llmframe.application.ports.llm_provider import JsonSchema

    from .dto import LlmBatchStructuredRequest, LlmBatchTextRequest


class BatchLlmAdapter(BaseLlmAdapter):
    """Internal mixin for asynchronous batch LLM operations."""

    def submit_text_batch(self, *, requests: list[LlmBatchTextRequest]) -> LlmBatchSubmission:
        normalized_requests = self._build_batch_text_requests(requests=requests)
        self._validate_batch_requests(normalized_requests)
        self._log_json_stage(
            label=REQUEST_DEBUG_LABEL,
            payload=build_batch_text_request_payload(model=self._model, requests=normalized_requests),
            message="LLM batch request payload",
        )
        submission = self._client.submit_text_batch(model=self._model, requests=normalized_requests)
        self._persist_batch_submission(submission=submission, request_kind="text")
        return submission

    def submit_structured_batch(
        self,
        *,
        requests: list[LlmBatchStructuredRequest],
        response_schema: StructuredOutputSchema | None = None,
    ) -> LlmBatchSubmission:
        schema_model = self._require_response_schema(response_schema)
        schema_name_value = schema_name(schema_model)
        schema = build_response_schema(schema_model)
        normalized_requests = self._build_batch_structured_requests(requests=requests)
        self._validate_batch_requests(normalized_requests)
        self._log_json_stage(
            label=REQUEST_DEBUG_LABEL,
            payload=build_batch_structured_request_payload(
                model=self._model,
                requests=normalized_requests,
                schema_name=schema_name_value,
                schema=schema,
            ),
            message="LLM batch request payload",
        )
        submission = self._client.submit_structured_batch(
            model=self._model,
            requests=normalized_requests,
            json_schema_name=schema_name_value,
            schema=cast("JsonSchema", schema),
        )
        self._persist_batch_submission(submission=submission, request_kind="structured")
        return submission

    def get_batch_status(self, *, batch_id: LlmBatchId) -> LlmBatchStatus:
        return self._client.get_batch_status(batch_id=batch_id)

    def cancel_batch(self, *, batch_id: LlmBatchId) -> LlmBatchStatus:
        return self._client.cancel_batch(batch_id=batch_id)

    def get_text_batch_result(self, *, batch_id: LlmBatchId) -> LlmBatchTextResult:
        return self._client.get_text_batch_result(batch_id=batch_id)

    def get_structured_batch_result(self, *, batch_id: LlmBatchId) -> LlmBatchStructuredResult:
        return self._client.get_structured_batch_result(batch_id=batch_id)

    @staticmethod
    def _build_batch_text_requests(*, requests: list[LlmBatchTextRequest]) -> list[LlmBatchRequestItem]:
        """Normalize high-level text batch requests into provider batch items."""
        return [
            LlmBatchRequestItem(
                custom_id=request.custom_id,
                input_items=build_inputs(
                    developer_prompt=request.developer_prompt,
                    user_prompt=request.user_prompt,
                ),
                temperature=request.temperature,
                reasoning_effort=request.reasoning_effort,
            )
            for request in requests
        ]

    @staticmethod
    def _build_batch_structured_requests(
        *,
        requests: list[LlmBatchStructuredRequest],
    ) -> list[LlmBatchRequestItem]:
        """Normalize high-level structured batch requests into provider batch items."""
        return [
            LlmBatchRequestItem(
                custom_id=request.custom_id,
                input_items=build_inputs(
                    developer_prompt=request.developer_prompt,
                    user_prompt=request.user_prompt,
                ),
                temperature=STRUCTURED_TEMPERATURE,
                reasoning_effort=STRUCTURED_REASONING_EFFORT,
            )
            for request in requests
        ]
