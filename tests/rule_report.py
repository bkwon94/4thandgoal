"""
Prints the offenses of a rule test in one shape: the place and the rule id, what is wrong, the rule, and the fix.
Every rule test uses it, so an agent reads one shape. It imports no pipeline code. See ADR 0009.
"""
from dataclasses import dataclass


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


def _lines(offense: Offense) -> str:
    return "\n".join([
        f"{offense.path}:{offense.line}  {offense.rule_id}",
        f"  {offense.what}",
        f"  Rule: {offense.rule} ({offense.adr}).",
        f"  Fix: {offense.fix}",
    ])


def report(offenses: list[Offense]) -> str:
    """The count, then each offense, with a blank line between. A test asserts `not offenses, report(offenses)`."""
    count = f"{len(offenses)} offense." if len(offenses) == 1 else f"{len(offenses)} offenses."
    return "\n\n".join([count] + [_lines(offense) for offense in offenses])
