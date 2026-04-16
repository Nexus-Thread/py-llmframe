"""Shared pytest configuration for local developer test runs."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

TEST_RESULTS_DIR = Path("test_results")


def pytest_configure(config: pytest.Config) -> None:
    """Configure a default timestamped HTML report when pytest-html is available.

    The report path is only set when the pytest-html plugin is installed and the
    caller did not explicitly pass an ``--html`` option.
    """
    if not config.pluginmanager.has_plugin("html"):
        return

    if getattr(config.option, "htmlpath", None):
        return

    TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%S")
    config.option.htmlpath = str(TEST_RESULTS_DIR / f"pytest-report-{timestamp}.html")
