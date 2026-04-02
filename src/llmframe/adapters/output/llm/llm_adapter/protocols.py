"""Narrow type alias used by the shared LLM adapter."""

from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel

StructuredOutputSchema: TypeAlias = type[BaseModel]


__all__ = [
    "StructuredOutputSchema",
]
