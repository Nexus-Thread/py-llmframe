"""Unit tests for the JSON file writer adapter."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from llmframe.adapters.output.persistence import JsonFileWriterAdapter

if TYPE_CHECKING:
    from pathlib import Path


def test_write_json_creates_timestamped_file_with_sanitized_label(tmp_path: Path) -> None:
    """Write JSON artifacts using a normalized label and stable formatting."""
    adapter = JsonFileWriterAdapter(base_dir=tmp_path)

    written_path = adapter.write_json(
        label="  Debug Payload / Example  ",
        payload={"z": 1, "á": [True, None, "text"]},
    )

    assert written_path.parent == tmp_path
    assert written_path.name.endswith("_debug_payload_example.json")
    assert json.loads(written_path.read_text(encoding="utf-8")) == {
        "z": 1,
        "á": [True, None, "text"],
    }
    assert written_path.read_text(encoding="utf-8") == (
        '{\n  "z": 1,\n  "á": [\n    true,\n    null,\n    "text"\n  ]\n}\n'
    )


def test_write_json_falls_back_to_payload_label_for_empty_sanitized_value(tmp_path: Path) -> None:
    """Use a default filename label when sanitization removes all characters."""
    adapter = JsonFileWriterAdapter(base_dir=tmp_path)

    written_path = adapter.write_json(label="!!!", payload={"value": 1})

    assert written_path.name.endswith("_payload.json")


def test_write_json_creates_missing_parent_directories(tmp_path: Path) -> None:
    """Create the configured output directory when it does not already exist."""
    adapter = JsonFileWriterAdapter(base_dir=tmp_path / "debug" / "artifacts")

    written_path = adapter.write_json(label="payload", payload={"value": 1})

    assert written_path.parent == tmp_path / "debug" / "artifacts"
    assert written_path.exists()
