"""Write labeled JSON debug artifacts to timestamped files."""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from llmframe.shared.json_types import JsonValue

LOGGER = logging.getLogger(__name__)
_LABEL_PATTERN = re.compile(r"[^a-zA-Z0-9_-]+")
_DEFAULT_LABEL = "payload"


class JsonFileWriterAdapter:
    """Persist labeled JSON payloads as timestamped files."""

    def __init__(self, *, base_dir: Path) -> None:
        """Initialize the adapter with the base output directory."""
        self._base_dir = base_dir

    def write_json(self, *, label: str, payload: JsonValue) -> Path:
        """Write a labeled JSON payload and return the created artifact path."""
        sanitized_label = self._sanitize_label(label)
        file_path = self._build_file_path(sanitized_label=sanitized_label)
        self._write_payload(file_path=file_path, payload=payload)
        LOGGER.debug(
            "JSON payload artifact written",
            extra={
                "component": self.__class__.__name__,
                "payload_label": sanitized_label,
                "file_path": str(file_path),
            },
        )
        return file_path

    @staticmethod
    def _sanitize_label(label: str) -> str:
        """Normalize a label into a safe filename component."""
        sanitized = _LABEL_PATTERN.sub("_", label.strip()).strip("_").lower()
        return sanitized or _DEFAULT_LABEL

    def _build_file_path(self, *, sanitized_label: str) -> Path:
        """Build an output path for a labeled JSON payload."""
        timestamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%S%fZ")
        return self._base_dir / f"{timestamp}_{sanitized_label}.json"

    @staticmethod
    def _write_payload(*, file_path: Path, payload: JsonValue) -> None:
        """Write a normalized JSON payload to disk."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as file_handle:
            json.dump(payload, file_handle, ensure_ascii=False, indent=2, sort_keys=True)
            file_handle.write("\n")
