"""Shared internal helpers for the public OpenAI provider adapter façade."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from llmframe.application.exceptions import StructuredLlmResponseError
from llmframe.application.ports import (
    LlmBatchStatus,
    LlmBatchStructuredResultItem,
    LlmBatchSubmission,
    LlmBatchTextResultItem,
)

from .batch import (
    extract_batch_response_json_payload,
    extract_batch_response_text,
    extract_batch_response_usage,
)
from .parsing import extract_message_content, extract_usage

if TYPE_CHECKING:
    from llmframe.application.ports import LlmUsage
    from llmframe.application.ports.llm_provider import JsonSchema
    from llmframe.shared.json_types import JsonValue

    from .transport import OpenAIClientProtocol, ReasoningEffort


class OpenAIProviderBase:
    """Shared OpenAI provider helpers used by sync and batch operations."""

    def __init__(self, *, transport: OpenAIClientProtocol) -> None:
        self._transport = transport

    def extract_text(self, response: object) -> str:
        """Extract text content from an OpenAI response object."""
        try:
            return extract_message_content(response)
        except ValueError as err:
            msg = "LLM response is missing content or has an invalid shape"
            raise StructuredLlmResponseError(msg, suggestion=str(err)) from err

    def extract_usage(self, response: object) -> LlmUsage | None:
        """Extract normalized usage metadata from an OpenAI response object."""
        return extract_usage(response)

    def _to_reasoning_effort(self, reasoning_effort: str | None) -> ReasoningEffort | None:
        """Cast the application reasoning-effort value to the transport type."""
        return cast("ReasoningEffort | None", reasoning_effort)

    def _to_transport_schema(self, schema: JsonSchema) -> dict[str, object]:
        """Cast the application JSON Schema payload to the transport shape."""
        return cast("dict[str, object]", schema)

    def _to_batch_submission(self, *, batch: object, request_count: int) -> LlmBatchSubmission:
        """Map one OpenAI batch object into a normalized submission DTO."""
        batch_object = cast("Any", batch)
        return LlmBatchSubmission(
            batch_id=cast("str", batch_object.id),
            input_file_id=cast("str", batch_object.input_file_id),
            endpoint=cast("str", batch_object.endpoint),
            status=cast("str", batch_object.status),
            request_count=request_count,
            metadata=self._get_batch_metadata(batch_object),
        )

    def _to_batch_status(self, *, batch: object) -> LlmBatchStatus:
        """Map one OpenAI batch object into a normalized status DTO."""
        batch_object = cast("Any", batch)
        return LlmBatchStatus(
            batch_id=cast("str", batch_object.id),
            status=cast("str", batch_object.status),
            output_file_id=cast("str | None", getattr(batch_object, "output_file_id", None)),
            error_file_id=cast("str | None", getattr(batch_object, "error_file_id", None)),
            request_counts=self._get_request_counts(batch_object),
            created_at=cast("int | None", getattr(batch_object, "created_at", None)),
            in_progress_at=cast("int | None", getattr(batch_object, "in_progress_at", None)),
            completed_at=cast("int | None", getattr(batch_object, "completed_at", None)),
            failed_at=cast("int | None", getattr(batch_object, "failed_at", None)),
            expired_at=cast("int | None", getattr(batch_object, "expired_at", None)),
            cancelling_at=cast("int | None", getattr(batch_object, "cancelling_at", None)),
            cancelled_at=cast("int | None", getattr(batch_object, "cancelled_at", None)),
            metadata=self._get_batch_metadata(batch_object),
        )

    @staticmethod
    def _require_output_file_id(*, status: LlmBatchStatus) -> str:
        """Return the required output file ID for a completed batch result lookup."""
        output_file_id = status.output_file_id
        if output_file_id is None:
            msg = "Batch output file is not available"
            raise StructuredLlmResponseError(msg, suggestion=f"Batch status is {status.status}")
        return output_file_id

    def _to_text_result_item(self, *, line: object) -> LlmBatchTextResultItem:
        """Map one parsed output line into a plain-text result item."""
        line_object = cast("Any", line)
        response_body = self._get_response_body(line_object)
        return LlmBatchTextResultItem(
            custom_id=cast("str", line_object.custom_id),
            content=None if response_body is None else extract_batch_response_text(response_body=response_body),
            usage=None if response_body is None else extract_batch_response_usage(response_body=response_body),
            error=self._get_line_error(line_object),
        )

    def _to_structured_result_item(self, *, line: object) -> LlmBatchStructuredResultItem:
        """Map one parsed output line into a structured-output result item."""
        line_object = cast("Any", line)
        response_body = self._get_response_body(line_object)
        return LlmBatchStructuredResultItem(
            custom_id=cast("str", line_object.custom_id),
            payload=None if response_body is None else extract_batch_response_json_payload(response_body=response_body),
            usage=None if response_body is None else extract_batch_response_usage(response_body=response_body),
            error=self._get_line_error(line_object),
        )

    @staticmethod
    def _get_batch_metadata(batch_object: object) -> dict[str, JsonValue] | None:
        """Return normalized batch metadata when the SDK object provides it."""
        return cast("dict[str, JsonValue] | None", getattr(batch_object, "metadata", None))

    @staticmethod
    def _get_request_counts(batch_object: object) -> dict[str, int] | None:
        """Return normalized request counts when the SDK object provides them."""
        request_counts = getattr(batch_object, "request_counts", None)
        if request_counts is None:
            return None
        return {
            "completed": cast("int", getattr(request_counts, "completed", 0)),
            "failed": cast("int", getattr(request_counts, "failed", 0)),
            "total": cast("int", getattr(request_counts, "total", 0)),
        }

    @staticmethod
    def _get_response_body(line_object: object) -> object | None:
        """Return the parsed response body for one batch output line."""
        return getattr(line_object, "response_body", None)

    @staticmethod
    def _get_line_error(line_object: object) -> str | None:
        """Return the provider-reported error for one batch output line."""
        return cast("str | None", getattr(line_object, "error", None))
