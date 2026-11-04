"""
The standings table and the season records it reads, built from the parsed week and the saved history.
It sits in the load layer, so the snapshot and the fact groups both read one table with no upward import.
"""
import logging
from collections import defaultdict
from decimal import Decimal

from cornerstone.client import Client
from cornerstone.models import History, PastWeek, Standing, Week
from cornerstone.numbers import r2

logger = logging.getLogger(__name__)


def week_median(week: PastWeek) -> Decimal:
    """The exact median score of one week, the line of the median game."""
    ordered = sorted((Decimal(str(p)) for p in week.scores.values()), reverse=True)
    # The same median as median_facts: the mean of the 6th and 7th scores.
    # A past week holds no client, so the two middle ranks come from the count of scores. A league has an even team
    # count, because every team plays a game each week.
    middle = len(ordered) // 2
    return (ordered[middle - 1] + ordered[middle]) / 2


def season_records(history: History, through: int) -> dict[int, tuple[int, int, float]]:
    """Wins, losses, and points for of each roster over weeks 1 to `through`.

    Each week is two games: the head-to-head game and the game against the median.
    A tie in a game counts as neither a win nor a loss.
    """
    wins: dict[int, int] = defaultdict(int)
    losses: dict[int, int] = defaultdict(int)
    points: dict[int, Decimal] = defaultdict(Decimal)

    def settle(roster_id: int, mine: Decimal, theirs: Decimal) -> None:
        if mine > theirs:
            wins[roster_id] += 1
        elif mine < theirs:
            losses[roster_id] += 1

    for number in range(1, through + 1):
        scores = {rid: Decimal(str(p)) for rid, p in history.weeks[number].scores.items()}
        median = week_median(history.weeks[number])
        for a, b in history.weeks[number].pairs:
            settle(a, scores[a], scores[b])
            settle(b, scores[b], scores[a])
        for rid, score in scores.items():
            settle(rid, score, median)
            points[rid] += score
    return {rid: (wins[rid], losses[rid], r2(float(points[rid]))) for rid in points}


def standings_order(records: dict[int, tuple[int, int, float]]) -> list[int]:
    """The roster IDs in standings order: most wins first, then most points for.

    The standings and the power rankings both use this order, so the two cannot drift.
    """
    return sorted(records, key=lambda rid: (-records[rid][0], -records[rid][2]))


def standings(week: Week, history: History | None = None, *, client: Client) -> list[Standing]:
    """The table after the week, in standings order. The cut reads the playoff spots of `client`, so it follows the
    league."""
    if history is not None and history.complete():
        records = season_records(history, week.week)
    else:
        if history is not None:
            logger.warning("history incomplete: standings from rosters.json")
        records = {
            t.roster_id: (t.wins, t.losses, t.points_for) for t in week.teams.values()
        }
    ordered = standings_order(records)
    cut_wins = records[ordered[client.settings.playoff_spots - 1]][0]
    strength = {rid: _schedule_strength(week, rid, records) for rid in ordered}
    # Rank the highest strength first. A team with no next matchup has no rank.
    by_strength = sorted(
        (rid for rid, s in strength.items() if s is not None),
        key=lambda rid: -strength[rid],
    )
    strength_rank = {rid: i + 1 for i, rid in enumerate(by_strength)}
    return [
        Standing(
            rank=i + 1,
            roster_id=rid,
            wins=records[rid][0],
            losses=records[rid][1],
            points_for=records[rid][2],
            in_playoffs=i + 1 <= client.settings.playoff_spots,
            games_from_cut=records[rid][0] - cut_wins,
            schedule_strength=strength[rid],
            strength_rank=strength_rank.get(rid),
        )
        for i, rid in enumerate(ordered)
    ]


def _schedule_strength(
    week: Week, roster_id: int, records: dict[int, tuple[int, int, float]]
) -> float | None:
    """Mean win rate of the remaining opponents. Version 1 has only the next one."""
    opponents = [
        b if a == roster_id else a
        for a, b in week.next_matchups
        if roster_id in (a, b)
    ]
    if not opponents:
        return None
    rates = [records[o][0] / (records[o][0] + records[o][1]) for o in opponents]
    return r2(sum(rates) / len(rates))
