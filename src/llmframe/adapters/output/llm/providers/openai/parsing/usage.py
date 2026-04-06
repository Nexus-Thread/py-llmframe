"""Public helpers for extracting usage metadata from OpenAI responses."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator

from llmframe.application.ports import LlmUsage


class _UsagePayload(BaseModel):
    """Internal normalized usage payload parsed from SDK response objects."""

    model_config = ConfigDict(from_attributes=True)

    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None

    @field_validator(
        "prompt_tokens",
        "completion_tokens",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        mode="before",
    )
    @classmethod
    def _validate_optional_int(cls, value: object) -> int | None:
        """Keep only integer token counts from loosely typed SDK payloads."""
        return value if isinstance(value, int) else None

    def to_usage(self) -> LlmUsage:
        """Convert the normalized payload into the exported DTO."""
        if self.input_tokens is not None or self.output_tokens is not None:
            return LlmUsage(
                input_tokens=self.input_tokens,
                output_tokens=self.output_tokens,
                total_tokens=self.total_tokens,
            )

        return LlmUsage(
            input_tokens=self.prompt_tokens,
            output_tokens=self.completion_tokens,
            total_tokens=self.total_tokens,
        )


def extract_usage(response: object) -> LlmUsage | None:
    """Extract token usage metadata from a model response."""
    usage = getattr(response, "usage", None)
    if usage is None:
        return None

    return _UsagePayload.model_validate(usage).to_usage()
