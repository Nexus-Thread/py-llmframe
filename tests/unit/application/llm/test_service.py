"""Unit tests for the provider-neutral LLM application service."""

from __future__ import annotations

from llmframe.application import LlmService, LlmTextCompletionResult
from llmframe.application.ports import LlmUsage
from tests.unit.adapters.output.llm.llm_adapter._support import _ResponsesApiResponse, _StubClient


def test_llm_service_generate_text_uses_provider_port() -> None:
    """Application service owns text-generation orchestration."""
    provider = _StubClient([_ResponsesApiResponse(output_text="hello", usage=LlmUsage(1, 2, 3))])
    service = LlmService(provider=provider, model="gpt-test")

    result = service.generate_text(developer_prompt="developer", user_prompt="user")

    assert result == LlmTextCompletionResult(content="hello", usage=LlmUsage(1, 2, 3))
    assert provider.calls == [
        (
            "responses_plain",
            "gpt-test",
            [{"role": "developer", "content": "developer"}, {"role": "user", "content": "user"}],
        )
    ]
