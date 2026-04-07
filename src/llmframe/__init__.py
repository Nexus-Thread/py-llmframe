"""Top-level public API for llmframe."""

from .adapters.output import llm
from .adapters.output.llm import build_openai_llm_adapter
from .adapters.output.llm.providers.openai import OpenAIClientSettings

__all__ = ["OpenAIClientSettings", "build_openai_llm_adapter", "llm"]
