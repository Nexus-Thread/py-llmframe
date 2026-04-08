"""Shared JSON-compatible type aliases used across llmframe."""

from __future__ import annotations

from typing import TypeAlias

JsonScalar: TypeAlias = None | bool | int | float | str
JsonArray: TypeAlias = list["JsonValue"]
JsonObject: TypeAlias = dict[str, "JsonValue"]
JsonValue: TypeAlias = JsonScalar | JsonArray | JsonObject

__all__ = ["JsonArray", "JsonObject", "JsonScalar", "JsonValue"]
