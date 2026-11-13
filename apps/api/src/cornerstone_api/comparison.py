"""
The comparison block of a typed "Start A or B?": one pair of values for each fact of the two Fact sheets, the side
that wins each fact, the pick of the Jev read, and the dot on each fact whose number the checked text gives.
"""
import re
from collections.abc import Callable
from dataclasses import dataclass

from cornerstone_api.free_wording import plain_text

# The kind of the block. The site picks the view of the comparison from it.
COMPARISON_KIND = "comparison"
# The positions that gain from a pass-heavy team. A RB gains from a run-heavy team.
PASS_POSITIONS = frozenset({"QB", "WR", "TE"})


@dataclass(frozen=True)
class Fact:
    """One fact of the comparison: its key, its label, how to read its value from a Fact sheet, how to show the value,
    and whether more is better for the player."""

    key: str
    label: str
    value: Callable[[dict], float | None]
    shown: Callable[[float], str]
    higher_wins: bool = True


def _points(value: float) -> str:
    return f"{value:.1f}"


def _margin(value: float) -> str:
    return f"{value:+.1f}" if value else "0.0"


def _percent(value: float) -> str:
    return f"{round(value * 100)}%"


def _usage(key: str) -> Callable[[dict], float | None]:
    return lambda sheet: (sheet.get("last_3_weeks") or {}).get(key)


FACTS = [
    Fact("projection", "Projection", lambda sheet: sheet.get("projection"), _points),
    # More points allowed to his position is a softer matchup for the player.
    Fact("defense", "Defense allows", lambda sheet: (sheet.get("defense_against_position") or {}).get("allowed_per_game"),
         _points),
    Fact("team_points", "Team points", lambda sheet: sheet.get("team_projected_points"), _points),
    Fact("margin", "Expected margin", lambda sheet: sheet.get("expected_margin"), _margin),
    Fact("snap_share", "Snap share, 3 wk", _usage("snap_share"), _percent),
    Fact("target_share", "Target share, 3 wk", _usage("target_share"), _percent),
    Fact("carry_share", "Carry share, 3 wk", _usage("carry_share"), _percent),
]


def _winner(values: list[float | None], higher_wins: bool) -> int | None:
    a, b = values
    if a is None or b is None or a == b:
        return None
    return int((b > a) == higher_wins)


def _row(key: str, label: str, values: list[float | None], shown: Callable[[float], str], winner: int | None) -> dict:
    return {"key": key, "label": label, "values": values,
            "shown": [None if value is None else shown(value) for value in values], "winner": winner, "cited": False}


def compare_facts(sheets: list[dict]) -> list[dict]:
    """The facts of two Fact sheets, each with the two values, the values as the block shows them, and the side that
    wins it. A fact with no value on either side, or a usage share of 0 on both sides, has no row."""
    rows = []
    for fact in FACTS:
        values = [fact.value(sheet) for sheet in sheets]
        if all(value is None for value in values) or (fact.key.endswith("_share") and not any(values)):
            continue
        rows.append(_row(fact.key, fact.label, values, fact.shown, _winner(values, fact.higher_wins)))
    shares = [sheet.get("team_pass_share") for sheet in sheets]
    if any(share is not None for share in shares):
        # A pass-heavy team wins this fact for a QB, a WR, or a TE, and a run-heavy team for a RB, so two players who
        # gain from different tilts have no side that wins it.
        gains = {sheet.get("position") in PASS_POSITIONS for sheet in sheets}
        winner = _winner(shares, gains == {True}) if len(gains) == 1 else None
        rows.append(_row("pass_share", "Team pass share", shares, _percent, winner))
    return rows


def _number(shown: str) -> str:
    """The digits of a shown value, with no sign and no percent sign: "+3.5" gives "3.5", and "24%" gives "24"."""
    return shown.lstrip("+-").removesuffix("%")


def with_cites(block: dict, text: str) -> dict:
    """The comparison block with a dot on each fact whose number, as the block shows it, is in the checked `text`. The
    check passed each sentence, so a dot never marks a fact of a sentence that the check did not pass."""
    said = plain_text(text)
    facts = []
    for fact in block["facts"]:
        numbers = [_number(shown) for shown in fact["shown"] if shown is not None]
        cited = any(re.search(rf"(?<![\d.]){re.escape(number)}(?![\d]|\.\d)", said) for number in numbers)
        facts.append({**fact, "cited": cited})
    return {**block, "facts": facts}
