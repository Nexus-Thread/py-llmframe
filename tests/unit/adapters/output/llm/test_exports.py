"""Tests for shared LLM package exports."""

from llmframe.adapters.output import llm


def test_exports_public_factory() -> None:
    """Expose the public OpenAI-backed shared adapter factory at package level."""
    assert llm.build_openai_llm_adapter is not None


def test_exports_public_batch_types() -> None:
    """Expose public batch request and error types at package level."""
    assert llm.LlmBatchTextRequest is not None
    assert llm.LlmBatchStructuredRequest is not None
    assert llm.LlmTextInputPart is not None
    assert llm.LlmImageFileInputPart is not None
    assert llm.LlmImageUrlInputPart is not None
    assert llm.StructuredLlmBatchError is not None
