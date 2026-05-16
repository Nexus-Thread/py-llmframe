"""Tests for shared LLM package exports."""

import pytest

from llmframe.adapters.output import llm
from llmframe.adapters.output.llm import llm_adapter


def test_exports_public_factory() -> None:
    """Expose the public OpenAI-backed shared adapter factory at package level."""
    assert callable(llm.build_openai_llm_adapter)
    assert "build_openai_llm_adapter" in llm.__all__


@pytest.mark.parametrize(
    ("export_name", "canonical_object"),
    [
        ("LlmBatchTextRequest", llm_adapter.LlmBatchTextRequest),
        ("LlmBatchStructuredRequest", llm_adapter.LlmBatchStructuredRequest),
        ("LlmFileInputPart", llm_adapter.LlmFileInputPart),
        ("LlmTextInputPart", llm_adapter.LlmTextInputPart),
        ("LlmImageFileInputPart", llm_adapter.LlmImageFileInputPart),
        ("LlmImageUrlInputPart", llm_adapter.LlmImageUrlInputPart),
        ("StructuredLlmBatchError", llm_adapter.StructuredLlmBatchError),
    ],
)
def test_exports_public_batch_types(export_name: str, canonical_object: object) -> None:
    """Expose public batch request and error types at package level."""
    assert getattr(llm, export_name) is canonical_object
    assert export_name in llm.__all__
