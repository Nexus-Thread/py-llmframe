"""Shared internal base implementation for the public LLM adapter façade."""

from __future__ import annotations

import base64
import logging
import mimetypes
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, cast

from llmframe.application.ports import (
    LlmBatchRequestItem,
    LlmContentPart,
    LlmInputItem,
    StoredLlmBatchRequest,
)

from .dto import LlmImageFileInputPart, LlmImageUrlInputPart, LlmTextInputPart
from .exceptions import StructuredLlmBatchError, StructuredLlmError
from .logging_utils import build_json_payload_log_extra, build_text_payload_log_extra

if TYPE_CHECKING:
    from pydantic import BaseModel

    from llmframe.application.ports import (
        BatchRequestStorePort,
        JsonArtifactWriterPort,
        LlmBatchSubmission,
        LlmProviderPort,
        StructuredOutputSchema,
    )
    from llmframe.shared.json_types import JsonValue

    from .dto import LlmBatchStructuredRequest, LlmBatchTextRequest

LOGGER = logging.getLogger(__name__)

REQUEST_DEBUG_LABEL = "request_payload"
RESPONSE_TEXT_DEBUG_LABEL = "response_text"
PARSED_RESPONSE_DEBUG_LABEL = "parsed_response_payload"
STRUCTURED_TEMPERATURE = 0
STRUCTURED_REASONING_EFFORT = "none"
RESPONSES_ENDPOINT = "/v1/responses"


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

    def _build_inputs(self, *, developer_prompt: str, user_prompt: str) -> list[LlmInputItem]:
        return [
            {"role": "developer", "content": developer_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _build_multimodal_inputs(
        self,
        *,
        developer_prompt: str,
        user_input_parts: list[LlmTextInputPart | LlmImageUrlInputPart | LlmImageFileInputPart],
    ) -> list[LlmInputItem]:
        return [
            {"role": "developer", "content": developer_prompt},
            {"role": "user", "content": self._build_user_content_parts(user_input_parts=user_input_parts)},
        ]

    def _build_user_content_parts(
        self,
        *,
        user_input_parts: list[LlmTextInputPart | LlmImageUrlInputPart | LlmImageFileInputPart],
    ) -> list[LlmContentPart]:
        content_parts: list[LlmContentPart] = []
        for input_part in user_input_parts:
            if isinstance(input_part, LlmTextInputPart):
                content_parts.append({"type": "input_text", "text": input_part.text})
                continue
            if isinstance(input_part, LlmImageUrlInputPart):
                content_parts.append({"type": "input_image", "image_url": input_part.url})
                continue
            if isinstance(input_part, LlmImageFileInputPart):
                content_parts.append({"type": "input_image", "image_url": self._build_image_data_url(input_part.path)})
                continue

            msg = f"Unsupported multimodal input part: {type(input_part).__name__}"
            raise StructuredLlmError(msg, suggestion="Pass only text, image URL, or local image file input parts")
        return content_parts

    def _build_image_data_url(self, image_path: str | Path) -> str:
        file_path = Path(image_path)
        if not file_path.exists():
            msg = f"Image file does not exist: {file_path}"
            raise StructuredLlmError(msg, suggestion="Pass a valid local image file path")
        if not file_path.is_file():
            msg = f"Image path is not a file: {file_path}"
            raise StructuredLlmError(msg, suggestion="Pass a path to a regular image file")

        mime_type, _ = mimetypes.guess_type(file_path.name)
        if mime_type is None or not mime_type.startswith("image/"):
            msg = f"Unsupported image file type: {file_path}"
            raise StructuredLlmError(msg, suggestion="Use a local image file with a recognized image extension")

        try:
            image_bytes = file_path.read_bytes()
        except OSError as err:
            msg = f"Failed to read image file: {file_path}"
            raise StructuredLlmError(msg, suggestion="Ensure the image file is readable") from err

        encoded = base64.b64encode(image_bytes).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"

    def _build_batch_text_requests(self, *, requests: list[LlmBatchTextRequest]) -> list[LlmBatchRequestItem]:
        return [
            LlmBatchRequestItem(
                custom_id=request.custom_id,
                input_items=self._build_inputs(
                    developer_prompt=request.developer_prompt,
                    user_prompt=request.user_prompt,
                ),
                temperature=request.temperature,
                reasoning_effort=request.reasoning_effort,
            )
            for request in requests
        ]

    def _build_batch_structured_requests(
        self,
        *,
        requests: list[LlmBatchStructuredRequest],
    ) -> list[LlmBatchRequestItem]:
        return [
            LlmBatchRequestItem(
                custom_id=request.custom_id,
                input_items=self._build_inputs(
                    developer_prompt=request.developer_prompt,
                    user_prompt=request.user_prompt,
                ),
                temperature=STRUCTURED_TEMPERATURE,
                reasoning_effort=STRUCTURED_REASONING_EFFORT,
            )
            for request in requests
        ]

    def _build_text_request_payload(
        self,
        *,
        inputs: list[LlmInputItem],
        temperature: float | None,
        reasoning_effort: str | None,
    ) -> dict[str, object]:
        payload: dict[str, object] = {
            "model": self._model,
            "input": inputs,
            "text": {"format": {"type": "text"}},
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if reasoning_effort is not None:
            payload["reasoning"] = {"effort": reasoning_effort}
        return payload

    def _build_structured_request_payload(
        self,
        *,
        inputs: list[LlmInputItem],
        schema_name: str,
        schema: dict[str, object],
    ) -> dict[str, object]:
        return {
            "model": self._model,
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

    def _build_batch_text_request_payload(self, *, requests: list[LlmBatchRequestItem]) -> dict[str, object]:
        return {
            "endpoint": RESPONSES_ENDPOINT,
            "request_count": len(requests),
            "requests": [
                {
                    "custom_id": request.custom_id,
                    "body": self._build_text_request_payload(
                        inputs=request.input_items,
                        temperature=request.temperature,
                        reasoning_effort=request.reasoning_effort,
                    ),
                }
                for request in requests
            ],
        }

    def _build_batch_structured_request_payload(
        self,
        *,
        requests: list[LlmBatchRequestItem],
        schema_name: str,
        schema: dict[str, object],
    ) -> dict[str, object]:
        return {
            "endpoint": RESPONSES_ENDPOINT,
            "request_count": len(requests),
            "requests": [
                {
                    "custom_id": request.custom_id,
                    "body": self._build_structured_request_payload(
                        inputs=request.input_items,
                        schema_name=schema_name,
                        schema=schema,
                    ),
                }
                for request in requests
            ],
        }

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

    def _schema_name(self, schema_model: type[BaseModel]) -> str:
        return schema_model.__name__

    def _build_response_schema(self, schema_model: type[BaseModel]) -> dict[str, object]:
        raw_schema = cast("dict[str, object]", schema_model.model_json_schema())
        return cast("dict[str, object]", self._normalize_schema_node(raw_schema))

    def _normalize_schema_properties(self, properties: dict[object, object]) -> dict[str, object]:
        normalized_properties: dict[str, object] = {}
        for field_name, field_schema in properties.items():
            if isinstance(field_schema, dict) and field_schema.get("internal") is True:
                continue
            normalized_properties[str(field_name)] = self._normalize_schema_node(field_schema)
        return normalized_properties

    def _finalize_normalized_schema_object(self, normalized: dict[str, object]) -> dict[str, object]:
        if "$ref" in normalized:
            return {"$ref": normalized["$ref"]}

        properties = normalized.get("properties")
        if isinstance(properties, dict):
            normalized["additionalProperties"] = False
            required_fields = normalized.get("required")
            if isinstance(required_fields, list):
                normalized["required"] = [field_name for field_name in required_fields if field_name in properties]
        return normalized

    def _normalize_schema_node(self, node: object) -> object:
        if isinstance(node, list):
            return [self._normalize_schema_node(item) for item in node]
        if not isinstance(node, dict):
            return node

        normalized: dict[str, object] = {}
        for key, value in node.items():
            if key == "properties" and isinstance(value, dict):
                normalized[key] = self._normalize_schema_properties(value)
                continue
            normalized[key] = self._normalize_schema_node(value)
        return self._finalize_normalized_schema_object(normalized)

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
