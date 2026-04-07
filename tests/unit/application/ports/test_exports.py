"""Tests for the application port package exports."""

from llmframe.application import ports


def test_exports_llm_provider_types() -> None:
    """Expose the application-layer LLM port types at package level."""
    assert ports.JsonArtifactWriterPort is not None
    assert ports.JsonSchema is not None
    assert ports.LlmInputItem is not None
    assert ports.LlmProviderPort is not None
    assert ports.LlmUsage is not None
    assert ports.StructuredOutputSchema is not None
