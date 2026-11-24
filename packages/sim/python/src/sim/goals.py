"""
The Goals of The Race: a playoff spot, a bye, or one seed. It holds the shape of the odds and the status of one Goal, the
team of the League board, and the Goal that the page opens on. The sim in season.py finds the Goals of each team.
"""
from collections.abc import Mapping

from pydantic import BaseModel

from league.models import OddsStatus
from sim.tunables import OPEN_GOAL_ODDS


class GoalOdds(BaseModel):
    """The odds of one Goal in whole percent, by the rule of the shown odds, and its status by the plain check on
    wins. GLOSSARY.md, "Goal", "Clinched", "In the hunt", and "Out"."""
    odds: int
    status: OddsStatus


class BoardTeam(BaseModel):
    """One team of the League board: the odds and the status of each Goal."""
    roster_id: int
    goals: dict[str, GoalOdds]


def open_goal(goals: Mapping[str, GoalOdds]) -> str | None:
    """The Goal the page opens on: the best Goal with odds of OPEN_GOAL_ODDS or more, in the order 1 seed, bye, spot.
    The spot when none reaches it. None with no Goal."""
    if not goals:
        return None
    return next((key for key in ("seed-1", "bye", "spot") if key in goals and goals[key].odds >= OPEN_GOAL_ODDS),
                "spot")
