"""Typed OpenAI transport payload models."""

from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

Message: TypeAlias = dict[str, str]
JsonSchema: TypeAlias = dict[str, object]
ReasoningEffort: TypeAlias = Literal["none", "low", "medium", "high"]


class OpenAIRequestConfigError(ValueError):
    """Raised when transport payload inputs are invalid."""


class ReasoningConfig(BaseModel):
    """Nested OpenAI reasoning configuration."""

    model_config = ConfigDict(extra="forbid")

    effort: ReasoningEffort


class StructuredSchemaDefinition(BaseModel):
    """Shared strict JSON Schema definition for structured outputs."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    name: str
    strict: bool = True
    schema_definition: JsonSchema = Field(alias="schema", serialization_alias="schema")


class ChatCompletionsResponseFormat(BaseModel):
    """Chat Completions response-format payload."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["json_object", "json_schema"]
    json_schema: StructuredSchemaDefinition | None = None


class ResponsesTextFormat(BaseModel):
    """Responses API text.format payload."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    type: Literal["text", "json_object", "json_schema"]
    name: str | None = None
    strict: bool | None = None
    schema_definition: JsonSchema | None = Field(default=None, alias="schema", serialization_alias="schema")


class ResponsesTextConfig(BaseModel):
    """Responses API text payload wrapper."""

    model_config = ConfigDict(extra="forbid")

    format: ResponsesTextFormat


class ChatCompletionsRequest(BaseModel):
    """Typed Chat Completions request payload."""

    model_config = ConfigDict(extra="forbid")

    model: str
    messages: list[Message]
    temperature: float | None = None
    reasoning: ReasoningConfig | None = None
    response_format: ChatCompletionsResponseFormat | None = None


class ResponsesTextRequest(BaseModel):
    """Typed Responses API request payload for plain text output."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    model: str
    input: list[Message]
    text: ResponsesTextConfig = ResponsesTextConfig(format=ResponsesTextFormat(type="text"))
    temperature: float | None = None
    reasoning: ReasoningConfig | None = None


class ResponsesJsonRequest(BaseModel):
    """Typed Responses API request payload for JSON object output."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    model: str
    input: list[Message]
    text: ResponsesTextConfig = ResponsesTextConfig(format=ResponsesTextFormat(type="json_object"))
    temperature: float | None = None
    reasoning: ReasoningConfig | None = None


class ResponsesStructuredRequest(BaseModel):
    """Typed Responses API request payload for structured JSON Schema output."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    model: str
    input: list[Message]
    text: ResponsesTextConfig
    temperature: float | None = None
    reasoning: ReasoningConfig | None = None


def build_text_response_request_payload(
    *,
    model: str,
    input_items: list[Message],
    temperature: float | None,
    reasoning_effort: ReasoningEffort | None,
) -> dict[str, object]:
    """Build a plain-text Responses API payload for the OpenAI wire format."""
    request_model = ResponsesTextRequest(
        model=model,
        input=input_items,
        temperature=temperature,
        reasoning=build_reasoning_config(reasoning_effort),
    )
    return request_model.model_dump(exclude_none=True, by_alias=True)


def build_structured_response_request_payload(
    *,
    model: str,
    input_items: list[Message],
    structured_schema: StructuredSchemaDefinition,
    temperature: float | None,
    reasoning_effort: ReasoningEffort | None,
) -> dict[str, object]:
    """Build a structured Responses API payload for the OpenAI wire format."""
    request_model = ResponsesStructuredRequest(
        model=model,
        input=input_items,
        text=ResponsesTextConfig(
            format=ResponsesTextFormat(
                type="json_schema",
                name=structured_schema.name,
                strict=structured_schema.strict,
                schema=structured_schema.schema_definition,
            )
        ),
        temperature=temperature,
        reasoning=build_reasoning_config(reasoning_effort),
    )
    return request_model.model_dump(exclude_none=True, by_alias=True)


def build_reasoning_config(reasoning_effort: ReasoningEffort | None) -> ReasoningConfig | None:
    """Return the nested reasoning payload when configured."""
    if reasoning_effort is None:
        return None
    return ReasoningConfig(effort=reasoning_effort)


def build_structured_schema_definition(
    *,
    json_schema_name: str | None,
    json_schema: JsonSchema | None,
) -> StructuredSchemaDefinition:
    """Return the strict JSON Schema payload for structured outputs."""
    if json_schema_name is None:
        msg = "Structured output mode requires json_schema_name"
        raise OpenAIRequestConfigError(msg)
    if json_schema is None:
        msg = "Structured output mode requires json_schema"
        raise OpenAIRequestConfigError(msg)

    return StructuredSchemaDefinition(name=json_schema_name, schema=json_schema)
