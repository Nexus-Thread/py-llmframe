"""Tests for output adapter package exports."""

import pytest

from llmframe.adapters import output
from llmframe.adapters.output import llm, persistence


@pytest.mark.parametrize(
    ("export_name", "canonical_object"),
    [
        ("llm", llm),
        ("persistence", persistence),
    ],
)
def test_exports_public_output_namespaces(export_name: str, canonical_object: object) -> None:
    """Expose the public output adapter namespaces at package level."""
    assert getattr(output, export_name) is canonical_object
    assert export_name in output.__all__


@pytest.mark.parametrize(
    ("export_name", "canonical_object"),
    [
        ("LlmAdapter", llm.LlmAdapter),
        ("LlmBatchTextRequest", llm.LlmBatchTextRequest),
        ("LlmBatchStructuredRequest", llm.LlmBatchStructuredRequest),
        ("LlmFileInputPart", llm.LlmFileInputPart),
        ("LlmTextCompletionResult", llm.LlmTextCompletionResult),
        ("StructuredLlmJsonCompletionResult", llm.StructuredLlmJsonCompletionResult),
        ("StructuredLlmBatchError", llm.StructuredLlmBatchError),
        ("LlmUsageTracker", llm.LlmUsageTracker),
        ("LlmUsageTrackerConfig", llm.LlmUsageTrackerConfig),
        ("LlmUsageSummary", llm.LlmUsageSummary),
        ("JsonFileWriterAdapter", persistence.JsonFileWriterAdapter),
        ("build_openai_llm_adapter", llm.build_openai_llm_adapter),
    ],
)
def test_exports_public_output_types(export_name: str, canonical_object: object) -> None:
    """Expose commonly used output adapter types and factories at package level."""
    assert getattr(output, export_name) is canonical_object
    assert export_name in output.__all__
