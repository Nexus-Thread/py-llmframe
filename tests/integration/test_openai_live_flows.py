"""On-demand live integration tests for the public OpenAI-backed LLM flows."""

from __future__ import annotations

import os
import time
from typing import assert_never

import pytest
from pydantic import BaseModel, ConfigDict

from llmframe import LlmAdapter, LlmBatchTextRequest, OpenAIClientSettings, build_openai_llm_adapter

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4.1-nano"
DEFAULT_BATCH_WAIT_TIMEOUT_SECONDS = 120.0
DEFAULT_BATCH_POLL_INTERVAL_SECONDS = 5.0
TERMINAL_BATCH_STATUSES = {"completed", "failed", "expired", "cancelled"}

pytestmark = [pytest.mark.integration, pytest.mark.on_demand]


class _TinyStructuredResponse(BaseModel):
    """Minimal schema used to keep structured-output tests tiny."""

    model_config = ConfigDict(extra="forbid")

    ok: bool


def _read_required_api_key() -> str:
    """Return the configured OpenAI API key or skip the live suite."""
    if os.getenv("LLMFRAME_RUN_ON_DEMAND_INTEGRATION") != "1":
        pytest.skip("Set LLMFRAME_RUN_ON_DEMAND_INTEGRATION=1 to run live integration tests.")

    api_key = os.getenv("LLMFRAME_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("Set OPENAI_API_KEY or LLMFRAME_OPENAI_API_KEY to run live integration tests.")
    return api_key


def _read_float_env(name: str, default: float) -> float:
    """Return a float environment override or the supplied default."""
    value = os.getenv(name)
    return float(value) if value is not None else default


def _build_live_adapter() -> tuple[LlmAdapter, str]:
    """Build the public OpenAI-backed adapter configured for live integration tests."""
    api_key = _read_required_api_key()
    base_url = os.getenv("LLMFRAME_OPENAI_BASE_URL", DEFAULT_BASE_URL)
    model = os.getenv("LLMFRAME_OPENAI_MODEL", DEFAULT_MODEL)

    adapter = build_openai_llm_adapter(
        settings=OpenAIClientSettings(base_url=base_url, api_key=api_key),
        model=model,
    )
    return adapter, model


def _wait_for_batch_completion(adapter: LlmAdapter, *, batch_id: str) -> str:
    """Poll a live batch until it reaches a terminal state or times out."""
    timeout_seconds = _read_float_env(
        "LLMFRAME_BATCH_WAIT_TIMEOUT_SECONDS",
        DEFAULT_BATCH_WAIT_TIMEOUT_SECONDS,
    )
    poll_interval_seconds = _read_float_env(
        "LLMFRAME_BATCH_POLL_INTERVAL_SECONDS",
        DEFAULT_BATCH_POLL_INTERVAL_SECONDS,
    )
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        status = adapter.get_batch_status(batch_id=batch_id)
        current_status = status.status
        if current_status in TERMINAL_BATCH_STATUSES:
            if isinstance(current_status, str):
                return current_status
            assert_never(current_status)
        time.sleep(poll_interval_seconds)

    pytest.fail(f"Timed out waiting for batch {batch_id} to complete.")


def test_generate_text_live_returns_tiny_response() -> None:
    """The public adapter returns a tiny plain-text response from the live provider."""
    adapter, model = _build_live_adapter()

    result = adapter.generate_text(
        developer_prompt="Reply with exactly OK.",
        user_prompt="Return OK.",
        temperature=0,
    )

    assert result.content.strip() == "OK"
    assert result.usage is not None
    assert result.usage.total_tokens is None or result.usage.total_tokens > 0
    assert model == os.getenv("LLMFRAME_OPENAI_MODEL", DEFAULT_MODEL)


def test_extract_json_live_returns_tiny_payload() -> None:
    """The public adapter returns a minimal structured JSON payload from the live provider."""
    adapter, _ = _build_live_adapter()

    result = adapter.extract_json(
        developer_prompt="Return JSON only.",
        user_prompt='Return an object with exactly one field: {"ok": true}.',
        response_schema=_TinyStructuredResponse,
    )

    assert result.payload == {"ok": True}
    assert result.usage is not None
    assert result.usage.total_tokens is None or result.usage.total_tokens > 0


def test_submit_text_batch_live_returns_result() -> None:
    """The public adapter can submit and retrieve a tiny live batch result."""
    adapter, _ = _build_live_adapter()

    submission = adapter.submit_text_batch(
        requests=[
            LlmBatchTextRequest(
                custom_id="tiny-text-1",
                developer_prompt="Reply with exactly OK.",
                user_prompt="Return OK.",
                temperature=0,
            )
        ]
    )

    assert submission.request_count == 1

    final_status = _wait_for_batch_completion(adapter, batch_id=submission.batch_id)
    assert final_status == "completed"

    result = adapter.get_text_batch_result(batch_id=submission.batch_id)

    assert result.batch_id == submission.batch_id
    assert result.status == "completed"
    assert len(result.items) == 1
    assert result.items[0].custom_id == "tiny-text-1"
    assert result.items[0].error is None
    assert result.items[0].content is not None
    assert result.items[0].content.strip() == "OK"
