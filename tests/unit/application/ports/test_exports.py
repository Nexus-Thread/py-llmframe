"""Tests for the application port package exports."""

from llmframe import application
from llmframe.application import ports


def test_exports_llm_provider_types() -> None:
    """Expose all application-layer port types from the ports package."""
    assert ports.BatchRequestStorePort is not None
    assert ports.JsonArtifactWriterPort is not None
    assert ports.JsonSchema is not None
    assert ports.LlmBatchId is not None
    assert ports.LlmBatchRequestItem is not None
    assert ports.LlmBatchStatus is not None
    assert ports.LlmBatchStructuredResult is not None
    assert ports.LlmBatchStructuredResultItem is not None
    assert ports.LlmBatchSubmission is not None
    assert ports.LlmBatchTextResult is not None
    assert ports.LlmBatchTextResultItem is not None
    assert ports.LlmContentPart is not None
    assert ports.LlmFileContentPart is not None
    assert ports.LlmImageUrlContentPart is not None
    assert ports.LlmInputItem is not None
    assert ports.LlmProviderPort is not None
    assert ports.LlmTextContentPart is not None
    assert ports.LlmUsage is not None
    assert ports.StoredLlmBatchRequest is not None
    assert ports.StructuredOutputSchema is not None


def test_exports_application_layer_types() -> None:
    """Expose all application-layer port types from the application package."""
    assert application.ports is not None
    assert application.BatchRequestStorePort is not None
    assert application.JsonArtifactWriterPort is not None
    assert application.JsonSchema is not None
    assert application.LlmBatchId is not None
    assert application.LlmBatchRequestItem is not None
    assert application.LlmBatchStatus is not None
    assert application.LlmBatchStructuredResult is not None
    assert application.LlmBatchStructuredResultItem is not None
    assert application.LlmBatchSubmission is not None
    assert application.LlmBatchTextResult is not None
    assert application.LlmBatchTextResultItem is not None
    assert application.LlmContentPart is not None
    assert application.LlmFileContentPart is not None
    assert application.LlmImageUrlContentPart is not None
    assert application.LlmInputItem is not None
    assert application.LlmProviderPort is not None
    assert application.LlmTextContentPart is not None
    assert application.LlmUsage is not None
    assert application.StoredLlmBatchRequest is not None
    assert application.StructuredOutputSchema is not None
