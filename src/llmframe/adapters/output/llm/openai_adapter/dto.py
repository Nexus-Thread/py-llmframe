"""Compatibility shim for the legacy OpenAI DTO module path."""

from llmframe.adapters.output.llm.providers.openai.dto import (
    OpenAIClientSettings,
    OpenAIResponseError,
    OpenAIResponseUsage,
)

__all__ = ["OpenAIClientSettings", "OpenAIResponseError", "OpenAIResponseUsage"]
