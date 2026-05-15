"""Application port contracts for debug artifact writing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pathlib import Path

    from llmframe.shared.json_types import JsonValue


class JsonArtifactWriterPort(Protocol):
    """Output port for writing labeled JSON debug artifacts."""

    def write_json(self, *, label: str, payload: JsonValue) -> Path:
        """Persist a labeled JSON payload and return the written file path."""
        ...


__all__ = ["JsonArtifactWriterPort"]
