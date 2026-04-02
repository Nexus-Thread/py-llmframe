"""Compatibility shim for the legacy OpenAI transport module path."""

from llmframe.adapters.output.llm.providers.openai.transport.adapter import (
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_MAX_RETRIES,
    OpenAIClient,
)

__all__ = ["DEFAULT_BACKOFF_FACTOR", "DEFAULT_MAX_RETRIES", "OpenAIClient"]
