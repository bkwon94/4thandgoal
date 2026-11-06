"""
Imports each module of the midseason package in the env of this member only.
The env holds only league, facts, and the listed libraries, so an import of an app or another package fails here.
"""
import importlib
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src" / "midseason"
MODULES = sorted(f"midseason.{path.stem}" for path in SRC.glob("*.py") if path.stem != "__init__")


@pytest.mark.parametrize("name", MODULES)
def test_each_module_imports_with_only_league_and_facts(name):
    assert importlib.import_module(name)


def test_no_module_imports_the_claude_sdk():
    """ADR 0023: the facts package owns the writer, so the Claude errors reach midseason only through facts."""
    import ast

    importers = []
    for path in SRC.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = ([alias.name for alias in node.names] if isinstance(node, ast.Import)
                     else [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
            if any(name.split(".")[0] == "anthropic" for name in names):
                importers.append(path.name)
    assert importers == []
