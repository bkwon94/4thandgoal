"""
Shared pytest setup for the waiver package tests: the week 6 raw fixtures, the CPC client, and the rule modules.
Each comes from the pipeline tests, and none of them imports pipeline code.
"""
import sys
from pathlib import Path

import pytest

# The pipeline tests hold the week 6 fixtures, the CPC client of the tests, the fakes, and the rule modules.
# The waiver package owns no copy of them.
PIPELINE_TESTS = Path(__file__).resolve().parents[4] / "apps" / "pipeline" / "tests"
sys.path.insert(0, str(PIPELINE_TESTS))


@pytest.fixture
def fixture_raw_dir() -> Path:
    return PIPELINE_TESTS / "fixtures" / "2026" / "week-06" / "raw"


@pytest.fixture
def fixture_history_root() -> Path:
    return PIPELINE_TESTS / "fixtures" / "2026" / "history"
