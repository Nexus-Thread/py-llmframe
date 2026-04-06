"""Shared LLM adapter for structured extraction and text generation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

from .dto import LlmTextCompletionResult, StructuredLlmJsonCompletionResult
from .exceptions import StructuredLlmError
from .logging_utils import build_json_payload_log_extra, build_text_payload_log_extra
from .response_parser import parse_json_object

if TYPE_CHECKING:
    from pydantic import BaseModel

    from llmframe.adapters.output.persistence import JsonWriterProtocol
    from llmframe.application.ports import LlmProviderPort, StructuredOutputSchema
    from llmframe.application.ports.llm_provider import JsonSchema
    from llmframe.shared.json_types import JsonValue

LOGGER = logging.getLogger(__name__)

REQUEST_DEBUG_LABEL = "request_payload"
RESPONSE_TEXT_DEBUG_LABEL = "response_text"
PARSED_RESPONSE_DEBUG_LABEL = "parsed_response_payload"


class LlmAdapter:
    """Generate structured JSON payloads and plain-text responses."""

    def __init__(
        self,
        *,
        client: LlmProviderPort,
        model: str,
        debug_json_writer: JsonWriterProtocol | None = None,
        debug_json_enabled: bool = False,
    ) -> None:
        """Store transport client and runtime configuration."""
        self._client = client
        self._model = model
        self._api_surface = "responses"
        self._debug_json_writer = debug_json_writer
        self._debug_json_enabled = debug_json_enabled

    def generate_text(
        self,
        *,
        developer_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        reasoning_effort: str | None = None,
    ) -> LlmTextCompletionResult:
        """Return plain-text content together with token-usage metadata."""
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
        """Return parsed JSON payload together with token usage metadata."""
        inputs = self._build_inputs(developer_prompt=developer_prompt, user_prompt=user_prompt)
        schema_type = self._require_response_schema(response_schema)
        schema_name = self._schema_name(schema_type)
        schema = self._build_response_schema(schema_type)
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
            temperature=0,
            reasoning_effort="none",
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

    def _build_inputs(self, *, developer_prompt: str, user_prompt: str) -> list[dict[str, str]]:
        """Build structured LLM inputs for the completion request."""
        return [
            {"role": "developer", "content": developer_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _build_text_request_payload(
        self,
        *,
        inputs: list[dict[str, str]],
        temperature: float | None,
        reasoning_effort: str | None,
    ) -> dict[str, object]:
        """Build metadata-safe text request payload details for logging/debug output."""
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
        inputs: list[dict[str, str]],
        schema_name: str,
        schema: dict[str, object],
    ) -> dict[str, object]:
        """Build metadata-safe structured request payload details for logging/debug output."""
        return {
            "model": self._model,
            "input": inputs,
            "reasoning": {"effort": "none"},
            "temperature": 0,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                }
            },
        }

    def _require_response_schema(self, response_schema: StructuredOutputSchema | None) -> StructuredOutputSchema:
        """Return the schema required for structured-output requests."""
        if response_schema is None:
            msg = "Structured output requests require a response schema"
            raise StructuredLlmError(msg, suggestion="Pass a Pydantic response schema to the LLM adapter")
        return response_schema

    def _schema_name(self, schema_type: type[BaseModel]) -> str:
        """Return a stable schema name for Structured Outputs requests."""
        return schema_type.__name__

    def _build_response_schema(self, schema_type: type[BaseModel]) -> dict[str, object]:
        """Return a JSON schema suitable for Structured Outputs requests."""
        raw_schema = cast("dict[str, object]", schema_type.model_json_schema())
        return cast("dict[str, object]", self._normalize_schema_node(raw_schema))

    def _normalize_schema_node(self, node: object) -> object:
        """Normalize one JSON Schema node for OpenAI Structured Outputs."""
        if isinstance(node, list):
            return [self._normalize_schema_node(item) for item in node]

        if not isinstance(node, dict):
            return node

        normalized: dict[str, object] = {}
        for key, value in node.items():
            if key == "properties" and isinstance(value, dict):
                filtered_properties: dict[str, object] = {}
                for field_name, field_schema in value.items():
                    if isinstance(field_schema, dict) and field_schema.get("internal") is True:
                        continue
                    filtered_properties[field_name] = self._normalize_schema_node(field_schema)
                normalized[key] = filtered_properties
                continue

            normalized[key] = self._normalize_schema_node(value)

        if "$ref" in normalized:
            return {"$ref": normalized["$ref"]}

        properties = normalized.get("properties")
        if isinstance(properties, dict):
            normalized["additionalProperties"] = False
            required_fields = normalized.get("required")
            if isinstance(required_fields, list):
                normalized["required"] = [field_name for field_name in required_fields if field_name in properties]

        return normalized

    def _log_json_stage(
        self,
        *,
        label: str,
        payload: object,
        message: str,
        extra: dict[str, object] | None = None,
    ) -> None:
        """Write and log JSON-stage metadata without logging raw payload content."""
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
        """Write and log text-stage metadata without logging raw content."""
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
        """Log payload metadata without logging raw payload content."""
        log_extra: dict[str, object] = {
            "component": self.__class__.__name__,
            "model": self._model,
            "api_surface": self._api_surface,
        }
        log_extra.update(extra)

        LOGGER.debug(message, extra=log_extra)

    def _write_debug_payload(self, *, label: str, payload: object) -> None:
        """Write a labeled debug payload when debug JSON output is enabled."""
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
