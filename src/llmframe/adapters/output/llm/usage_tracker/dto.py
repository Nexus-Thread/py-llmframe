"""Shared DTOs describing aggregated LLM usage."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LlmUsageSummary:
    """Aggregated token usage and estimated cost for one logical run.

    A nullable numeric field means that at least one recorded request was
    missing the corresponding usage value, so the aggregate cannot be reported
    accurately.
    """

    request_count: int
    short_context_input_tokens: int | None
    short_context_output_tokens: int | None
    long_context_input_tokens: int | None
    long_context_output_tokens: int | None
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    estimated_cost_usd: float | None


@dataclass(frozen=True, slots=True)
class LlmUsageTrackerConfig:
    """Optional pricing and threshold settings for aggregated LLM usage tracking."""

    short_context_input_cost_per_million_tokens: float | None = None
    short_context_output_cost_per_million_tokens: float | None = None
    long_context_input_cost_per_million_tokens: float | None = None
    long_context_output_cost_per_million_tokens: float | None = None
    long_context_input_token_threshold: int | None = None
