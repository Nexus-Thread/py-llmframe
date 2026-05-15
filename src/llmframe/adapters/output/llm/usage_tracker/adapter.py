"""Aggregate normalized LLM usage and estimated request cost."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import TYPE_CHECKING

from .dto import LlmUsageSummary, LlmUsageTrackerConfig

if TYPE_CHECKING:
    from llmframe.application.ports import LlmUsage

TOKENS_PER_MILLION = 1_000_000
USD_PRECISION_DIGITS = 12


@dataclass(frozen=True, slots=True)
class _PricingTier:
    """Per-million-token pricing for one context tier."""

    input_cost_per_million_tokens: float
    output_cost_per_million_tokens: float


@dataclass(frozen=True, slots=True)
class _TokenAggregate:
    """Aggregate an optional token value across many requests."""

    value: int = 0
    is_complete: bool = True

    def add(self, value: int | None) -> _TokenAggregate:
        """Return updated aggregate state for one optional token value."""
        if value is None:
            return _TokenAggregate(value=self.value, is_complete=False)
        if not self.is_complete:
            return self
        return _TokenAggregate(value=self.value + value, is_complete=True)

    def as_summary_value(self) -> int | None:
        """Return the aggregate value only when all contributors were complete."""
        if not self.is_complete:
            return None
        return self.value


class LlmUsageTracker:
    """Aggregate normalized usage across multiple LLM calls.

    Provider adapters are responsible for extracting provider-specific usage data
    into the shared ``LlmUsage`` shape. This tracker only aggregates that
    normalized usage.
    """

    _request_count: int
    _short_context_input_tokens: _TokenAggregate
    _short_context_output_tokens: _TokenAggregate
    _long_context_input_tokens: _TokenAggregate
    _long_context_output_tokens: _TokenAggregate
    _input_tokens: _TokenAggregate
    _output_tokens: _TokenAggregate
    _total_tokens: _TokenAggregate
    _estimated_cost_usd: float
    _estimated_cost_complete: bool

    def __init__(
        self,
        *,
        config: LlmUsageTrackerConfig,
    ) -> None:
        """Store optional pricing and initialize empty usage state."""
        self._validate_cost(
            name="short_context_input_cost_per_million_tokens",
            value=config.short_context_input_cost_per_million_tokens,
        )
        self._validate_cost(
            name="short_context_output_cost_per_million_tokens",
            value=config.short_context_output_cost_per_million_tokens,
        )
        self._validate_cost(
            name="long_context_input_cost_per_million_tokens",
            value=config.long_context_input_cost_per_million_tokens,
        )
        self._validate_cost(
            name="long_context_output_cost_per_million_tokens",
            value=config.long_context_output_cost_per_million_tokens,
        )
        self._validate_threshold(value=config.long_context_input_token_threshold)

        self._short_context_pricing = self._build_pricing_tier(
            input_cost_per_million_tokens=config.short_context_input_cost_per_million_tokens,
            output_cost_per_million_tokens=config.short_context_output_cost_per_million_tokens,
        )
        self._long_context_pricing = self._build_pricing_tier(
            input_cost_per_million_tokens=config.long_context_input_cost_per_million_tokens,
            output_cost_per_million_tokens=config.long_context_output_cost_per_million_tokens,
        )
        self._long_context_input_token_threshold = config.long_context_input_token_threshold
        self._lock = Lock()
        self._reset_unlocked()

    def reset(self) -> None:
        """Clear all previously recorded usage state."""
        with self._lock:
            self._reset_unlocked()

    def record_usage(self, *, usage: LlmUsage | None) -> None:
        """Record one normalized usage snapshot."""
        with self._lock:
            self._request_count += 1

            if usage is None:
                self._mark_usage_incomplete()
                return

            self._record_token_counts(usage=usage)
            self._record_estimated_cost(usage=usage)

    def build_summary(self) -> LlmUsageSummary | None:
        """Return aggregated usage for the current run, if any."""
        with self._lock:
            if self._request_count == 0:
                return None

            short_context_input_tokens = self._short_context_input_tokens.as_summary_value()
            short_context_output_tokens = self._short_context_output_tokens.as_summary_value()
            long_context_input_tokens = self._long_context_input_tokens.as_summary_value()
            long_context_output_tokens = self._long_context_output_tokens.as_summary_value()
            input_tokens = self._input_tokens.as_summary_value()
            output_tokens = self._output_tokens.as_summary_value()
            total_tokens = self._build_total_tokens(input_tokens=input_tokens, output_tokens=output_tokens)
            estimated_cost_usd = self._build_estimated_cost_usd()

            return LlmUsageSummary(
                request_count=self._request_count,
                short_context_input_tokens=short_context_input_tokens,
                short_context_output_tokens=short_context_output_tokens,
                long_context_input_tokens=long_context_input_tokens,
                long_context_output_tokens=long_context_output_tokens,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=estimated_cost_usd,
            )

    def _build_total_tokens(self, *, input_tokens: int | None, output_tokens: int | None) -> int | None:
        """Return total tokens from direct totals or complete prompt/completion sums."""
        total_tokens = self._total_tokens.as_summary_value()
        if total_tokens is not None:
            return total_tokens
        if input_tokens is None or output_tokens is None:
            return None
        return input_tokens + output_tokens

    def _build_estimated_cost_usd(self) -> float | None:
        """Return the rounded aggregated cost when it remains complete."""
        if not self._estimated_cost_complete:
            return None
        return round(self._estimated_cost_usd, USD_PRECISION_DIGITS)

    @staticmethod
    def _build_pricing_tier(
        *,
        input_cost_per_million_tokens: float | None,
        output_cost_per_million_tokens: float | None,
    ) -> _PricingTier | None:
        """Return a pricing tier only when both token prices are configured."""
        if input_cost_per_million_tokens is None and output_cost_per_million_tokens is None:
            return None
        if input_cost_per_million_tokens is None or output_cost_per_million_tokens is None:
            msg = "Both input and output token prices must be configured for a pricing tier"
            raise ValueError(msg)
        return _PricingTier(
            input_cost_per_million_tokens=input_cost_per_million_tokens,
            output_cost_per_million_tokens=output_cost_per_million_tokens,
        )

    @staticmethod
    def _validate_threshold(*, value: int | None) -> None:
        """Validate the optional long-context threshold."""
        if value is None or value >= 1:
            return

        msg = "long_context_input_token_threshold must be greater than or equal to 1"
        raise ValueError(msg)

    @staticmethod
    def _estimate_cost(*, usage: LlmUsage, pricing: _PricingTier) -> float | None:
        """Return request cost when both token counts and tier pricing are available."""
        if usage.input_tokens is None or usage.output_tokens is None:
            return None

        input_cost = usage.input_tokens * pricing.input_cost_per_million_tokens / TOKENS_PER_MILLION
        output_cost = usage.output_tokens * pricing.output_cost_per_million_tokens / TOKENS_PER_MILLION
        return input_cost + output_cost

    def _pricing_for_usage(self, *, usage: LlmUsage) -> _PricingTier | None:
        """Return the configured pricing tier for one request."""
        if self._long_context_input_token_threshold is None or usage.input_tokens is None:
            return self._short_context_pricing
        if usage.input_tokens < self._long_context_input_token_threshold:
            return self._short_context_pricing
        return self._long_context_pricing

    @staticmethod
    def _validate_cost(*, name: str, value: float | None) -> None:
        """Validate an optional per-million-token price."""
        if value is None or value >= 0:
            return

        msg = f"{name} must be greater than or equal to 0"
        raise ValueError(msg)

    def _mark_usage_incomplete(self) -> None:
        """Mark all aggregated token counts as incomplete."""
        self._short_context_input_tokens = self._short_context_input_tokens.add(None)
        self._short_context_output_tokens = self._short_context_output_tokens.add(None)
        self._long_context_input_tokens = self._long_context_input_tokens.add(None)
        self._long_context_output_tokens = self._long_context_output_tokens.add(None)
        self._input_tokens = self._input_tokens.add(None)
        self._output_tokens = self._output_tokens.add(None)
        self._total_tokens = self._total_tokens.add(None)
        self._estimated_cost_complete = False

    def _record_token_counts(self, *, usage: LlmUsage) -> None:
        """Record all token counts from one usage snapshot."""
        self._record_tier_token_counts(usage=usage)
        self._record_input_tokens(usage.input_tokens)
        self._record_output_tokens(usage.output_tokens)
        self._record_total_tokens(usage.total_tokens)

    def _record_tier_token_counts(self, *, usage: LlmUsage) -> None:
        """Record per-tier token totals for one usage snapshot."""
        if self._is_long_context_usage(usage=usage):
            self._long_context_input_tokens = self._long_context_input_tokens.add(usage.input_tokens)
            self._long_context_output_tokens = self._long_context_output_tokens.add(usage.output_tokens)
        else:
            self._short_context_input_tokens = self._short_context_input_tokens.add(usage.input_tokens)
            self._short_context_output_tokens = self._short_context_output_tokens.add(usage.output_tokens)

    def _is_long_context_usage(self, *, usage: LlmUsage) -> bool:
        """Return whether one request belongs to the long-context tier."""
        return (
            self._long_context_input_token_threshold is not None
            and usage.input_tokens is not None
            and usage.input_tokens >= self._long_context_input_token_threshold
        )

    def _record_estimated_cost(self, *, usage: LlmUsage) -> None:
        """Record the estimated cost for one usage snapshot when pricing is available."""
        if not self._estimated_cost_complete:
            return

        pricing = self._pricing_for_usage(usage=usage)
        if pricing is None:
            self._estimated_cost_complete = False
            return

        estimated_cost = self._estimate_cost(usage=usage, pricing=pricing)
        if estimated_cost is None:
            self._estimated_cost_complete = False
            return

        self._estimated_cost_usd += estimated_cost

    def _record_input_tokens(self, value: int | None) -> None:
        """Record aggregate input tokens when present."""
        self._input_tokens = self._input_tokens.add(value)

    def _record_output_tokens(self, value: int | None) -> None:
        """Record aggregate output tokens when present."""
        self._output_tokens = self._output_tokens.add(value)

    def _record_total_tokens(self, value: int | None) -> None:
        """Record aggregate total tokens when present."""
        self._total_tokens = self._total_tokens.add(value)

    def _reset_unlocked(self) -> None:
        """Reset mutable state while the caller already holds the lock."""
        self._request_count = 0
        self._short_context_input_tokens = _TokenAggregate()
        self._short_context_output_tokens = _TokenAggregate()
        self._long_context_input_tokens = _TokenAggregate()
        self._long_context_output_tokens = _TokenAggregate()
        self._input_tokens = _TokenAggregate()
        self._output_tokens = _TokenAggregate()
        self._total_tokens = _TokenAggregate()
        self._estimated_cost_usd = 0.0
        self._estimated_cost_complete = True
