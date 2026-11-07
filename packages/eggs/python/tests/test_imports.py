"""
Imports each module of the eggs package in the env of this member only.
The env holds only league and the listed libraries, so an import of an app or another package fails here.
"""
import importlib
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src" / "eggs"
MODULES = sorted(f"eggs.{path.stem}" for path in SRC.glob("*.py") if path.stem != "__init__")


@pytest.mark.parametrize("name", MODULES)
def test_each_module_imports_with_only_league(name):
    assert importlib.import_module(name)
