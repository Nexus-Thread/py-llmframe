"""Application service for provider-neutral LLM orchestration."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, cast

from llmframe.application.dtos import (
    LlmBatchStructuredRequest,
    LlmBatchTextRequest,
    LlmFileInputPart,
    LlmImageFileInputPart,
    LlmImageUrlInputPart,
    LlmTextCompletionResult,
    LlmTextInputPart,
    StructuredLlmJsonCompletionResult,
)
from llmframe.application.exceptions import StructuredLlmBatchError, StructuredLlmError
from llmframe.application.llm.input_builders import build_inputs, build_multimodal_inputs
from llmframe.application.llm.payload_builders import (
    STRUCTURED_REASONING_EFFORT,
    STRUCTURED_TEMPERATURE,
    build_batch_structured_request_payload,
    build_batch_text_request_payload,
    build_structured_request_payload,
    build_text_request_payload,
)
from llmframe.application.llm.response_parser import parse_json_object
from llmframe.application.llm.schema_normalizer import build_response_schema, schema_name
from llmframe.application.ports import LlmBatchRequestItem, StoredLlmBatchRequest

if TYPE_CHECKING:
    from llmframe.application.ports import (
        BatchRequestStorePort,
        JsonArtifactWriterPort,
        LlmBatchId,
        LlmBatchStatus,
        LlmBatchStructuredResult,
        LlmBatchSubmission,
        LlmBatchTextResult,
        LlmProviderPort,
        StructuredOutputSchema,
    )
    from llmframe.application.ports.llm_provider import JsonSchema
    from llmframe.shared.json_types import JsonValue

LOGGER = logging.getLogger(__name__)

REQUEST_DEBUG_LABEL = "request_payload"
RESPONSE_TEXT_DEBUG_LABEL = "response_text"
PARSED_RESPONSE_DEBUG_LABEL = "parsed_response_payload"


class LlmService:
    """Application service that coordinates provider-neutral LLM use cases."""

    def __init__(
        self,
        *,
        provider: LlmProviderPort,
        model: str,
        debug_json_writer: JsonArtifactWriterPort | None = None,
        batch_request_store: BatchRequestStorePort | None = None,
        debug_json_enabled: bool = False,
    ) -> None:
        self._provider = provider
        self._model = model
        self._api_surface = "responses"
        self._debug_json_writer = debug_json_writer
        self._batch_request_store = batch_request_store
        self._debug_json_enabled = debug_json_enabled

    def generate_text(
        self,
        *,
        developer_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        reasoning_effort: str | None = None,
    ) -> LlmTextCompletionResult:
        """Generate plain text from developer and user prompts."""
        inputs = build_inputs(developer_prompt=developer_prompt, user_prompt=user_prompt)
        self._log_json_stage(
            label=REQUEST_DEBUG_LABEL,
            payload=build_text_request_payload(
                model=self._model,
                inputs=inputs,
                temperature=temperature,
                reasoning_effort=reasoning_effort,
            ),
            message="LLM request payload",
        )
        response = self._provider.create_response(
            model=self._model,
            input_items=inputs,
            temperature=temperature,
            reasoning_effort=reasoning_effort,
        )
        content = self._provider.extract_text(response)
        usage = self._provider.extract_usage(response)
        self._log_text_stage(label=RESPONSE_TEXT_DEBUG_LABEL, content=content, message="LLM response content")
        return LlmTextCompletionResult(content=content, usage=usage)

    def generate_text_from_input(
        self,
        *,
        developer_prompt: str,
        user_input_parts: list[LlmTextInputPart | LlmImageUrlInputPart | LlmImageFileInputPart | LlmFileInputPart],
        temperature: float | None = None,
        reasoning_effort: str | None = None,
    ) -> LlmTextCompletionResult:
        """Generate plain text from mixed text, image, and file input parts."""
        inputs = build_multimodal_inputs(developer_prompt=developer_prompt, user_input_parts=user_input_parts)
        self._log_json_stage(
            label=REQUEST_DEBUG_LABEL,
            payload=build_text_request_payload(
                model=self._model,
                inputs=inputs,
                temperature=temperature,
                reasoning_effort=reasoning_effort,
            ),
            message="LLM request payload",
        )
        response = self._provider.create_response(
            model=self._model,
            input_items=inputs,
            temperature=temperature,
            reasoning_effort=reasoning_effort,
        )
        content = self._provider.extract_text(response)
        usage = self._provider.extract_usage(response)
        self._log_text_stage(label=RESPONSE_TEXT_DEBUG_LABEL, content=content, message="LLM response content")
        return LlmTextCompletionResult(content=content, usage=usage)

    def extract_json(
        self,
        *,
        developer_prompt: str,
        user_prompt: str,
        response_schema: StructuredOutputSchema | None = None,
    ) -> StructuredLlmJsonCompletionResult:
        """Generate and parse a structured JSON object response."""
        inputs = build_inputs(developer_prompt=developer_prompt, user_prompt=user_prompt)
        schema_model = self._require_response_schema(response_schema)
        schema_name_value = schema_name(schema_model)
        schema = build_response_schema(schema_model)
        self._log_json_stage(
            label=REQUEST_DEBUG_LABEL,
            payload=build_structured_request_payload(
                model=self._model,
                inputs=inputs,
                schema_name=schema_name_value,
                schema=schema,
            ),
            message="LLM request payload",
        )
        response = self._provider.create_structured_response(
            model=self._model,
            input_items=inputs,
            json_schema_name=schema_name_value,
            schema=cast("JsonSchema", schema),
            temperature=STRUCTURED_TEMPERATURE,
            reasoning_effort=STRUCTURED_REASONING_EFFORT,
        )
        content = self._provider.extract_text(response)
        usage = self._provider.extract_usage(response)
        self._log_text_stage(label=RESPONSE_TEXT_DEBUG_LABEL, content=content, message="LLM response content")
        payload = parse_json_object(content)
        self._log_json_stage(
            label=PARSED_RESPONSE_DEBUG_LABEL,
            payload=payload,
            message="LLM parsed JSON payload",
            extra={"payload_keys": list(payload.keys())},
        )
        return StructuredLlmJsonCompletionResult(payload=payload, usage=usage)

    def submit_text_batch(self, *, requests: list[LlmBatchTextRequest]) -> LlmBatchSubmission:
        """Submit a plain-text LLM batch request."""
        normalized_requests = self._build_batch_text_requests(requests=requests)
        self._validate_batch_requests(normalized_requests)
        self._log_json_stage(
            label=REQUEST_DEBUG_LABEL,
            payload=build_batch_text_request_payload(model=self._model, requests=normalized_requests),
            message="LLM batch request payload",
        )
        submission = self._provider.submit_text_batch(model=self._model, requests=normalized_requests)
        self._persist_batch_submission(submission=submission, request_kind="text")
        return submission

    def submit_structured_batch(
        self,
        *,
        requests: list[LlmBatchStructuredRequest],
        response_schema: StructuredOutputSchema | None = None,
    ) -> LlmBatchSubmission:
        """Submit a structured-output LLM batch request."""
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
        submission = self._provider.submit_structured_batch(
            model=self._model,
            requests=normalized_requests,
            json_schema_name=schema_name_value,
            schema=cast("JsonSchema", schema),
        )
        self._persist_batch_submission(submission=submission, request_kind="structured")
        return submission

    def get_batch_status(self, *, batch_id: LlmBatchId) -> LlmBatchStatus:
        """Return status for a submitted LLM batch."""
        return self._provider.get_batch_status(batch_id=batch_id)

    def cancel_batch(self, *, batch_id: LlmBatchId) -> LlmBatchStatus:
        """Cancel a submitted LLM batch."""
        return self._provider.cancel_batch(batch_id=batch_id)

    def get_text_batch_result(self, *, batch_id: LlmBatchId) -> LlmBatchTextResult:
        """Return parsed plain-text batch results."""
        return self._provider.get_text_batch_result(batch_id=batch_id)

    def get_structured_batch_result(self, *, batch_id: LlmBatchId) -> LlmBatchStructuredResult:
        """Return parsed structured-output batch results."""
        return self._provider.get_structured_batch_result(batch_id=batch_id)

    @staticmethod
    def _build_batch_text_requests(*, requests: list[LlmBatchTextRequest]) -> list[LlmBatchRequestItem]:
        return [
            LlmBatchRequestItem(
                custom_id=request.custom_id,
                input_items=build_inputs(developer_prompt=request.developer_prompt, user_prompt=request.user_prompt),
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
        return [
            LlmBatchRequestItem(
                custom_id=request.custom_id,
                input_items=build_inputs(developer_prompt=request.developer_prompt, user_prompt=request.user_prompt),
                temperature=STRUCTURED_TEMPERATURE,
                reasoning_effort=STRUCTURED_REASONING_EFFORT,
            )
            for request in requests
        ]

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
                extra={"component": self.__class__.__name__, "model": self._model, "request_kind": request_kind},
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
            raise StructuredLlmError(msg, suggestion="Pass a Pydantic response schema to the LLM service")
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
        payload_extra = _build_json_payload_log_extra(payload=payload)
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
        payload_extra = _build_text_payload_log_extra(content=content)
        if extra is not None:
            payload_extra.update(extra)
        self._log_payload_metadata(message=message, extra={"debug_label": label, **payload_extra})

    def _log_payload_metadata(self, *, message: str, extra: dict[str, object]) -> None:
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
                extra={"component": self.__class__.__name__, "model": self._model, "debug_label": label},
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


def _build_json_payload_log_extra(*, payload: object) -> dict[str, object]:
    serialized_payload = json.dumps(payload, ensure_ascii=False, default=str)
    metadata: dict[str, object] = {
        "payload_length": len(serialized_payload),
        "payload_kind": type(payload).__name__,
        "payload_preview_omitted": True,
    }
    if isinstance(payload, dict):
        metadata["payload_keys"] = sorted(str(key) for key in payload)
    return metadata


def _build_text_payload_log_extra(*, content: str) -> dict[str, object]:
    return {"payload_length": len(content), "payload_kind": "text", "payload_preview_omitted": True}


__all__ = ["LlmService"]
