"""Unit tests for public shared LLM adapter factories."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

from llmframe.adapters.output.llm import LlmAdapter, build_openai_llm_adapter
from llmframe.adapters.output.llm.providers.openai import OpenAIClientSettings
from llmframe.adapters.output.persistence import JsonFileBatchRequestStoreAdapter, JsonFileWriterAdapter

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch

    from llmframe.application import BatchRequestStorePort, StoredLlmBatchRequest


TEST_SETTINGS = OpenAIClientSettings(base_url="https://example.invalid/v1", api_key="test-key")
TEST_MODEL = "gpt-test"


class _StubDebugJsonWriter:
    def write_json(self, *, label: str, payload: object) -> Path:
        del payload
        return Path(f"debug/{label}.json")


class _StubBatchRequestStore:
    def save_batch_request(self, *, batch_request: object) -> Path:
        del batch_request
        return Path("batches/batch_123.json")

    def get_batch_request(self, *, batch_id: str) -> StoredLlmBatchRequest | None:
        del batch_id
        return None


def _install_stub_build_provider(monkeypatch: MonkeyPatch) -> dict[str, object]:
    """Capture factory arguments passed to provider construction."""
    captured: dict[str, object] = {}

    def _stub_build_provider(
        settings: OpenAIClientSettings,
        *,
        debug_json_writer: object | None = None,
        debug_json_enabled: bool = False,
    ) -> object:
        captured["settings"] = settings
        captured["provider_debug_json_writer"] = debug_json_writer
        captured["provider_debug_json_enabled"] = debug_json_enabled
        return object()

    monkeypatch.setattr(
        "llmframe.adapters.output.llm.factory.build_provider",
        _stub_build_provider,
    )
    return captured


def test_build_openai_llm_adapter_returns_shared_adapter() -> None:
    """Public factory returns the shared provider-neutral adapter type."""
    adapter = build_openai_llm_adapter(
        settings=TEST_SETTINGS,
        model=TEST_MODEL,
    )

    assert isinstance(adapter, LlmAdapter)


def test_build_openai_llm_adapter_passes_debug_settings_to_provider_and_adapter(
    monkeypatch: MonkeyPatch,
) -> None:
    """Public factory forwards debug configuration to provider construction and adapter."""
    captured = _install_stub_build_provider(monkeypatch)

    writer = _StubDebugJsonWriter()

    adapter = build_openai_llm_adapter(
        settings=TEST_SETTINGS,
        model=TEST_MODEL,
        debug_json_writer=writer,
        debug_json_enabled=True,
    )

    assert isinstance(adapter, LlmAdapter)
    assert captured == {
        "settings": TEST_SETTINGS,
        "provider_debug_json_writer": writer,
        "provider_debug_json_enabled": True,
    }
    assert adapter._model == TEST_MODEL
    assert adapter._batch_request_store is not None
    assert adapter._debug_json_writer is writer
    assert adapter._debug_json_enabled is True


def test_build_openai_llm_adapter_creates_default_json_file_writer_when_enabled(
    monkeypatch: MonkeyPatch,
) -> None:
    """Public factory creates the default JSON file writer when debug output is enabled."""
    captured = _install_stub_build_provider(monkeypatch)

    adapter = build_openai_llm_adapter(
        settings=TEST_SETTINGS,
        model=TEST_MODEL,
        debug_json_enabled=True,
    )

    writer = captured["provider_debug_json_writer"]
    assert isinstance(adapter, LlmAdapter)
    assert isinstance(writer, JsonFileWriterAdapter)
    assert writer._base_dir == Path("artifacts/llm-debug")
    assert isinstance(adapter._batch_request_store, JsonFileBatchRequestStoreAdapter)
    assert adapter._debug_json_writer is writer
    assert captured["provider_debug_json_enabled"] is True


def test_build_openai_llm_adapter_uses_custom_debug_output_dir(
    monkeypatch: MonkeyPatch,
) -> None:
    """Public factory uses the configured output directory for the default JSON writer."""
    captured = _install_stub_build_provider(monkeypatch)

    custom_output_dir = Path("custom/debug-dir")

    build_openai_llm_adapter(
        settings=TEST_SETTINGS,
        model=TEST_MODEL,
        debug_json_enabled=True,
        debug_json_output_dir=custom_output_dir,
    )

    writer = captured["provider_debug_json_writer"]
    assert isinstance(writer, JsonFileWriterAdapter)
    assert writer._base_dir == custom_output_dir


def test_build_openai_llm_adapter_uses_custom_batch_request_output_dir(monkeypatch: MonkeyPatch) -> None:
    """Public factory uses the configured output directory for batch request persistence."""
    _install_stub_build_provider(monkeypatch)

    adapter = build_openai_llm_adapter(
        settings=TEST_SETTINGS,
        model=TEST_MODEL,
        batch_request_output_dir=Path("custom/batches"),
    )

    batch_request_store = adapter._batch_request_store
    assert isinstance(batch_request_store, JsonFileBatchRequestStoreAdapter)
    assert batch_request_store._base_dir == Path("custom/batches")


def test_build_openai_llm_adapter_prefers_explicit_writer_over_default_factory_behavior(
    monkeypatch: MonkeyPatch,
) -> None:
    """Public factory keeps an explicitly provided writer instead of creating a file writer."""
    captured = _install_stub_build_provider(monkeypatch)

    writer = _StubDebugJsonWriter()

    adapter = build_openai_llm_adapter(
        settings=TEST_SETTINGS,
        model=TEST_MODEL,
        debug_json_writer=writer,
        debug_json_enabled=True,
        debug_json_output_dir=Path("custom/debug-dir"),
    )

    assert isinstance(adapter, LlmAdapter)
    assert captured["provider_debug_json_writer"] is writer
    assert adapter._debug_json_writer is writer


def test_build_openai_llm_adapter_prefers_explicit_batch_request_store(monkeypatch: MonkeyPatch) -> None:
    """Public factory keeps an explicitly provided batch request store."""
    _install_stub_build_provider(monkeypatch)

    store = _StubBatchRequestStore()
    adapter = build_openai_llm_adapter(
        settings=TEST_SETTINGS,
        model=TEST_MODEL,
        batch_request_store=cast("BatchRequestStorePort", store),
    )

    assert isinstance(adapter, LlmAdapter)
    assert adapter._batch_request_store is store
