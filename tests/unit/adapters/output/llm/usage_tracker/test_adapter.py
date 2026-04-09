"""Unit tests for provider-agnostic aggregated LLM usage tracking."""

from __future__ import annotations

import pytest

from llmframe.adapters.output.llm import (
    LlmUsageSummary,
    LlmUsageTracker,
    LlmUsageTrackerConfig,
)
from llmframe.application.ports import LlmUsage


def test_usage_tracker_aggregates_tokens_and_estimated_cost() -> None:
    """Usage tracker aggregates multiple calls into one immutable summary."""
    tracker = LlmUsageTracker(
        config=LlmUsageTrackerConfig(
            short_context_input_cost_per_million_tokens=2.5,
            short_context_output_cost_per_million_tokens=10.0,
        ),
    )

    tracker.record_usage(usage=LlmUsage(input_tokens=1000, output_tokens=200, total_tokens=1200))
    tracker.record_usage(usage=LlmUsage(input_tokens=500, output_tokens=100, total_tokens=600))

    assert tracker.build_summary() == LlmUsageSummary(
        request_count=2,
        short_context_input_tokens=1500,
        short_context_output_tokens=300,
        long_context_input_tokens=0,
        long_context_output_tokens=0,
        input_tokens=1500,
        output_tokens=300,
        total_tokens=1800,
        estimated_cost_usd=0.00675,
    )


def test_usage_tracker_returns_unavailable_fields_when_usage_missing() -> None:
    """Usage tracker preserves request count even when usage metadata is absent."""
    tracker = LlmUsageTracker(config=LlmUsageTrackerConfig())

    tracker.record_usage(usage=None)

    assert tracker.build_summary() == LlmUsageSummary(
        request_count=1,
        short_context_input_tokens=None,
        short_context_output_tokens=None,
        long_context_input_tokens=None,
        long_context_output_tokens=None,
        input_tokens=None,
        output_tokens=None,
        total_tokens=None,
        estimated_cost_usd=None,
    )


def test_usage_tracker_reset_clears_previous_summary() -> None:
    """Usage tracker reset clears all accumulated usage state."""
    tracker = LlmUsageTracker(config=LlmUsageTrackerConfig())
    tracker.record_usage(usage=LlmUsage(input_tokens=10, output_tokens=5, total_tokens=15))

    tracker.reset()

    assert tracker.build_summary() is None


def test_usage_tracker_recomputes_total_tokens_from_complete_input_and_output_counts() -> None:
    """Usage tracker derives total tokens when only the aggregate total is missing."""
    tracker = LlmUsageTracker(config=LlmUsageTrackerConfig())

    tracker.record_usage(usage=LlmUsage(input_tokens=10, output_tokens=5, total_tokens=None))
    tracker.record_usage(usage=LlmUsage(input_tokens=20, output_tokens=15, total_tokens=None))

    assert tracker.build_summary() == LlmUsageSummary(
        request_count=2,
        short_context_input_tokens=30,
        short_context_output_tokens=20,
        long_context_input_tokens=0,
        long_context_output_tokens=0,
        input_tokens=30,
        output_tokens=20,
        total_tokens=50,
        estimated_cost_usd=None,
    )


@pytest.mark.parametrize(
    (
        "short_context_input_cost_per_million_tokens",
        "short_context_output_cost_per_million_tokens",
    ),
    [(-1.0, None), (None, -1.0)],
)
def test_usage_tracker_rejects_negative_pricing(
    short_context_input_cost_per_million_tokens: float | None,
    short_context_output_cost_per_million_tokens: float | None,
) -> None:
    """Usage tracker rejects negative pricing values."""
    with pytest.raises(ValueError, match="greater than or equal to 0"):
        LlmUsageTracker(
            config=LlmUsageTrackerConfig(
                short_context_input_cost_per_million_tokens=short_context_input_cost_per_million_tokens,
                short_context_output_cost_per_million_tokens=short_context_output_cost_per_million_tokens,
            ),
        )


def test_usage_tracker_uses_long_context_pricing_for_large_input_requests() -> None:
    """Usage tracker switches pricing tiers based on request input token size."""
    tracker = LlmUsageTracker(
        config=LlmUsageTrackerConfig(
            short_context_input_cost_per_million_tokens=2.0,
            short_context_output_cost_per_million_tokens=8.0,
            long_context_input_cost_per_million_tokens=4.0,
            long_context_output_cost_per_million_tokens=16.0,
            long_context_input_token_threshold=1000,
        ),
    )

    tracker.record_usage(usage=LlmUsage(input_tokens=999, output_tokens=100, total_tokens=1099))
    tracker.record_usage(usage=LlmUsage(input_tokens=1000, output_tokens=100, total_tokens=1100))

    assert tracker.build_summary() == LlmUsageSummary(
        request_count=2,
        short_context_input_tokens=999,
        short_context_output_tokens=100,
        long_context_input_tokens=1000,
        long_context_output_tokens=100,
        input_tokens=1999,
        output_tokens=200,
        total_tokens=2199,
        estimated_cost_usd=0.008398,
    )


def test_usage_tracker_rejects_incomplete_pricing_tier_configuration() -> None:
    """Usage tracker requires both input and output prices for each configured tier."""
    with pytest.raises(ValueError, match="Both input and output token prices must be configured"):
        LlmUsageTracker(config=LlmUsageTrackerConfig(short_context_input_cost_per_million_tokens=2.5))
