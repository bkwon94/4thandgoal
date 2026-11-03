"""
Prints the offenses of a rule test in one shape: the place and the rule id, what is wrong, the rule, and the fix.
Every rule test uses it, so an agent reads one shape. It imports no pipeline code. See ADR 0009.
"""
import os
from dataclasses import dataclass


def clean_git_env() -> dict[str, str]:
    """The environment with no GIT_DIR, GIT_INDEX_FILE, or GIT_WORK_TREE.

    Under the prek hook, git sets these. With GIT_DIR set and no GIT_WORK_TREE, git takes the current folder
    as the top of the tree, so a git call from apps/pipeline would read the paths of the repo root.
    """
    env = dict(os.environ)
    for name in ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE"):
        env.pop(name, None)
    return env


@dataclass(frozen=True)
class Offense:
    """One break of a rule at one place.

    The path is from the repo root. The rule id is <topic>/<name>, such as layers/upward-import.
    """
    path: str
    line: int
    rule_id: str
    what: str
    rule: str
    adr: str
    fix: str


def _format(offense: Offense) -> str:
    return "\n".join([
        f"{offense.path}:{offense.line}  {offense.rule_id}",
        f"  {offense.what}",
        f"  Rule: {offense.rule} ({offense.adr}).",
        f"  Fix: {offense.fix}",
    ])


def report(offenses: list[Offense]) -> str:
    """The count, then each offense, with a blank line between. A test asserts `not offenses, report(offenses)`."""
    count = f"{len(offenses)} offense." if len(offenses) == 1 else f"{len(offenses)} offenses."
    return "\n\n".join([count] + [_format(offense) for offense in offenses])
