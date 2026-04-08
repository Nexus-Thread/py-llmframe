"""Shared helpers for on-demand live OpenAI integration tests."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import assert_never

import pytest
from pydantic import BaseModel, ConfigDict

from llmframe import LlmAdapter, OpenAIClientSettings, build_openai_llm_adapter

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-5.4-nano"
DEFAULT_BATCH_WAIT_TIMEOUT_SECONDS = 120.0
DEFAULT_BATCH_POLL_INTERVAL_SECONDS = 5.0
DEFAULT_BATCH_REQUEST_OUTPUT_DIR = Path("artifacts/llm-batches")
TERMINAL_BATCH_STATUSES = {"completed", "failed", "expired", "cancelled"}
PYTEST_MARKS = [pytest.mark.integration, pytest.mark.on_demand]


class TinyStructuredResponse(BaseModel):
    """Minimal schema used to keep structured-output tests tiny."""

    model_config = ConfigDict(extra="forbid")

    ok: bool


def read_required_api_key() -> str:
    """Return the configured OpenAI API key or skip the live suite."""
    if os.getenv("LLMFRAME_RUN_ON_DEMAND_INTEGRATION") != "1":
        pytest.skip("Set LLMFRAME_RUN_ON_DEMAND_INTEGRATION=1 to run live integration tests.")

    api_key = os.getenv("LLMFRAME_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("Set OPENAI_API_KEY or LLMFRAME_OPENAI_API_KEY to run live integration tests.")
    return api_key


def read_float_env(name: str, default: float) -> float:
    """Return a float environment override or the supplied default."""
    value = os.getenv(name)
    return float(value) if value is not None else default


def build_live_adapter() -> tuple[LlmAdapter, str]:
    """Build the public OpenAI-backed adapter configured for live integration tests."""
    api_key = read_required_api_key()
    base_url = os.getenv("LLMFRAME_OPENAI_BASE_URL", DEFAULT_BASE_URL)
    model = os.getenv("LLMFRAME_OPENAI_MODEL", DEFAULT_MODEL)

    adapter = build_openai_llm_adapter(
        settings=OpenAIClientSettings(base_url=base_url, api_key=api_key),
        model=model,
    )
    return adapter, model


def read_batch_request_output_dir() -> Path:
    """Return the configured batch metadata directory for live integration tests."""
    output_dir = os.getenv("LLMFRAME_BATCH_REQUEST_OUTPUT_DIR")
    if output_dir:
        return Path(output_dir)
    return DEFAULT_BATCH_REQUEST_OUTPUT_DIR


def read_explicit_batch_id() -> str | None:
    """Return an explicit batch ID override for retrieval tests when configured."""
    return os.getenv("LLMFRAME_TEST_BATCH_ID")


def read_latest_persisted_batch_id() -> str:
    """Return the newest persisted batch ID for manual/live retrieval workflows."""
    batch_files = sorted(
        read_batch_request_output_dir().glob("*.json"),
        key=lambda file_path: file_path.stat().st_mtime,
        reverse=True,
    )
    if not batch_files:
        pytest.skip(
            "No persisted batch metadata found. Submit a batch first or set LLMFRAME_TEST_BATCH_ID.",
        )

    with batch_files[0].open("r", encoding="utf-8") as file_handle:
        payload = json.load(file_handle)

    batch_id = payload.get("batch_id")
    if not isinstance(batch_id, str) or not batch_id:
        pytest.skip("Newest persisted batch metadata does not contain a valid batch_id.")
    return batch_id


def read_batch_id_for_retrieval() -> str:
    """Return the batch ID that retrieval tests should inspect."""
    explicit_batch_id = read_explicit_batch_id()
    if explicit_batch_id:
        return explicit_batch_id
    return read_latest_persisted_batch_id()


def wait_for_batch_completion(adapter: LlmAdapter, *, batch_id: str) -> str:
    """Poll a live batch until it reaches a terminal state or times out."""
    timeout_seconds = read_float_env(
        "LLMFRAME_BATCH_WAIT_TIMEOUT_SECONDS",
        DEFAULT_BATCH_WAIT_TIMEOUT_SECONDS,
    )
    poll_interval_seconds = read_float_env(
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
