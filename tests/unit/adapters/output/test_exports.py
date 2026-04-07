"""Tests for output adapter package exports."""

from llmframe.adapters import output


def test_exports_public_output_namespaces() -> None:
    """Expose the public output adapter namespaces at package level."""
    assert output.llm is not None
    assert output.persistence is not None
