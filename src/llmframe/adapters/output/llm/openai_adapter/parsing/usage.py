"""Compatibility shim for the legacy OpenAI parsing module path."""

from llmframe.adapters.output.llm.providers.openai.parsing.usage import extract_usage

__all__ = ["extract_usage"]
