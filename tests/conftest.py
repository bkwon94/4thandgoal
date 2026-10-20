"""
Shared pytest fixtures for the Cornerstone Weekly tests.
They give tests the path to the recorded Sleeper data.
"""
from pathlib import Path

import pytest

from cornerstone.history import load_history
from cornerstone.parse import parse_week
from cornerstone.sheet import build_bundle
from cornerstone.sleeper import load_raw


@pytest.fixture
def fixture_raw_dir() -> Path:
    return Path(__file__).parent / "fixtures" / "2026" / "week-06" / "raw"


@pytest.fixture
def fixture_history_root() -> Path:
    return Path(__file__).parent / "fixtures" / "2026" / "history"


@pytest.fixture
def hbundle(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    return build_bundle(parse_week(raw), news=lambda pid: [],
                        history=load_history(fixture_history_root, raw, week=6))
