"""Tests for the application port package exports."""

from llmframe import application
from llmframe.application import ports


def test_exports_llm_provider_types() -> None:
    """Expose the application-layer LLM port types at package level."""
    assert ports.JsonArtifactWriterPort is not None
    assert ports.JsonSchema is not None
    assert ports.LlmInputItem is not None
    assert ports.LlmProviderPort is not None
    assert ports.LlmUsage is not None
    assert ports.StructuredOutputSchema is not None


def test_exports_application_layer_types() -> None:
    """Expose application-layer port types from the application package."""
    assert application.ports is not None
    assert application.JsonArtifactWriterPort is not None
    assert application.JsonSchema is not None
    assert application.LlmInputItem is not None
    assert application.LlmProviderPort is not None
    assert application.LlmUsage is not None
    assert application.StructuredOutputSchema is not None
