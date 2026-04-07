"""Helpers for constructing OpenAI transports and provider adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
from openai import OpenAI

from .provider_adapter import OpenAIProviderAdapter
from .transport import OpenAIClient

if TYPE_CHECKING:
    from llmframe.application.ports import JsonArtifactWriterPort

    from .dto import OpenAIClientSettings


def build_client(
    settings: OpenAIClientSettings,
    *,
    debug_json_writer: JsonArtifactWriterPort | None = None,
    debug_json_enabled: bool = False,
) -> OpenAIClient:
    """Build an ``OpenAIClient`` from explicit settings.

    Args:
        settings: OpenAI transport configuration.
        debug_json_writer: Optional writer for request/response debug snapshots.
        debug_json_enabled: Whether debug snapshot writing is enabled.
    """
    http_client = httpx.Client(
        verify=settings.verify_ssl,
        timeout=httpx.Timeout(settings.timeout_seconds),
    )
    sdk_client = OpenAI(
        base_url=settings.base_url,
        api_key=settings.api_key,
        http_client=http_client,
    )
    return OpenAIClient(
        sdk_client=sdk_client,
        max_retries=settings.max_retries,
        backoff_factor=settings.backoff_factor,
        debug_json_writer=debug_json_writer,
        debug_json_enabled=debug_json_enabled,
    )


def build_provider(
    settings: OpenAIClientSettings,
    *,
    debug_json_writer: JsonArtifactWriterPort | None = None,
    debug_json_enabled: bool = False,
) -> OpenAIProviderAdapter:
    """Build an application-facing OpenAI provider adapter.

    Args:
        settings: OpenAI transport configuration.
        debug_json_writer: Optional writer for request/response debug snapshots.
        debug_json_enabled: Whether debug snapshot writing is enabled.
    """
    return OpenAIProviderAdapter(
        transport=build_client(
            settings,
            debug_json_writer=debug_json_writer,
            debug_json_enabled=debug_json_enabled,
        )
    )
