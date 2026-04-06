"""OpenAI SDK transport wrapper implementation."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Literal, Protocol, TypeAlias, cast

from openai import APIError

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

if TYPE_CHECKING:
    from collections.abc import Callable
if TYPE_CHECKING:
    from llmframe.adapters.output.persistence import JsonWriterProtocol
    from llmframe.shared.json_types import JsonValue

RequestPayload: TypeAlias = dict[str, object]
ResponseFormatType: TypeAlias = Literal["text", "json_object", "json_schema"]


LOGGER = logging.getLogger(__name__)

DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 2.0

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


class OpenAIClient(OpenAIClientProtocol):
    """Thin transport wrapper around the OpenAI SDK client."""

    def __init__(
        self,
        sdk_client: object,
        *,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        sleep: Callable[[float], None] = time.sleep,
        debug_json_writer: JsonWriterProtocol | None = None,
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

    def _execute_chat_request(
        self,
        *,
        model: str,
        request_model: ChatCompletionsRequest,
    ) -> object:
        """Execute a chat-completions request with shared debug and retry handling."""
        request_payload = self._dump_request_model(request_model)
        self._write_debug_payload(label=REQUEST_DEBUG_LABEL, payload=cast("JsonValue", request_payload))
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
        request_payload = self._dump_request_model(request_model)
        self._write_debug_payload(label=REQUEST_DEBUG_LABEL, payload=cast("JsonValue", request_payload))
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
        request_model: ChatCompletionsRequest
        | ResponsesTextRequest
        | ResponsesJsonRequest
        | ResponsesStructuredRequest,
    ) -> RequestPayload:
        """Serialize a typed request model for the OpenAI SDK."""
        return cast("RequestPayload", request_model.model_dump(exclude_none=True, by_alias=True))

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
        if isinstance(payload, dict | list | str | int | float | bool) or payload is None:
            return cast("JsonValue", payload)

        model_dump = getattr(payload, "model_dump", None)
        if callable(model_dump):
            return cast("JsonValue", model_dump(exclude_none=True, by_alias=True))

        to_dict = getattr(payload, "to_dict", None)
        if callable(to_dict):
            return cast("JsonValue", to_dict())

        return {"repr": repr(payload)}

    def _write_debug_payload(self, *, label: str, payload: JsonValue) -> None:
        """Persist a labeled debug payload when transport debug output is enabled."""
        if not self._debug_json_enabled or self._debug_json_writer is None:
            return

        try:
            self._debug_json_writer.write_json(label=label, payload=payload)
        except (OSError, TypeError, ValueError):
            LOGGER.warning(
                "Failed to write OpenAI transport debug payload",
                extra={
                    "component": self.__class__.__name__,
                    "debug_label": label,
                },
                exc_info=True,
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
        total_attempts = self._max_retries + 1
        for attempt in range(1, total_attempts + 1):
            try:
                return request()
            except APIError:
                if attempt >= total_attempts:
                    self._log_final_failure(
                        action_name=action_name,
                        model=model,
                        attempt=attempt,
                        total_attempts=total_attempts,
                    )
                    raise
                delay = self._retry_delay_seconds(attempt)
                self._log_retry(
                    action_name=action_name,
                    model=model,
                    attempt=attempt,
                    total_attempts=total_attempts,
                    delay=delay,
                )
                self._sleep(delay)

        message = "Unexpected transport retry loop termination"
        raise RuntimeError(message)

    def _retry_delay_seconds(self, attempt: int) -> float:
        """Return the exponential backoff delay for a retry attempt."""
        return self._backoff_factor**attempt
