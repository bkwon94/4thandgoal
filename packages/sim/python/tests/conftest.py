"""
Shared pytest setup for the sim package tests. The rule modules come from the pipeline tests.
The rule modules use only the standard library, so they import here with no pipeline code.
"""
import sys
from pathlib import Path

# The pipeline tests hold the rule modules and rule_report. The sim package owns no copy of them.
PIPELINE_TESTS = Path(__file__).resolve().parents[4] / "apps" / "pipeline" / "tests"
sys.path.insert(0, str(PIPELINE_TESTS))
