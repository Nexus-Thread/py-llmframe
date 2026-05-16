"""OpenAI SDK transport wrapper implementation."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Literal, Protocol, TypeAlias, cast

from .batch_io import download_batch_output, parse_output_jsonl, upload_batch_file
from .debug import serialize_debug_payload, write_debug_payload
from .payload_builders import (
    ChatCompletionsRequest,
    ChatCompletionsResponseFormat,
    JsonSchema,
    Message,
    OpenAIRequestConfigError,
    ReasoningEffort,
    ResponsesJsonRequest,
    ResponsesStructuredRequest,
    ResponsesTextConfig,
    ResponsesTextFormat,
    ResponsesTextRequest,
    StructuredSchemaDefinition,
    build_reasoning_config,
    build_structured_schema_definition,
)
from .protocols import OpenAIClientProtocol
from .retry import DEFAULT_BACKOFF_FACTOR, DEFAULT_MAX_RETRIES, RetryContext, call_with_retries, retry_delay_seconds

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from llmframe.adapters.output.llm.providers.openai.dto import (
        OpenAIBatchFileUpload,
        OpenAIBatchRequestLine,
        OpenAIBatchResultLine,
    )
    from llmframe.application.ports import JsonArtifactWriterPort
    from llmframe.shared.json_types import JsonValue

RequestPayload: TypeAlias = dict[str, object]
ResponseFormatType: TypeAlias = Literal["text", "json_object", "json_schema"]
RequestModel: TypeAlias = (
    ChatCompletionsRequest | ResponsesTextRequest | ResponsesJsonRequest | ResponsesStructuredRequest
)


LOGGER = logging.getLogger(__name__)

REQUEST_DEBUG_LABEL = "request_payload"
RESPONSE_DEBUG_LABEL = "response_payload"


class _ChatCompletionsProtocol(Protocol):
    """Private protocol for the SDK completions namespace."""

    def create(self, **kwargs: object) -> object:
        """Create a completion response from the SDK."""
        ...


class _ChatNamespaceProtocol(Protocol):
    """Private protocol for the SDK chat namespace."""

    @property
    def completions(self) -> _ChatCompletionsProtocol:
        """Return the completions API namespace."""
        ...


class _ResponsesNamespaceProtocol(Protocol):
    """Private protocol for the SDK responses namespace."""

    def create(self, **kwargs: object) -> object:
        """Create a response object from the SDK."""
        ...


class _FilesNamespaceProtocol(Protocol):
    """Private protocol for the SDK files namespace."""

    def create(self, *, file: object, purpose: str) -> object:
        """Upload one file object to the SDK."""
        ...

    def content(self, file_id: str) -> object:
        """Download one file content payload from the SDK."""
        ...


class _BatchesNamespaceProtocol(Protocol):
    """Private protocol for the SDK batches namespace."""

    def create(
        self,
        *,
        completion_window: str,
        endpoint: str,
        input_file_id: str,
        metadata: dict[str, str] | None = None,
    ) -> object:
        """Create one batch through the SDK."""
        ...

    def retrieve(self, batch_id: str) -> object:
        """Retrieve one batch through the SDK."""
        ...

    def cancel(self, batch_id: str) -> object:
        """Cancel one batch through the SDK."""
        ...


class _OpenAISDKClientProtocol(Protocol):
    """Private protocol for minimal OpenAI SDK client shape."""

    @property
    def chat(self) -> _ChatNamespaceProtocol:
        """Return the chat API namespace."""
        ...

    @property
    def responses(self) -> _ResponsesNamespaceProtocol:
        """Return the responses API namespace."""
        ...

    @property
    def files(self) -> _FilesNamespaceProtocol:
        """Return the files API namespace."""
        ...

    @property
    def batches(self) -> _BatchesNamespaceProtocol:
        """Return the batches API namespace."""
        ...


class OpenAIClient(OpenAIClientProtocol):
    """Thin transport wrapper around the OpenAI SDK client."""

    def __init__(
        self,
        sdk_client: object,
        *,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        sleep: Callable[[float], None] = time.sleep,
        debug_json_writer: JsonArtifactWriterPort | None = None,
        debug_json_enabled: bool = False,
    ) -> None:
        """Store the SDK client and retry configuration."""
        if max_retries < 0:
            msg = "max_retries must be greater than or equal to 0"
            raise ValueError(msg)
        if backoff_factor < 1.0:
            msg = "backoff_factor must be greater than or equal to 1.0"
            raise ValueError(msg)

        self._sdk_client = cast("_OpenAISDKClientProtocol", sdk_client)
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor
        self._sleep = sleep
        self._debug_json_writer = debug_json_writer
        self._debug_json_enabled = debug_json_enabled

    def create_chat_completion(
        self,
        *,
        model: str,
        messages: list[Message],
        temperature: float | None = None,
        reasoning_effort: ReasoningEffort | None = None,
    ) -> object:
        """Create a plain chat completion without enforced response format."""
        request_model = ChatCompletionsRequest(
            model=model,
            messages=messages,
            temperature=temperature,
            reasoning=build_reasoning_config(reasoning_effort),
        )
        return self._execute_chat_request(
            model=model,
            request_model=request_model,
        )

    def create_json_chat_completion(
        self,
        *,
        model: str,
        messages: list[Message],
        temperature: float | None = None,
        reasoning_effort: ReasoningEffort | None = None,
    ) -> object:
        """Create a JSON-formatted chat completion."""
        request_model = ChatCompletionsRequest(
            model=model,
            messages=messages,
            temperature=temperature,
            reasoning=build_reasoning_config(reasoning_effort),
            response_format=self._build_chat_response_format(format_type="json_object"),
        )
        return self._execute_chat_request(
            model=model,
            request_model=request_model,
        )

    def create_structured_chat_completion(
        self,
        *,
        model: str,
        messages: list[Message],
        json_schema_name: str,
        schema: JsonSchema,
        temperature: float | None = None,
        reasoning_effort: ReasoningEffort | None = None,
    ) -> object:
        """Create a chat completion using Structured Outputs JSON Schema mode."""
        request_model = ChatCompletionsRequest(
            model=model,
            messages=messages,
            temperature=temperature,
            reasoning=build_reasoning_config(reasoning_effort),
            response_format=self._build_chat_response_format(
                format_type="json_schema",
                json_schema_name=json_schema_name,
                schema=schema,
            ),
        )
        return self._execute_chat_request(
            model=model,
            request_model=request_model,
        )

    def create_response(
        self,
        *,
        model: str,
        input_items: list[Message],
        temperature: float | None = None,
        reasoning_effort: ReasoningEffort | None = None,
    ) -> object:
        """Create a plain text response via the Responses API."""
        request_model = ResponsesTextRequest(
            model=model,
            input=input_items,
            temperature=temperature,
            reasoning=build_reasoning_config(reasoning_effort),
        )
        return self._execute_responses_request(
            model=model,
            request_model=request_model,
        )

    def create_json_response(
        self,
        *,
        model: str,
        input_items: list[Message],
        temperature: float | None = None,
        reasoning_effort: ReasoningEffort | None = None,
    ) -> object:
        """Create a JSON-formatted response via the Responses API."""
        request_model = ResponsesJsonRequest(
            model=model,
            input=input_items,
            temperature=temperature,
            reasoning=build_reasoning_config(reasoning_effort),
        )
        return self._execute_responses_request(
            model=model,
            request_model=request_model,
        )

    def create_structured_response(
        self,
        *,
        model: str,
        input_items: list[Message],
        json_schema_name: str,
        schema: JsonSchema,
        temperature: float | None = None,
        reasoning_effort: ReasoningEffort | None = None,
    ) -> object:
        """Create a structured response via the Responses API."""
        request_model = ResponsesStructuredRequest(
            model=model,
            input=input_items,
            text=self._build_responses_text_config(
                format_type="json_schema",
                json_schema_name=json_schema_name,
                schema=schema,
            ),
            temperature=temperature,
            reasoning=build_reasoning_config(reasoning_effort),
        )
        return self._execute_responses_request(
            model=model,
            request_model=request_model,
        )

    def upload_batch_file(self, *, lines: Sequence[OpenAIBatchRequestLine]) -> OpenAIBatchFileUpload:
        """Upload a JSONL input file for the OpenAI Batch API."""
        return upload_batch_file(
            lines=lines,
            upload=lambda file_payload: self._call_with_retries(
                model="batch",
                action_name="batch_file_upload",
                request=lambda: self._sdk_client.files.create(file=file_payload, purpose="batch"),
            ),
        )

    def create_response_batch(self, *, input_file_id: str, metadata: dict[str, str] | None = None) -> object:
        """Create one OpenAI Batch API job targeting the Responses endpoint."""
        return self._call_with_retries(
            model="batch",
            action_name="batch_create",
            request=lambda: self._sdk_client.batches.create(
                completion_window="24h",
                endpoint="/v1/responses",
                input_file_id=input_file_id,
                metadata=metadata,
            ),
        )

    def retrieve_batch(self, *, batch_id: str) -> object:
        """Retrieve one previously submitted batch."""
        return self._call_with_retries(
            model="batch",
            action_name="batch_retrieve",
            request=lambda: self._sdk_client.batches.retrieve(batch_id),
        )

    def cancel_batch(self, *, batch_id: str) -> object:
        """Cancel one previously submitted batch."""
        return self._call_with_retries(
            model="batch",
            action_name="batch_cancel",
            request=lambda: self._sdk_client.batches.cancel(batch_id),
        )

    def download_batch_output(self, *, file_id: str) -> str:
        """Download the content of one batch output file as text."""
        content = self._call_with_retries(
            model="batch",
            action_name="batch_output_download",
            request=lambda: self._sdk_client.files.content(file_id),
        )
        return download_batch_output(content=content)

    def parse_batch_output_jsonl(self, *, content: str) -> list[OpenAIBatchResultLine]:
        """Parse JSONL batch output content into normalized result lines."""
        return parse_output_jsonl(content=content)

    def _execute_chat_request(
        self,
        *,
        model: str,
        request_model: ChatCompletionsRequest,
    ) -> object:
        """Execute a chat-completions request with shared debug and retry handling."""
        request_payload = self._prepare_request_payload(request_model)
        return self._call_with_retries(
            model=model,
            action_name="completion",
            request=lambda: self._create_and_capture_response(
                request=lambda: self._sdk_client.chat.completions.create(**request_payload)
            ),
        )

    def _execute_responses_request(
        self,
        *,
        model: str,
        request_model: ResponsesTextRequest | ResponsesJsonRequest | ResponsesStructuredRequest,
    ) -> object:
        """Execute a Responses API request with shared debug and retry handling."""
        request_payload = self._prepare_request_payload(request_model)
        return self._call_with_retries(
            model=model,
            action_name="response",
            request=lambda: self._create_and_capture_response(
                request=lambda: self._sdk_client.responses.create(**request_payload)
            ),
        )

    def _build_chat_response_format(
        self,
        *,
        format_type: ResponseFormatType,
        json_schema_name: str | None = None,
        schema: dict[str, object] | None = None,
    ) -> ChatCompletionsResponseFormat | None:
        """Build the Chat Completions response format for the selected mode."""
        if format_type == "json_object":
            return ChatCompletionsResponseFormat(type="json_object")
        if format_type == "json_schema":
            return ChatCompletionsResponseFormat(
                type="json_schema",
                json_schema=self._build_schema_definition(
                    json_schema_name=json_schema_name,
                    schema=schema,
                ),
            )

        msg = f"Unsupported chat response format: {format_type}"
        raise OpenAIRequestConfigError(msg)

    def _build_responses_text_config(
        self,
        *,
        format_type: ResponseFormatType,
        json_schema_name: str | None = None,
        schema: dict[str, object] | None = None,
    ) -> ResponsesTextConfig:
        """Build the Responses API text configuration for the selected mode."""
        if format_type == "text":
            return ResponsesTextConfig(format=ResponsesTextFormat(type="text"))
        if format_type == "json_object":
            return ResponsesTextConfig(format=ResponsesTextFormat(type="json_object"))
        if format_type == "json_schema":
            schema_definition = self._build_schema_definition(
                json_schema_name=json_schema_name,
                schema=schema,
            )
            return ResponsesTextConfig(
                format=ResponsesTextFormat(
                    type="json_schema",
                    name=schema_definition.name,
                    strict=schema_definition.strict,
                    schema=schema_definition.schema_definition,
                )
            )

        msg = f"Unsupported responses format: {format_type}"
        raise OpenAIRequestConfigError(msg)

    def _build_schema_definition(
        self,
        *,
        json_schema_name: str | None,
        schema: dict[str, object] | None,
    ) -> StructuredSchemaDefinition:
        """Build normalized structured-output schema metadata."""
        return build_structured_schema_definition(
            json_schema_name=json_schema_name,
            json_schema=schema,
        )

    def _dump_request_model(
        self,
        request_model: RequestModel,
    ) -> RequestPayload:
        """Serialize a typed request model for the OpenAI SDK."""
        return cast("RequestPayload", request_model.model_dump(exclude_none=True, by_alias=True))

    def _prepare_request_payload(self, request_model: RequestModel) -> RequestPayload:
        """Serialize and optionally persist a request payload debug snapshot."""
        request_payload = self._dump_request_model(request_model)
        self._write_debug_payload(label=REQUEST_DEBUG_LABEL, payload=cast("JsonValue", request_payload))
        return request_payload

    def _create_and_capture_response(self, *, request: Callable[[], object]) -> object:
        """Execute a request and optionally persist a debug snapshot of the raw response."""
        response = request()
        self._write_debug_payload(
            label=RESPONSE_DEBUG_LABEL,
            payload=self._serialize_debug_payload(response),
        )
        return response

    def _serialize_debug_payload(self, payload: object) -> JsonValue:
        """Convert a transport payload into a JSON-writable debug snapshot."""
        return serialize_debug_payload(payload)

    def _write_debug_payload(self, *, label: str, payload: JsonValue) -> None:
        """Persist a labeled debug payload when transport debug output is enabled."""
        write_debug_payload(
            debug_json_enabled=self._debug_json_enabled,
            debug_json_writer=self._debug_json_writer,
            label=label,
            payload=payload,
            component=self.__class__.__name__,
        )

    def _build_retry_log_extra(
        self,
        *,
        model: str,
        attempt: int,
        total_attempts: int,
    ) -> RequestPayload:
        """Return retry metadata shared by warning and error logs."""
        return {
            "component": self.__class__.__name__,
            "model": model,
            "attempt": attempt,
            "total_attempts": total_attempts,
            "max_retries": self._max_retries,
        }

    def _log_final_failure(self, *, action_name: str, model: str, attempt: int, total_attempts: int) -> None:
        """Log the final transport failure after all retries are exhausted."""
        LOGGER.exception(
            "OpenAI %s failed after exhausting retries",
            action_name,
            extra=self._build_retry_log_extra(
                model=model,
                attempt=attempt,
                total_attempts=total_attempts,
            ),
        )

    def _log_retry(self, *, action_name: str, model: str, attempt: int, total_attempts: int, delay: float) -> None:
        """Log retry metadata for a transient transport failure."""
        extra = self._build_retry_log_extra(
            model=model,
            attempt=attempt,
            total_attempts=total_attempts,
        )
        extra["attempts_remaining"] = total_attempts - attempt
        extra["retry_delay_seconds"] = delay
        LOGGER.warning(
            "OpenAI %s attempt failed; retrying",
            action_name,
            extra=extra,
        )

    def _call_with_retries(
        self,
        *,
        model: str,
        action_name: str,
        request: Callable[[], object],
    ) -> object:
        """Execute an SDK request with shared retry and logging behavior."""
        return call_with_retries(
            request=request,
            sleep=self._sleep,
            context=RetryContext(
                action_name=action_name,
                model=model,
                max_retries=self._max_retries,
                backoff_factor=self._backoff_factor,
                component=self.__class__.__name__,
            ),
        )

    def _retry_delay_seconds(self, attempt: int) -> float:
        """Return the exponential backoff delay for a retry attempt."""
        return retry_delay_seconds(backoff_factor=self._backoff_factor, attempt=attempt)
