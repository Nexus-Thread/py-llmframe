"""Batch operations for the public OpenAI provider adapter façade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from llmframe.application.ports import LlmBatchStructuredResult, LlmBatchTextResult

from .batch import build_structured_batch_request_line, build_text_batch_request_line
from .provider_base import OpenAIProviderBase

if TYPE_CHECKING:
    from llmframe.application.ports import (
        LlmBatchId,
        LlmBatchRequestItem,
        LlmBatchStatus,
        LlmBatchSubmission,
    )
    from llmframe.application.ports.llm_provider import JsonSchema


class OpenAIProviderBatchAdapter(OpenAIProviderBase):
    """Internal mixin for batch OpenAI provider operations."""

    def submit_text_batch(self, *, model: str, requests: list[LlmBatchRequestItem]) -> LlmBatchSubmission:
        """Submit one plain-text Responses batch."""
        lines = [build_text_batch_request_line(request=request, model=model) for request in requests]
        upload = self._transport.upload_batch_file(lines=lines)
        batch = self._transport.create_response_batch(input_file_id=upload.file_id)
        return self._to_batch_submission(batch=batch, request_count=len(requests))

    def submit_structured_batch(
        self,
        *,
        model: str,
        requests: list[LlmBatchRequestItem],
        json_schema_name: str,
        schema: JsonSchema,
    ) -> LlmBatchSubmission:
        """Submit one structured-output Responses batch."""
        lines = [
            build_structured_batch_request_line(
                request=request,
                model=model,
                json_schema_name=json_schema_name,
                schema=schema,
            )
            for request in requests
        ]
        upload = self._transport.upload_batch_file(lines=lines)
        batch = self._transport.create_response_batch(input_file_id=upload.file_id)
        return self._to_batch_submission(batch=batch, request_count=len(requests))

    def get_batch_status(self, *, batch_id: LlmBatchId) -> LlmBatchStatus:
        """Return a normalized status snapshot for one batch."""
        return self._to_batch_status(batch=self._transport.retrieve_batch(batch_id=batch_id))

    def cancel_batch(self, *, batch_id: LlmBatchId) -> LlmBatchStatus:
        """Cancel one batch and return a normalized status snapshot."""
        return self._to_batch_status(batch=self._transport.cancel_batch(batch_id=batch_id))

    def get_text_batch_result(self, *, batch_id: LlmBatchId) -> LlmBatchTextResult:
        """Return normalized plain-text results for one completed batch."""
        status = self._to_batch_status(batch=self._transport.retrieve_batch(batch_id=batch_id))
        output_file_id = self._require_output_file_id(status=status)
        content = self._transport.download_batch_output(file_id=output_file_id)
        lines = self._transport.parse_batch_output_jsonl(content=content)
        return LlmBatchTextResult(
            batch_id=batch_id,
            status=status.status,
            items=[self._to_text_result_item(line=line) for line in lines],
        )

    def get_structured_batch_result(self, *, batch_id: LlmBatchId) -> LlmBatchStructuredResult:
        """Return normalized structured-output results for one completed batch."""
        status = self._to_batch_status(batch=self._transport.retrieve_batch(batch_id=batch_id))
        output_file_id = self._require_output_file_id(status=status)
        content = self._transport.download_batch_output(file_id=output_file_id)
        lines = self._transport.parse_batch_output_jsonl(content=content)
        return LlmBatchStructuredResult(
            batch_id=batch_id,
            status=status.status,
            items=[self._to_structured_result_item(line=line) for line in lines],
        )
