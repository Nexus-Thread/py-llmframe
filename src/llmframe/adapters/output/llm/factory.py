"""Public factories for ready-to-use shared LLM adapters."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from llmframe.adapters.output.persistence import JsonFileWriterAdapter

from .llm_adapter import LlmAdapter
from .providers.openai import build_provider

if TYPE_CHECKING:
    from llmframe.application.ports import JsonArtifactWriterPort

    from .providers.openai import OpenAIClientSettings

DEFAULT_DEBUG_JSON_OUTPUT_DIR = Path("artifacts/llm-debug")


def _resolve_debug_json_writer(
    *,
    debug_json_writer: JsonArtifactWriterPort | None,
    debug_json_enabled: bool,
    debug_json_output_dir: Path | None,
) -> JsonArtifactWriterPort | None:
    """Resolve the debug JSON writer used by the public factory."""
    if debug_json_writer is not None:
        return debug_json_writer
    if not debug_json_enabled:
        return None
    return JsonFileWriterAdapter(base_dir=debug_json_output_dir or DEFAULT_DEBUG_JSON_OUTPUT_DIR)


def build_openai_llm_adapter(
    *,
    settings: OpenAIClientSettings,
    model: str,
    debug_json_writer: JsonArtifactWriterPort | None = None,
    debug_json_enabled: bool = False,
    debug_json_output_dir: Path | None = None,
) -> LlmAdapter:
    """Build a ready-to-use shared ``LlmAdapter`` backed by OpenAI.

    Args:
        settings: OpenAI transport configuration.
        model: Model identifier used for text and structured requests.
        debug_json_writer: Optional writer for request/response debug snapshots.
        debug_json_enabled: Whether debug snapshot writing is enabled.
        debug_json_output_dir: Optional output directory used for the default JSON file writer.

    Returns:
        A provider-neutral ``LlmAdapter`` configured with an OpenAI provider.
    """
    resolved_debug_json_writer = _resolve_debug_json_writer(
        debug_json_writer=debug_json_writer,
        debug_json_enabled=debug_json_enabled,
        debug_json_output_dir=debug_json_output_dir,
    )
    provider = build_provider(
        settings,
        debug_json_writer=resolved_debug_json_writer,
        debug_json_enabled=debug_json_enabled,
    )
    return LlmAdapter(
        client=provider,
        model=model,
        debug_json_writer=resolved_debug_json_writer,
        debug_json_enabled=debug_json_enabled,
    )
