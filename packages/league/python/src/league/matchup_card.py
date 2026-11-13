"""
The matchup card of Your last matchup and Your next matchup: its model and the rows of its slots. The weekly build of the
pipeline and the live card of the API share it, so it lives in the league package that both import.
"""
from typing import Literal

from pydantic import BaseModel, Field

from league.lineup import BENCH_SLOTS


class MatchupPlayer(BaseModel):
    """The player of one side in one slot of a matchup card. The points are final for a played game and the
    projection for a game ahead."""
    name: str
    position: str
    nfl_team: str | None
    points: float


class MatchupSlot(BaseModel):
    """One starting slot of a matchup card, such as RB or FLEX, with the player of each side. A side with an empty
    slot has None there. The site draws the gap of the slot from the two points."""
    slot: str
    you: MatchupPlayer | None
    them: MatchupPlayer | None


class MatchupTeam(BaseModel):
    """One team of a matchup card with its total: the final score or the projected score."""
    roster_id: int
    name: str
    score: float


class MatchupBlock(BaseModel):
    """The matchup card of Your last matchup and Your next matchup: the two teams, their scores, and the starting
    slots in the Sleeper order of the league. `final` tells final scores from projected ones. `odds` is the win chance
    of Your team from 0 to 1 for a game ahead, or None when no odds are known, such as for a played game. The weekly
    build and the live card of the API share this model. `read_at` is the time of the live read of Sleeper, in ISO 8601,
    on the live card of the API only. The weekly build leaves it out of topics.json."""
    kind: Literal["matchup"] = "matchup"
    final: bool
    you: MatchupTeam
    them: MatchupTeam
    odds: float | None = None
    slots: list[MatchupSlot]
    read_at: str | None = Field(default=None, exclude_if=lambda value: value is None)


def starting_slots(roster_positions: list[str]) -> list[str]:
    """The starting slots of a league in the Sleeper order, such as QB, RB, RB, FLEX, with the bench slots left out."""
    return [slot for slot in roster_positions if slot not in BENCH_SLOTS]


def matchup_slots(slots: list[str], you: list[tuple[str, MatchupPlayer]],
                  them: list[tuple[str, MatchupPlayer]]) -> list[MatchupSlot]:
    """The rows of a matchup card: each starting slot in `slots` with the next player of each side for that slot.
    Each side lists its starters as pairs of the slot and the player, best first within a slot, so RB1 meets RB1."""
    def take(side: list[tuple[str, MatchupPlayer]], slot: str) -> MatchupPlayer | None:
        at = next((i for i, (each, _) in enumerate(side) if each == slot), None)
        return None if at is None else side.pop(at)[1]

    left, right = list(you), list(them)
    return [MatchupSlot(slot=slot, you=take(left, slot), them=take(right, slot)) for slot in slots]
