"""Tests for root package exports."""

import llmframe


def test_exports_top_level_openai_entrypoints() -> None:
    """Expose the ergonomic OpenAI-first entrypoints at package level."""
    assert llmframe.build_openai_llm_adapter is not None
    assert llmframe.OpenAIClientSettings is not None


def test_exports_top_level_adapter_types() -> None:
    """Expose commonly used adapter types at package level."""
    assert llmframe.LlmAdapter is not None
    assert llmframe.LlmTextCompletionResult is not None
    assert llmframe.StructuredLlmJsonCompletionResult is not None
    assert llmframe.LlmUsageTracker is not None
    assert llmframe.LlmUsageTrackerConfig is not None
    assert llmframe.LlmUsageSummary is not None
    assert llmframe.JsonFileWriterAdapter is not None


def test_exports_top_level_application_types() -> None:
    """Expose commonly used application port types at package level."""
    assert llmframe.JsonArtifactWriterPort is not None
    assert llmframe.JsonSchema is not None
    assert llmframe.LlmInputItem is not None
    assert llmframe.LlmProviderPort is not None
    assert llmframe.LlmUsage is not None
    assert llmframe.StructuredOutputSchema is not None


def test_exports_top_level_namespaces() -> None:
    """Expose the main package namespaces at package level."""
    assert llmframe.adapters is not None
    assert llmframe.application is not None
    assert llmframe.llm is not None
    assert llmframe.persistence is not None
