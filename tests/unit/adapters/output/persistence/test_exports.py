"""Tests for persistence package exports."""

import pytest

from llmframe.adapters.output import persistence
from llmframe.adapters.output.persistence.batch_request_store import JsonFileBatchRequestStoreAdapter
from llmframe.adapters.output.persistence.json_file_writer_adapter import JsonFileWriterAdapter


@pytest.mark.parametrize(
    ("export_name", "canonical_object"),
    [
        ("JsonFileBatchRequestStoreAdapter", JsonFileBatchRequestStoreAdapter),
        ("JsonFileWriterAdapter", JsonFileWriterAdapter),
    ],
)
def test_exports_json_file_writer_adapter(export_name: str, canonical_object: object) -> None:
    """Expose the concrete JSON file writer adapter at package level."""
    assert getattr(persistence, export_name) is canonical_object
    assert export_name in persistence.__all__
