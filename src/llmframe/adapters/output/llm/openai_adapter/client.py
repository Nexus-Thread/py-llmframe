"""Helpers for constructing the shared OpenAI transport client."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
from openai import OpenAI

from .transport import OpenAIClient

if TYPE_CHECKING:
    from llmframe.adapters.output.persistence import JsonWriterProtocol

    from .dto import OpenAIClientSettings


def build_client(
    settings: OpenAIClientSettings,
    *,
    debug_json_writer: JsonWriterProtocol | None = None,
    debug_json_enabled: bool = False,
) -> OpenAIClient:
    """Build an ``OpenAIClient`` from explicit settings."""
    timeout = httpx.Timeout(settings.timeout_seconds)
    http_client = httpx.Client(
        verify=settings.verify_ssl,
        timeout=timeout,
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
