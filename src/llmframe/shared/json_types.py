"""Shared JSON-compatible types for llmframe."""

from __future__ import annotations

from typing import TypeAlias

JsonValue: TypeAlias = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]

__all__ = ["JsonValue"]
