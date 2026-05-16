"""Debug payload helpers for the OpenAI transport."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from llmframe.application.ports import JsonArtifactWriterPort
    from llmframe.shared.json_types import JsonValue

LOGGER = logging.getLogger(__name__)


def serialize_debug_payload(payload: object) -> JsonValue:
    """Convert a transport payload into a JSON-writable debug snapshot."""
    if isinstance(payload, dict | list | str | int | float | bool) or payload is None:
        return cast("JsonValue", payload)

    model_dump = getattr(payload, "model_dump", None)
    if callable(model_dump):
        return cast("JsonValue", model_dump(exclude_none=True, by_alias=True))

    to_dict = getattr(payload, "to_dict", None)
    if callable(to_dict):
        return cast("JsonValue", to_dict())

    return {"repr": repr(payload)}


def write_debug_payload(
    *,
    debug_json_enabled: bool,
    debug_json_writer: JsonArtifactWriterPort | None,
    label: str,
    payload: JsonValue,
    component: str,
) -> None:
    """Persist a labeled debug payload when transport debug output is enabled."""
    if not debug_json_enabled or debug_json_writer is None:
        return

    try:
        debug_json_writer.write_json(label=label, payload=payload)
    except (OSError, TypeError, ValueError):
        LOGGER.warning(
            "Failed to write OpenAI transport debug payload",
            extra={"component": component, "debug_label": label},
            exc_info=True,
        )


__all__ = ["serialize_debug_payload", "write_debug_payload"]
