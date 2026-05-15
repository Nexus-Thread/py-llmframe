"""Shared JSON-compatible type aliases used across llmframe."""

from __future__ import annotations

from typing import TypeAlias

JsonScalar: TypeAlias = None | bool | int | float | str
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonArray: TypeAlias = list[JsonValue]
JsonObject: TypeAlias = dict[str, JsonValue]

__all__ = ["JsonArray", "JsonObject", "JsonScalar", "JsonValue"]
