"""Tests for the application port package exports."""

import pytest

from llmframe import application
from llmframe.application import ports


@pytest.mark.parametrize(
    "export_name",
    [
        "BatchRequestStorePort",
        "JsonArtifactWriterPort",
        "JsonSchema",
        "LlmBatchId",
        "LlmBatchRequestItem",
        "LlmBatchStatus",
        "LlmBatchStructuredResult",
        "LlmBatchStructuredResultItem",
        "LlmBatchSubmission",
        "LlmBatchTextResult",
        "LlmBatchTextResultItem",
        "LlmContentPart",
        "LlmFileContentPart",
        "LlmImageUrlContentPart",
        "LlmInputItem",
        "LlmProviderPort",
        "LlmTextContentPart",
        "LlmUsage",
        "StoredLlmBatchRequest",
        "StructuredOutputSchema",
    ],
)
def test_exports_llm_provider_types(export_name: str) -> None:
    """Expose all application-layer port types from the ports package."""
    assert getattr(ports, export_name) is getattr(application, export_name)
    assert export_name in ports.__all__


@pytest.mark.parametrize(
    "export_name",
    [
        "BatchRequestStorePort",
        "JsonArtifactWriterPort",
        "JsonSchema",
        "LlmBatchId",
        "LlmBatchRequestItem",
        "LlmBatchStatus",
        "LlmBatchStructuredResult",
        "LlmBatchStructuredResultItem",
        "LlmBatchSubmission",
        "LlmBatchTextResult",
        "LlmBatchTextResultItem",
        "LlmContentPart",
        "LlmFileContentPart",
        "LlmImageUrlContentPart",
        "LlmInputItem",
        "LlmProviderPort",
        "LlmTextContentPart",
        "LlmUsage",
        "StoredLlmBatchRequest",
        "StructuredOutputSchema",
    ],
)
def test_exports_application_layer_types(export_name: str) -> None:
    """Expose all application-layer port types from the application package."""
    assert getattr(application, export_name) is getattr(ports, export_name)
    assert export_name in application.__all__


def test_exports_application_ports_namespace() -> None:
    """Expose the ports namespace from the application package."""
    assert application.ports is ports
    assert "ports" in application.__all__
