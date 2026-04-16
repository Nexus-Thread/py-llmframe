"""Tests for output adapter package exports."""

from llmframe.adapters import output


def test_exports_public_output_namespaces() -> None:
    """Expose the public output adapter namespaces at package level."""
    assert output.llm is not None
    assert output.persistence is not None


def test_exports_public_output_types() -> None:
    """Expose commonly used output adapter types and factories at package level."""
    assert output.LlmAdapter is not None
    assert output.LlmBatchTextRequest is not None
    assert output.LlmBatchStructuredRequest is not None
    assert output.LlmFileInputPart is not None
    assert output.LlmTextCompletionResult is not None
    assert output.StructuredLlmJsonCompletionResult is not None
    assert output.StructuredLlmBatchError is not None
    assert output.LlmUsageTracker is not None
    assert output.LlmUsageTrackerConfig is not None
    assert output.LlmUsageSummary is not None
    assert output.JsonFileWriterAdapter is not None
    assert output.build_openai_llm_adapter is not None
