"""Public façade for shared LLM adapter operations."""

from __future__ import annotations

from .base import BaseLlmAdapter
from .batch_adapter import BatchLlmAdapter
from .single_request_adapter import SingleRequestLlmAdapter


class LlmAdapter(SingleRequestLlmAdapter, BatchLlmAdapter, BaseLlmAdapter):
    """Public façade combining single-request and batch LLM operations."""
