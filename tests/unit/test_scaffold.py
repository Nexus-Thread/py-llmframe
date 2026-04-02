"""Scaffold verification tests."""

from pathlib import Path


def test_source_package_exists() -> None:
    """Ensure the initial package scaffold exists."""
    assert Path("src/llmframe").is_dir()
