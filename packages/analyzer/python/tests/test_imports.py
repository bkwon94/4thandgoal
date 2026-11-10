"""
Imports each module of the analyzer package in the env of this member only.
The env holds only league, facts, and the listed libraries, so an import of an app or another package fails here.
"""
import importlib
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src" / "analyzer"
MODULES = sorted(f"analyzer.{path.stem}" for path in SRC.glob("*.py") if path.stem != "__init__")


@pytest.mark.parametrize("name", MODULES)
def test_each_module_imports_with_only_league_and_facts(name):
    assert importlib.import_module(name)


def test_the_rule_prompts_sit_in_the_package():
    from analyzer import RULE_PROMPTS

    assert sorted(path.name for path in RULE_PROMPTS.glob("*.md")) == ["advisor.md", "finder_pick.md"]
