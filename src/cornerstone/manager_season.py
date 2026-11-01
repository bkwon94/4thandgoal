"""
The season so far of a manager entry: the points per week, the bench points, and the awards shelf.
Pure code over the saved history, except saved_awards, which reads the saved facts files.
"""
import json
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel

from cornerstone.adjusters import fill_slots
from cornerstone.facts_league import head_to_head, week_median
from cornerstone.models import History, PastWeek
from cornerstone.numbers import r2

# The award keys the shelf counts. The Overachiever award is not on the shelf.
SHELF_KEYS = ("top_scorer", "mvb", "game_changer", "underperformer")


class SeasonWeek(BaseModel):
    """One saved week of a roster: its points, the league median, and the head-to-head result."""
    week: int
    points: float
    median: float
    # None when the roster has no head-to-head game that week, such as a bye, or when the game is a tie.
    won: bool | None


class BenchWorst(BaseModel):
    """The week the bench cost the most points, and the bench player of the best lineup with the most points."""
    week: int
    points: float
    player_id: str
    name: str


class Bench(BaseModel):
    """The bench points of the season: the best lineup's points minus the points of the lineup it started."""
    total: float
    # None when no week of the season cost a point.
    worst: BenchWorst | None


class AwardCounts(BaseModel):
    """The awards shelf: the count of each shelf award over the weeks a report ran."""
    top_scorer: int = 0
    mvb: int = 0
    game_changer: int = 0
    underperformer: int = 0


def season_weeks(history: History, roster_id: int) -> list[SeasonWeek]:
    """The points per saved week of one roster, in week order."""
    out = []
    for number in range(1, history.week + 1):
        week = history.weeks[number]
        result = head_to_head(week, roster_id)
        out.append(SeasonWeek(
            week=number,
            points=week.scores[roster_id],
            median=r2(float(week_median(week))),
            won=None if result is None or result[1] == 0 else result[1] > 0,
        ))
    return out


def _week_bench(week: PastWeek, roster_id: int, slots: list[str]) -> tuple[Decimal, str | None]:
    """The bench cost of one week, and the bench player of the best lineup with the most points."""
    points = {pid: Decimal(str(p)) for pid, p in week.points.items()}
    # A player with no stat line has no position, so no slot can take him. He scored nothing.
    roster = [pid for pid in week.rosters.get(roster_id, []) if pid in week.positions]
    best = [pid for _, pid in fill_slots(roster, slots, week.positions, points) if pid is not None]
    started = week.starters.get(roster_id, [])
    cost = sum((points.get(pid, Decimal(0)) for pid in best), Decimal(0)) - sum(
        (points.get(pid, Decimal(0)) for pid in started), Decimal(0),
    )
    sat = [pid for pid in best if pid not in started]
    # The player id breaks a tie, so the same week always names the same player.
    top = min(sat, key=lambda pid: (-points.get(pid, Decimal(0)), pid)) if sat else None
    return cost, top


def bench_points(history: History, roster_id: int, slots: list[str], names: dict[str, str]) -> Bench:
    """The bench points of one roster over the saved weeks. A name not in `names` falls back to the player id."""
    total = Decimal(0)
    worst_cost = Decimal(0)
    worst: BenchWorst | None = None
    for number in range(1, history.week + 1):
        cost, top = _week_bench(history.weeks[number], roster_id, slots)
        total += cost
        # A later week must cost more to replace the worst week, so a tie keeps the earlier week.
        if cost > worst_cost and top is not None:
            worst_cost = cost
            worst = BenchWorst(week=number, points=r2(float(cost)), player_id=top, name=names.get(top, top))
    return Bench(total=r2(float(total)), worst=worst)


def award_counts(week_awards: dict[int, list[tuple[str, int]]], roster_id: int, through: int) -> AwardCounts:
    """The shelf counts of one roster over weeks 1 to `through`. A week with no report adds nothing."""
    counts = {key: 0 for key in SHELF_KEYS}
    for number in range(1, through + 1):
        for key, rid in week_awards.get(number, []):
            if rid == roster_id and key in counts:
                counts[key] += 1
    return AwardCounts(**counts)


def saved_awards(facts_files: dict[int, Path]) -> dict[int, list[tuple[str, int]]]:
    """The award key and the roster id of each award, per week, from the saved facts file of each week.

    A week whose file does not exist had no report, so it is not in the result.
    """
    out = {}
    for number, path in facts_files.items():
        if not path.exists():
            continue
        body = json.loads(path.read_text(encoding="utf-8"))
        out[number] = [(award["key"], award["roster_id"]) for award in body["data"]["awards"]]
    return out
