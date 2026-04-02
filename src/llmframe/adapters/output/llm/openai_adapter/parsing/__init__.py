"""Compatibility shim for the legacy OpenAI parsing package path."""

from llmframe.adapters.output.llm.providers.openai.parsing import (
    extract_message_content,
    extract_usage,
)

__all__ = ["extract_message_content", "extract_usage"]
