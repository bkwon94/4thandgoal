"""
Shared pytest fixtures for the Cornerstone Weekly tests.
They give tests the path to the recorded Sleeper data.
"""
from pathlib import Path

import pytest


@pytest.fixture
def fixture_raw_dir() -> Path:
    return Path(__file__).parent / "fixtures" / "2026" / "week-06" / "raw"


@pytest.fixture
def fixture_history_root() -> Path:
    return Path(__file__).parent / "fixtures" / "2026" / "history"
