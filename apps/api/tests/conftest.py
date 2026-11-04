"""
Shared pytest fixtures for the API tests. They come from the pipeline tests, with the recorded week 6 data.
The API serves the same league data as the pipeline, so its tests read the same fixture files.
"""
import importlib.util
import sys
from pathlib import Path

# The pipeline tests hold the fixture files and the helper modules fakes and rule_report.
PIPELINE_TESTS = Path(__file__).resolve().parents[2] / "pipeline" / "tests"
sys.path.insert(0, str(PIPELINE_TESTS))

# The file loads under its own name, because this file is the module conftest of the API tests.
_spec = importlib.util.spec_from_file_location("pipeline_conftest", PIPELINE_TESTS / "conftest.py")
assert _spec is not None and _spec.loader is not None
_pipeline = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pipeline)

chart_week6 = _pipeline.chart_week6
fixture_history_root = _pipeline.fixture_history_root
fixture_nflverse_dir = _pipeline.fixture_nflverse_dir
fixture_raw_dir = _pipeline.fixture_raw_dir
strip_trend_numbers = _pipeline.strip_trend_numbers
