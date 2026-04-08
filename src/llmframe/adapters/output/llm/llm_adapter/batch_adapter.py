"""Batch operations for the public LLM adapter façade."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from .base import REQUEST_DEBUG_LABEL, BaseLlmAdapter

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
            payload=self._build_batch_text_request_payload(requests=normalized_requests),
            message="LLM batch request payload",
        )
        return self._client.submit_text_batch(model=self._model, requests=normalized_requests)

    def submit_structured_batch(
        self,
        *,
        requests: list[LlmBatchStructuredRequest],
        response_schema: StructuredOutputSchema | None = None,
    ) -> LlmBatchSubmission:
        schema_model = self._require_response_schema(response_schema)
        schema_name = self._schema_name(schema_model)
        schema = self._build_response_schema(schema_model)
        normalized_requests = self._build_batch_structured_requests(requests=requests)
        self._validate_batch_requests(normalized_requests)
        self._log_json_stage(
            label=REQUEST_DEBUG_LABEL,
            payload=self._build_batch_structured_request_payload(
                requests=normalized_requests,
                schema_name=schema_name,
                schema=schema,
            ),
            message="LLM batch request payload",
        )
        return self._client.submit_structured_batch(
            model=self._model,
            requests=normalized_requests,
            json_schema_name=schema_name,
            schema=cast("JsonSchema", schema),
        )

    def get_batch_status(self, *, batch_id: LlmBatchId) -> LlmBatchStatus:
        return self._client.get_batch_status(batch_id=batch_id)

    def cancel_batch(self, *, batch_id: LlmBatchId) -> LlmBatchStatus:
        return self._client.cancel_batch(batch_id=batch_id)

    def get_text_batch_result(self, *, batch_id: LlmBatchId) -> LlmBatchTextResult:
        return self._client.get_text_batch_result(batch_id=batch_id)

    def get_structured_batch_result(self, *, batch_id: LlmBatchId) -> LlmBatchStructuredResult:
        return self._client.get_structured_batch_result(batch_id=batch_id)
