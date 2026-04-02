"""Narrow persistence protocols shared by output adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pathlib import Path

    from llmframe.json_types import JsonValue


class JsonWriterProtocol(Protocol):
    """Protocol for writing labeled JSON debug payloads."""

    def write_json(self, *, label: str, payload: JsonValue) -> Path:
        """Persist one labeled JSON payload and return the written file path."""
        ...


__all__ = ["JsonWriterProtocol"]
