"""Compatibility shim for the legacy OpenAI client module path."""

from llmframe.adapters.output.llm.providers.openai.client import build_client

__all__ = ["build_client"]
