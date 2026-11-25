"""
The Goals of The Race: a playoff spot, a bye, or one seed. It holds the shape of the odds and the status of one Goal, the
team of the League board with the shape of its Clinch lines, and the Goal that the page opens on. The sim in season.py finds the Goals of each team.
"""
from collections.abc import Mapping
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from league.models import OddsStatus
from sim.tunables import OPEN_GOAL_ODDS


class GoalOdds(BaseModel):
    """The odds of one Goal in whole percent, by the rule of the shown odds, and its status by the plain check on
    wins. GLOSSARY.md, "Goal", "Clinched", "In the hunt", and "Out"."""
    odds: int
    status: OddsStatus


class GameResult(BaseModel):
    """A game of another team this week, by its winner and its loser."""
    kind: Literal["game"] = "game"
    winner: int
    loser: int


class MedianResult(BaseModel):
    """The median result of another team this week."""
    kind: Literal["median"] = "median"
    roster_id: int
    median: Literal["above", "below"]


class ClinchWay(BaseModel):
    """One way of a Clinch line: the result of the team itself, and the results of other teams it needs. Every set of
    results that fits the way gives the status of its line. A result of None is any result."""
    game: Literal["win", "loss"] | None
    median: Literal["above", "below"] | None
    others: list[Annotated[GameResult | MedianResult, Field(discriminator="kind")]]
    # The share of the runs of the sim whose results of this week fit the way, in percent to one decimal.
    chance: float


class ClinchLine(BaseModel):
    """The Clinch line of one team for one Goal and one status: each way, most likely first. GLOSSARY.md, "Clinch
    line". The ways list every set of results that gives the status, unless they stop at CLINCH_WAYS."""
    goal: Literal["spot", "bye"]
    status: Literal["in", "out"]
    ways: list[ClinchWay]


class BoardTeam(BaseModel):
    """One team of the League board: the odds and the status of each Goal, and the Clinch lines of the next week. The
    weekly build writes the lines. A What-if holds none."""
    roster_id: int
    goals: dict[str, GoalOdds]
    clinch: list[ClinchLine] = []


def open_goal(goals: Mapping[str, GoalOdds]) -> str | None:
    """The Goal the page opens on: the best Goal with odds of OPEN_GOAL_ODDS or more, in the order 1 seed, bye, spot.
    The spot when none reaches it. None with no Goal."""
    if not goals:
        return None
    return next((key for key in ("seed-1", "bye", "spot") if key in goals and goals[key].odds >= OPEN_GOAL_ODDS),
                "spot")
