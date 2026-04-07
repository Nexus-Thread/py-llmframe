"""Tests for persistence package exports."""

from llmframe.adapters.output import persistence


def test_exports_json_file_writer_adapter() -> None:
    """Expose the concrete JSON file writer adapter at package level."""
    assert persistence.JsonFileWriterAdapter is not None
