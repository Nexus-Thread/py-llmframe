"""Retry helpers for OpenAI transport requests."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from openai import APIError

if TYPE_CHECKING:
    from collections.abc import Callable

LOGGER = logging.getLogger(__name__)

DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 2.0


@dataclass(frozen=True, slots=True)
class RetryContext:
    """Configuration and log context for one retryable OpenAI operation."""

    action_name: str
    model: str
    max_retries: int
    backoff_factor: float
    component: str


def retry_delay_seconds(*, backoff_factor: float, attempt: int) -> float:
    """Return the exponential backoff delay for a retry attempt."""
    return backoff_factor**attempt


def build_retry_log_extra(
    *,
    component: str,
    model: str,
    attempt: int,
    total_attempts: int,
    max_retries: int,
) -> dict[str, object]:
    """Return retry metadata shared by warning and error logs."""
    return {
        "component": component,
        "model": model,
        "attempt": attempt,
        "total_attempts": total_attempts,
        "max_retries": max_retries,
    }


def log_final_failure(
    *,
    attempt: int,
    total_attempts: int,
    context: RetryContext,
) -> None:
    """Log the final transport failure after all retries are exhausted."""
    LOGGER.exception(
        "OpenAI %s failed after exhausting retries",
        context.action_name,
        extra=build_retry_log_extra(
            component=context.component,
            model=context.model,
            attempt=attempt,
            total_attempts=total_attempts,
            max_retries=context.max_retries,
        ),
    )


def log_retry(
    *,
    attempt: int,
    total_attempts: int,
    delay: float,
    context: RetryContext,
) -> None:
    """Log retry metadata for a transient transport failure."""
    extra = build_retry_log_extra(
        component=context.component,
        model=context.model,
        attempt=attempt,
        total_attempts=total_attempts,
        max_retries=context.max_retries,
    )
    extra["attempts_remaining"] = total_attempts - attempt
    extra["retry_delay_seconds"] = delay
    LOGGER.warning("OpenAI %s attempt failed; retrying", context.action_name, extra=extra)


def call_with_retries(
    *,
    request: Callable[[], object],
    sleep: Callable[[float], None],
    context: RetryContext,
) -> object:
    """Execute an SDK request with shared retry and logging behavior."""
    total_attempts = context.max_retries + 1
    for attempt in range(1, total_attempts + 1):
        try:
            return request()
        except APIError:
            if attempt >= total_attempts:
                log_final_failure(
                    attempt=attempt,
                    total_attempts=total_attempts,
                    context=context,
                )
                raise
            delay = retry_delay_seconds(backoff_factor=context.backoff_factor, attempt=attempt)
            log_retry(
                attempt=attempt,
                total_attempts=total_attempts,
                delay=delay,
                context=context,
            )
            sleep(delay)

    message = "Unexpected transport retry loop termination"
    raise RuntimeError(message)


__all__ = [
    "DEFAULT_BACKOFF_FACTOR",
    "DEFAULT_MAX_RETRIES",
    "RetryContext",
    "build_retry_log_extra",
    "call_with_retries",
    "retry_delay_seconds",
]
