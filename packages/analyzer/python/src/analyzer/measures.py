"""
The Measures of the Advisor sheet: each old adjuster of the rubric writes its read of one side as one fact.
A Measure moves nothing. Its step stays out of the fact, and the Advisor weighs the read with the other facts.
"""
import re

from analyzer.adjusters import (
    ADJUSTERS,
    EXPECTED,
    HANDCUFF,
    INJURY,
    ROSTER_FIT,
    SCHEDULE,
    STANDING,
    SUPERSTAR,
    TREND,
    UPSIDE,
    Side,
)
from facts.tokens import Nums, fact
from league.models import Fact
from league.snapshot import Snapshot

# The short id of each Measure, the last part of its fact id, such as 10.measure.trend.
MEASURE_IDS = {ROSTER_FIT: "fit", STANDING: "standing", TREND: "trend", INJURY: "injury", UPSIDE: "upside",
               SUPERSTAR: "superstar", HANDCUFF: "handcuff", SCHEDULE: "schedule", EXPECTED: "expected"}


def _names_in(text: str, snapshot: Snapshot) -> list[str]:
    """The full player names that the text holds, so the guard lets a Bullet that cites the fact name them."""
    return [p.name for p in snapshot.players.values() if re.search(rf"(?<!\w){re.escape(p.name)}(?!\w)", text)]


def measure_facts(snapshot: Snapshot, sides: tuple[Side, ...]) -> list[Fact]:
    """One fact per Measure and side, in the order of the old adjusters. A silent read, such as "No player it gets
    is a superstar.", writes no fact. The text says "you" for the side the fact names."""
    facts = []
    for side in sides:
        team = snapshot.teams[side.roster_id].name
        for measure in ADJUSTERS:
            read = measure(snapshot, side)
            if read.silent:
                continue
            n = Nums()
            text = f"The {read.name} measure for {team}: {n.text(read.reason)}"
            facts.append(fact(f"{side.roster_id}.measure.{MEASURE_IDS[read.name]}", text, n, [team],
                              _names_in(read.reason, snapshot)))
    return facts
