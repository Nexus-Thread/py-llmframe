"""Tests for root package exports."""

import pytest

import llmframe
from llmframe import application
from llmframe.adapters import output
from llmframe.adapters.output import llm, persistence
from llmframe.adapters.output.llm.providers.openai import OpenAIClientSettings


@pytest.mark.parametrize(
    ("export_name", "canonical_object"),
    [
        ("build_openai_llm_adapter", llm.build_openai_llm_adapter),
        ("OpenAIClientSettings", OpenAIClientSettings),
    ],
)
def test_exports_top_level_openai_entrypoints(export_name: str, canonical_object: object) -> None:
    """Expose the ergonomic OpenAI-first entrypoints at package level."""
    assert getattr(llmframe, export_name) is canonical_object
    assert export_name in llmframe.__all__


@pytest.mark.parametrize(
    ("export_name", "canonical_object"),
    [
        ("LlmAdapter", output.LlmAdapter),
        ("LlmBatchTextRequest", output.LlmBatchTextRequest),
        ("LlmBatchStructuredRequest", output.LlmBatchStructuredRequest),
        ("LlmFileInputPart", output.LlmFileInputPart),
        ("LlmTextInputPart", output.LlmTextInputPart),
        ("LlmImageFileInputPart", output.LlmImageFileInputPart),
        ("LlmImageUrlInputPart", output.LlmImageUrlInputPart),
        ("LlmTextCompletionResult", output.LlmTextCompletionResult),
        ("StructuredLlmJsonCompletionResult", output.StructuredLlmJsonCompletionResult),
        ("StructuredLlmBatchError", output.StructuredLlmBatchError),
        ("LlmUsageTracker", output.LlmUsageTracker),
        ("LlmUsageTrackerConfig", output.LlmUsageTrackerConfig),
        ("LlmUsageSummary", output.LlmUsageSummary),
        ("JsonFileBatchRequestStoreAdapter", output.JsonFileBatchRequestStoreAdapter),
        ("JsonFileWriterAdapter", output.JsonFileWriterAdapter),
    ],
)
def test_exports_top_level_adapter_types(export_name: str, canonical_object: object) -> None:
    """Expose commonly used adapter types at package level."""
    assert getattr(llmframe, export_name) is canonical_object
    assert export_name in llmframe.__all__


@pytest.mark.parametrize(
    ("export_name", "canonical_object"),
    [
        ("BatchRequestStorePort", application.BatchRequestStorePort),
        ("JsonArtifactWriterPort", application.JsonArtifactWriterPort),
        ("JsonSchema", application.JsonSchema),
        ("LlmBatchId", application.LlmBatchId),
        ("LlmBatchRequestItem", application.LlmBatchRequestItem),
        ("LlmBatchStatus", application.LlmBatchStatus),
        ("LlmBatchSubmission", application.LlmBatchSubmission),
        ("LlmBatchTextResult", application.LlmBatchTextResult),
        ("LlmBatchStructuredResult", application.LlmBatchStructuredResult),
        ("LlmTextContentPart", application.LlmTextContentPart),
        ("LlmFileContentPart", application.LlmFileContentPart),
        ("LlmImageUrlContentPart", application.LlmImageUrlContentPart),
        ("LlmContentPart", application.LlmContentPart),
        ("LlmInputItem", application.LlmInputItem),
        ("LlmProviderPort", application.LlmProviderPort),
        ("LlmUsage", application.LlmUsage),
        ("StoredLlmBatchRequest", application.StoredLlmBatchRequest),
        ("StructuredOutputSchema", application.StructuredOutputSchema),
    ],
)
def test_exports_top_level_application_types(export_name: str, canonical_object: object) -> None:
    """Expose commonly used application port types at package level."""
    assert getattr(llmframe, export_name) is canonical_object
    assert export_name in llmframe.__all__


@pytest.mark.parametrize(
    ("export_name", "canonical_object"),
    [
        ("adapters", llmframe.adapters),
        ("application", application),
        ("llm", llm),
        ("persistence", persistence),
    ],
)
def test_exports_top_level_namespaces(export_name: str, canonical_object: object) -> None:
    """Expose the main package namespaces at package level."""
    assert getattr(llmframe, export_name) is canonical_object
    assert export_name in llmframe.__all__
