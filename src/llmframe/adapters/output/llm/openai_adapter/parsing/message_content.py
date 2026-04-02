"""Compatibility shim for the legacy OpenAI parsing module path."""

from llmframe.adapters.output.llm.providers.openai.parsing.message_content import extract_message_content

__all__ = ["extract_message_content"]
