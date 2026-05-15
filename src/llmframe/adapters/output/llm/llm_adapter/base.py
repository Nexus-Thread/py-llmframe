"""Shared internal base implementation for the public LLM adapter façade."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, cast

from llmframe.application.ports import (
    LlmBatchRequestItem,
    StoredLlmBatchRequest,
)

from .exceptions import StructuredLlmBatchError, StructuredLlmError
from .logging_utils import build_json_payload_log_extra, build_text_payload_log_extra

if TYPE_CHECKING:
    from llmframe.application.ports import (
        BatchRequestStorePort,
        JsonArtifactWriterPort,
        LlmBatchSubmission,
        LlmProviderPort,
        StructuredOutputSchema,
    )
    from llmframe.shared.json_types import JsonValue

LOGGER = logging.getLogger(__name__)

REQUEST_DEBUG_LABEL = "request_payload"
RESPONSE_TEXT_DEBUG_LABEL = "response_text"
PARSED_RESPONSE_DEBUG_LABEL = "parsed_response_payload"


class BaseLlmAdapter:
    """Shared runtime state and helper methods for LLM adapter operations."""

    def __init__(
        self,
        *,
        client: LlmProviderPort,
        model: str,
        debug_json_writer: JsonArtifactWriterPort | None = None,
        batch_request_store: BatchRequestStorePort | None = None,
        debug_json_enabled: bool = False,
    ) -> None:
        self._client = client
        self._model = model
        self._api_surface = "responses"
        self._debug_json_writer = debug_json_writer
        self._batch_request_store = batch_request_store
        self._debug_json_enabled = debug_json_enabled

    def _persist_batch_submission(self, *, submission: LlmBatchSubmission, request_kind: str) -> None:
        if self._batch_request_store is None:
            return
        try:
            batch_request = StoredLlmBatchRequest(
                batch_id=submission.batch_id,
                submitted_at=datetime.now(tz=UTC),
                model=self._model,
                request_kind=request_kind,
                input_file_id=submission.input_file_id,
                endpoint=submission.endpoint,
                status=submission.status,
                request_count=submission.request_count,
                metadata=submission.metadata,
            )
            written_path = self._batch_request_store.save_batch_request(batch_request=batch_request)
        except (OSError, TypeError, ValueError) as err:
            LOGGER.warning(
                "Failed to persist LLM batch submission metadata",
                exc_info=err,
                extra={
                    "component": self.__class__.__name__,
                    "model": self._model,
                    "request_kind": request_kind,
                },
            )
            return
        LOGGER.debug(
            "Persisted LLM batch submission metadata",
            extra={
                "component": self.__class__.__name__,
                "model": self._model,
                "request_kind": request_kind,
                "batch_id": batch_request.batch_id,
                "file_path": str(written_path),
            },
        )

    def _validate_batch_requests(self, requests: list[LlmBatchRequestItem]) -> None:
        if not requests:
            msg = "Batch requests must include at least one item"
            raise StructuredLlmBatchError(msg, suggestion="Pass one or more batch request items")

        custom_ids = [request.custom_id for request in requests]
        if len(custom_ids) != len(set(custom_ids)):
            msg = "Batch request custom_id values must be unique"
            raise StructuredLlmBatchError(msg, suggestion="Use a different custom_id for each batch item")

    def _require_response_schema(self, response_schema: StructuredOutputSchema | None) -> StructuredOutputSchema:
        if response_schema is None:
            msg = "Structured output requests require a response schema"
            raise StructuredLlmError(msg, suggestion="Pass a Pydantic response schema to the LLM adapter")
        return response_schema

    def _log_json_stage(
        self,
        *,
        label: str,
        payload: object,
        message: str,
        extra: dict[str, object] | None = None,
    ) -> None:
        self._write_debug_payload(label=label, payload=payload)
        payload_extra = build_json_payload_log_extra(payload=payload)
        if extra is not None:
            payload_extra.update(extra)
        self._log_payload_metadata(message=message, extra={"debug_label": label, **payload_extra})

    def _log_text_stage(
        self,
        *,
        label: str,
        content: str,
        message: str,
        extra: dict[str, object] | None = None,
    ) -> None:
        self._write_debug_payload(label=label, payload={"content": content})
        payload_extra = build_text_payload_log_extra(content=content)
        if extra is not None:
            payload_extra.update(extra)
        self._log_payload_metadata(message=message, extra={"debug_label": label, **payload_extra})

    def _log_payload_metadata(
        self,
        *,
        message: str,
        extra: dict[str, object],
    ) -> None:
        log_extra: dict[str, object] = {
            "component": self.__class__.__name__,
            "model": self._model,
            "api_surface": self._api_surface,
        }
        log_extra.update(extra)
        LOGGER.debug(message, extra=log_extra)

    def _write_debug_payload(self, *, label: str, payload: object) -> None:
        if not self._debug_json_enabled or self._debug_json_writer is None:
            return
        try:
            written_path = self._debug_json_writer.write_json(label=label, payload=cast("JsonValue", payload))
        except (OSError, TypeError, ValueError) as err:
            LOGGER.warning(
                "Failed to write LLM debug payload",
                exc_info=err,
                extra={
                    "component": self.__class__.__name__,
                    "model": self._model,
                    "debug_label": label,
                },
            )
            return
        LOGGER.debug(
            "LLM debug payload written",
            extra={
                "component": self.__class__.__name__,
                "model": self._model,
                "debug_label": label,
                "file_path": str(written_path),
            },
        )
