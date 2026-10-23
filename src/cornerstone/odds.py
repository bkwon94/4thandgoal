"""
The playoff odds engine: a Monte Carlo of the remaining weeks that gives each roster its odds and seed.
It also gives the swing of each next-week game. Pure code: no network and no Claude.
"""
import random
from collections import Counter
from typing import Literal

from pydantic import BaseModel

from cornerstone.tunables import (
    BYE_COUNT,
    PLAYOFF_SPOTS,
    PROJECTION_WEIGHT,
    RECENT_WEEKS,
    RECENT_WEIGHT,
    SEED_SHOW_AT,
    SIM_RUNS,
)

Status = Literal["in", "out", "open"]
ByeStatus = Literal["bye_sure", "bye_gone", "open"]
# A week has two games, the head-to-head game and the median game, so a roster wins at most 2 a week.
MAX_WINS_PER_WEEK = 2


class TeamOdds(BaseModel):
    """The odds of one roster. Each odds number is a whole percent."""
    roster_id: int
    playoff: int
    bye: int
    # The most likely seed. None when the playoff odds are below SEED_SHOW_AT.
    seed: int | None
    status: Status


class Swing(BaseModel):
    """The playoff odds of both sides of one next-week game. Each side has its odds after a win and after a loss."""
    a: int
    b: int
    a_win: int
    a_loss: int
    b_win: int
    b_loss: int


class OddsResult(BaseModel):
    """The odds of every roster, keyed by roster ID, and the swing of each next-week game in pair order."""
    teams: dict[int, TeamOdds]
    swings: list[Swing]


def playoff_odds(
    scores: dict[int, list[float]],
    records: dict[int, tuple[int, int, float]],
    remaining: dict[int, list[tuple[int, int]]],
    *,
    season: int,
    week: int,
    playoff_spots: int = PLAYOFF_SPOTS,
    bye_count: int = BYE_COUNT,
    runs: int = SIM_RUNS,
    projected: dict[int, dict[int, float]] | None = None,
    projection_weight: float = PROJECTION_WEIGHT,
) -> OddsResult:
    """The playoff odds after week `week`.

    `scores` holds each roster's played-week scores, oldest first. `records` holds the real wins, losses,
    and points for. `remaining` holds the pairs of each remaining week; the first week is week N+1.
    `projected` holds the projected best-lineup total of each roster, by roster ID and week. Each drawn
    score of a week moves by `projection_weight` times the gap from that total to the roster's season average.
    """
    if len(records) % 2:
        raise ValueError(f"the median rule needs an even count of rosters, got {len(records)}")
    weeks_left = len(remaining)
    if not weeks_left:
        return _final_table(records, playoff_spots, bye_count)

    # Sorted roster IDs, so each draw and each sort reads the rosters in one fixed order, whatever the dict order.
    rosters = sorted(records)
    status = {rid: _status(rid, records, weeks_left, playoff_spots) for rid in rosters}
    bye_status = {rid: _bye_status(rid, records, weeks_left, bye_count) for rid in rosters}
    # The random seed derives from the season and the week, so the same inputs give the same odds.
    rng = random.Random(season * 100 + week)
    order = [remaining[w] for w in sorted(remaining)]
    weights = {rid: _draw_weights(scores[rid]) for rid in rosters}
    shifts = _shifts(scores, projected, sorted(remaining), projection_weight) if projected else None
    next_pairs = order[0]
    made: Counter[int] = Counter()
    byes: Counter[int] = Counter()
    seeds: dict[int, Counter[int]] = {rid: Counter() for rid in rosters}
    # Per next-week pair and per winner, three counts: the runs, the runs side a made it, the runs side b made it.
    halves = {pair: {"a": [0, 0, 0], "b": [0, 0, 0]} for pair in next_pairs}
    for _ in range(runs):
        drawn = {rid: rng.choices(scores[rid], cum_weights=weights[rid], k=weeks_left) for rid in rosters}
        if shifts:
            drawn = {rid: [score + shift for score, shift in zip(d, shifts[rid])] for rid, d in drawn.items()}
        table = _run(records, order, drawn)
        top = set(table[:playoff_spots])
        for place, rid in enumerate(table[:playoff_spots], start=1):
            made[rid] += 1
            seeds[rid][place] += 1
            if place <= bye_count:
                byes[rid] += 1
        for a, b in next_pairs:
            # An exact tie is neither a win nor a loss, so the run lands in neither half.
            if drawn[a][0] == drawn[b][0]:
                continue
            half = halves[(a, b)]["a" if drawn[a][0] > drawn[b][0] else "b"]
            half[0] += 1
            half[1] += a in top
            half[2] += b in top

    teams = {}
    for rid in rosters:
        playoff = _shown(status[rid], made[rid], runs)
        # The most common seed; a tie between two seeds goes to the better seed.
        seed = min(seeds[rid], key=lambda s: (-seeds[rid][s], s)) if seeds[rid] else None
        teams[rid] = TeamOdds(
            roster_id=rid,
            playoff=playoff,
            bye=_shown_bye(bye_status[rid], status[rid], byes[rid], runs, playoff),
            seed=seed if playoff >= SEED_SHOW_AT else None,
            status=status[rid],
        )
    swings = [_swing(a, b, halves[(a, b)], status, teams) for a, b in next_pairs]
    return OddsResult(teams=teams, swings=swings)


def _draw_weights(values: list[float]) -> list[float]:
    """The cumulative draw weights of a roster's played-week scores. The last RECENT_WEEKS weeks weigh more."""
    cum, total = [], 0.0
    for i in range(len(values)):
        total += RECENT_WEIGHT if i >= len(values) - RECENT_WEEKS else 1
        cum.append(total)
    return cum


def _shifts(
    scores: dict[int, list[float]], projected: dict[int, dict[int, float]], weeks: list[int], weight: float,
) -> dict[int, list[float]]:
    """The shift of each roster's drawn score in each remaining week, in the order of `weeks`.

    A week with no projected total for the roster has no shift.
    """
    shifts = {}
    for rid, values in scores.items():
        average = sum(values) / len(values)
        totals = projected.get(rid, {})
        shifts[rid] = [weight * (totals[w] - average) if w in totals else 0.0 for w in weeks]
    return shifts


def _run(
    records: dict[int, tuple[int, int, float]],
    order: list[list[tuple[int, int]]],
    drawn: dict[int, list[float]],
) -> list[int]:
    """One run of the remaining weeks. It returns the final table in seed order."""
    wins = {rid: r[0] for rid, r in records.items()}
    points = {rid: r[2] for rid, r in records.items()}
    for i, pairs in enumerate(order):
        week = {rid: d[i] for rid, d in drawn.items()}
        for a, b in pairs:
            if week[a] > week[b]:
                wins[a] += 1
            elif week[b] > week[a]:
                wins[b] += 1
        median = _median(list(week.values()))
        for rid, score in week.items():
            if score > median:
                wins[rid] += 1
            points[rid] += score
    return _table_order(wins, points)


def _table_order(wins: dict[int, int], points: dict[int, float]) -> list[int]:
    """The roster IDs in seed order: most wins first, then most points for, then the lower roster ID.

    The same order as standings_order in facts_league.py. Roster ID is the last key, so a full tie has one fixed order.
    """
    return sorted(wins, key=lambda rid: (-wins[rid], -points[rid], rid))


def _median(scores: list[float]) -> float:
    """The line of the median game: the mean of the two middle scores, the 6th and 7th of 12.

    The same rule as week_median in facts_league.py, for any even count of rosters.
    Floats are exact here. The mean equals a score only when both middle scores are equal.
    Then it equals that score exactly, so a tie stays a tie.
    """
    ordered = sorted(scores, reverse=True)
    middle = len(ordered) // 2
    return (ordered[middle - 1] + ordered[middle]) / 2


def _status(roster_id: int, records: dict[int, tuple[int, int, float]], weeks_left: int, spots: int) -> Status:
    """In, out, or open, by a plain check on wins, not by the runs. Both `in` and `out` are sure.

    `in`: no roster outside the top spots by wins can reach this roster's wins with 2 wins every week left.
    `out`: this roster cannot reach the wins of the roster in the last spot with 2 wins every week left.
    """
    by_wins = sorted(records, key=lambda rid: (-records[rid][0], rid))
    reach = MAX_WINS_PER_WEEK * weeks_left
    wins = records[roster_id][0]
    if roster_id in by_wins[:spots] and all(records[o][0] + reach < wins for o in by_wins[spots:]):
        return "in"
    if wins + reach < records[by_wins[spots - 1]][0]:
        return "out"
    return "open"


def _shown(status: Status, made: int, runs: int) -> int:
    """The odds as shown: 100 for `in`, 0 for `out`, and the whole percent clamped to 1 to 99 for `open`."""
    if status == "in":
        return 100
    if status == "out":
        return 0
    return min(99, max(1, _percent(made, runs)))


def _bye_status(
    roster_id: int, records: dict[int, tuple[int, int, float]], weeks_left: int, bye_count: int,
) -> ByeStatus:
    """Sure, gone, or open for the bye, by the same plain check on wins as the playoff status.

    `bye_sure`: no roster outside the top `bye_count` by wins can reach this roster's wins with 2 wins every week left.
    `bye_gone`: this roster cannot reach the wins of the roster in the last bye spot with 2 wins every week left.
    """
    # The bye spots are the top `bye_count` seeds, so the playoff check with that count is the bye check.
    return {"in": "bye_sure", "out": "bye_gone", "open": "open"}[_status(roster_id, records, weeks_left, bye_count)]


def _shown_bye(bye_status: ByeStatus, status: Status, byes: int, runs: int, playoff: int) -> int:
    """The bye odds as shown: 100 for `bye_sure`, 0 for `bye_gone` or `out`, else clamped to 1 to 99.

    A bye needs a playoff spot, so the open bye odds never read above the shown playoff odds.
    """
    if bye_status == "bye_sure":
        return 100
    if bye_status == "bye_gone" or status == "out":
        return 0
    return min(99, max(1, _percent(byes, runs)), playoff)


def _percent(part: int, total: int) -> int:
    """`part` over `total` as a whole percent."""
    # Round half up in integers. Python's round() rounds half to even, so 2.5 would show as 2.
    return (200 * part + total) // (2 * total)


def _swing(a: int, b: int, half: dict[str, list[int]], status: dict[int, Status], teams: dict[int, TeamOdds]) -> Swing:
    """Both sides' odds in the runs where side a won and in the runs where side b won.

    A half with no run falls back to the full odds, since the runs never saw that result.
    """
    def side(rid: int, runs_and_made: list[int], index: int) -> int:
        count = runs_and_made[0]
        if not count:
            return teams[rid].playoff
        return _shown(status[rid], runs_and_made[index], count)

    return Swing(
        a=a,
        b=b,
        a_win=side(a, half["a"], 1),
        a_loss=side(a, half["b"], 1),
        b_win=side(b, half["b"], 2),
        b_loss=side(b, half["a"], 2),
    )


def _final_table(records: dict[int, tuple[int, int, float]], spots: int, bye_count: int) -> OddsResult:
    """The result with no weeks left: the real table sets every roster, with no runs.

    The seed order settles a tie on wins too.
    """
    table = _table_order({rid: r[0] for rid, r in records.items()}, {rid: r[2] for rid, r in records.items()})
    teams = {}
    for place, rid in enumerate(table, start=1):
        made = place <= spots
        teams[rid] = TeamOdds(
            roster_id=rid,
            playoff=100 if made else 0,
            bye=100 if place <= bye_count else 0,
            seed=place if made else None,
            status="in" if made else "out",
        )
    return OddsResult(teams=teams, swings=[])
