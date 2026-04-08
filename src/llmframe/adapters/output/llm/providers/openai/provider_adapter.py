"""Public façade for OpenAI provider adapter operations."""

from __future__ import annotations

from .provider_base import OpenAIProviderBase
from .provider_batch_adapter import OpenAIProviderBatchAdapter
from .provider_single_request_adapter import OpenAIProviderSingleRequestAdapter


class OpenAIProviderAdapter(
    OpenAIProviderSingleRequestAdapter,
    OpenAIProviderBatchAdapter,
    OpenAIProviderBase,
):
    """Public façade combining single-request and batch OpenAI provider operations."""
