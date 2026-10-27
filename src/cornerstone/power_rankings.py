"""
Power rankings: a rank per team per week from four components, standing, form, schedule played, and scoring.
Pure code over the saved history. No trade value and no chart enter the formula.
"""
from decimal import Decimal

from cornerstone.facts_league import TREND_WEEKS, head_to_head, season_records, standings_order, week_median
from cornerstone.models import History, PastWeek, PowerRow
from cornerstone.tunables import FORM_HEAD_TO_HEAD_WEIGHT, FORM_MEDIAN_WEIGHT, POWER_WEIGHTS

# A quality win is a win against a team in this many top places of the standings.
QUALITY_TOP = 4
# The neutral half of a rate with no game behind it,
# so the formula does not punish a team for a schedule it did not choose.
NEUTRAL = 0.5
# The longest form streak: both weighted games of every week in the form window.
# The scale runs from minus this to plus this.
STREAK_CAP = (FORM_HEAD_TO_HEAD_WEIGHT + FORM_MEDIAN_WEIGHT) * TREND_WEEKS


def power_rankings(history: History, through: int) -> dict[int, list[PowerRow]]:
    """The power rankings of every week from 1 to `through`, each as of that week, best first."""
    out: dict[int, list[PowerRow]] = {}
    for week in range(1, through + 1):
        before = {row.roster_id: row.power_rank for row in out.get(week - 1, [])}
        out[week] = _week_rows(history, week, before)
    return out


def _week_rows(history: History, week: int, before: dict[int, int]) -> list[PowerRow]:
    records = season_records(history, week)
    standing = standings_order(records)
    standing_rank = {rid: i + 1 for i, rid in enumerate(standing)}
    weeks = [history.weeks[n] for n in range(1, week + 1)]
    recent = weeks[-TREND_WEEKS:]
    values = {
        "standing": {rid: _scaled(len(standing) - standing_rank[rid], 0, len(standing) - 1) for rid in standing},
        "form": _form(recent, standing),
        "schedule_played": _schedule_played(weeks, standing),
        "scoring": _scoring(weeks, records),
    }
    ranks = {name: _rank(scores, standing_rank) for name, scores in values.items()}
    score = {rid: sum(POWER_WEIGHTS[name] * values[name][rid] for name in values) for rid in standing}
    power = _rank(score, standing_rank)
    return sorted(
        (
            PowerRow(
                roster_id=rid,
                power_rank=power[rid],
                movement=before[rid] - power[rid] if rid in before else None,
                power_score=score[rid],
                values={name: values[name][rid] for name in values},
                ranks={name: ranks[name][rid] for name in ranks},
                head_to_head=_head_to_head_record(recent, rid),
                median=_median_record(recent, rid),
                form_weeks=len(recent),
            )
            for rid in standing
        ),
        key=lambda row: row.power_rank,
    )


def _rank(scores: dict[int, float], standing_rank: dict[int, int]) -> dict[int, int]:
    """Rank 1 for the highest score. A tie goes to the better standing rank."""
    ordered = sorted(scores, key=lambda rid: (-scores[rid], standing_rank[rid]))
    return {rid: i + 1 for i, rid in enumerate(ordered)}


def _scaled(x: float, low: float, high: float) -> float:
    """`x` on a 0 to 1 scale from `low` to `high`. A flat range gives the neutral value."""
    return (x - low) / (high - low) if high != low else NEUTRAL


def _rate(wins: int, losses: int) -> float:
    """Wins over decided games. A tie is neither, the same as the season records."""
    return wins / (wins + losses) if wins + losses else NEUTRAL


def _all_play_rate(weeks: list[PastWeek], roster_id: int) -> float:
    """The all-play win rate: each week the roster plays every other team. A tie is neither."""
    wins = losses = 0
    for week in weeks:
        mine = week.scores[roster_id]
        others = [s for rid, s in week.scores.items() if rid != roster_id]
        wins += sum(mine > s for s in others)
        losses += sum(mine < s for s in others)
    return _rate(wins, losses)


def _head_to_head_record(weeks: list[PastWeek], roster_id: int) -> tuple[int, int]:
    """Head-to-head wins and losses over the weeks. The median game is not counted."""
    results = [g[1] for g in (head_to_head(w, roster_id) for w in weeks) if g is not None]
    return results.count(1), results.count(-1)


def _median_result(week: PastWeek, roster_id: int) -> int:
    """The result of the median game: 1 is a win, -1 a loss, 0 a tie."""
    # Decimal, as season_records settles it, so a float never flips a game at the median.
    mine, median = Decimal(str(week.scores[roster_id])), week_median(week)
    return (mine > median) - (mine < median)


def _median_record(weeks: list[PastWeek], roster_id: int) -> tuple[int, int]:
    """Median game wins and losses over the weeks. A tie is neither."""
    results = [_median_result(w, roster_id) for w in weeks]
    return results.count(1), results.count(-1)


def _week_games(week: PastWeek, roster_id: int) -> list[tuple[int, int]]:
    """The results of one week's games with their weights, oldest first: the head-to-head game, then the median game.

    A result is 1 for a win, -1 for a loss, 0 for a tie. A bye week has the median game only.
    """
    games = []
    game = head_to_head(week, roster_id)
    if game is not None:
        games.append((game[1], FORM_HEAD_TO_HEAD_WEIGHT))
    games.append((_median_result(week, roster_id), FORM_MEDIAN_WEIGHT))
    return games


def _form_streak(games: list[tuple[int, int]]) -> int:
    """The weighted wins (positive) or losses (negative) in a row, newest game back, with the median game counted.

    The median game is the newer game of its week, since it settles after every head-to-head game.
    """
    run = 0
    for result, weight in reversed(games):
        if result == 0 or (run and result != (1 if run > 0 else -1)):
            break
        run += result * weight
    return run


def _form(recent: list[PastWeek], rosters: list[int]) -> dict[int, float]:
    """A third each over the recent weeks: the form streak, the weighted record of both games, the all-play rate."""
    out = {}
    for rid in rosters:
        games = [game for week in recent for game in _week_games(week, rid)]
        streak = _scaled(_form_streak(games), -STREAK_CAP, STREAK_CAP)
        wins = sum(weight for result, weight in games if result == 1)
        losses = sum(weight for result, weight in games if result == -1)
        out[rid] = (streak + _rate(wins, losses) + _all_play_rate(recent, rid)) / 3
    return out


def _schedule_played(weeks: list[PastWeek], standing: list[int]) -> dict[int, float]:
    """Half the mean head-to-head win rate of every past opponent, half the quality win rate."""
    top = set(standing[:QUALITY_TOP])
    rate = {rid: _rate(*_head_to_head_record(weeks, rid)) for rid in standing}
    out = {}
    for rid in standing:
        games = [g for g in (head_to_head(w, rid) for w in weeks) if g is not None]
        # The mean is per game, not per opponent: a team played twice is twice the schedule.
        opponents = sum(rate[o] for o, _ in games) / len(games) if games else NEUTRAL
        # The quality rate counts a tie as a game and not a win, per the spec: wins over games.
        quality = [result for o, result in games if o in top]
        quality_rate = quality.count(1) / len(quality) if quality else NEUTRAL
        out[rid] = opponents / 2 + quality_rate / 2
    return out


def _mean_margin(weeks: list[PastWeek], roster_id: int) -> float:
    """The mean head-to-head margin per game, points for minus points against. No game gives 0."""
    margins = []
    for week in weeks:
        game = head_to_head(week, roster_id)
        if game is not None:
            margins.append(week.scores[roster_id] - week.scores[game[0]])
    return sum(margins) / len(margins) if margins else 0.0


def _scoring(weeks: list[PastWeek], records: dict[int, tuple[int, int, float]]) -> dict[int, float]:
    """A third the points for, a third the season all-play win rate, a third the mean margin.

    Points for and margin are each scaled from the bottom team to the top.
    """
    points = {rid: record[2] for rid, record in records.items()}
    low, high = min(points.values()), max(points.values())
    margin = {rid: _mean_margin(weeks, rid) for rid in records}
    margin_low, margin_high = min(margin.values()), max(margin.values())
    out = {}
    for rid in records:
        out[rid] = (
            _scaled(points[rid], low, high)
            + _all_play_rate(weeks, rid)
            + _scaled(margin[rid], margin_low, margin_high)
        ) / 3
    return out
