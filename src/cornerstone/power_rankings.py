"""
Power rankings: a rank per team per week from four components, standing, form, schedule played, and scoring.
Pure code over the saved history. No trade value and no chart enter the formula.
"""
from cornerstone.facts_league import TREND_WEEKS, head_to_head, season_records, standings_order
from cornerstone.models import History, PastWeek, PowerRow
from cornerstone.tunables import POWER_WEIGHTS

# A quality win is a win against a team in this many top places of the standings.
QUALITY_TOP = 4
# The neutral half of a rate with no game behind it,
# so the formula does not punish a team for a schedule it did not choose.
NEUTRAL = 0.5


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
    values = {
        "standing": {rid: _scaled(len(standing) - standing_rank[rid], 0, len(standing) - 1) for rid in standing},
        "form": _form(weeks[-TREND_WEEKS:], standing),
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


def _form(recent: list[PastWeek], rosters: list[int]) -> dict[int, float]:
    """Half the head-to-head win rate, half the all-play win rate, over the recent weeks."""
    out = {}
    for rid in rosters:
        out[rid] = _rate(*_head_to_head_record(recent, rid)) / 2 + _all_play_rate(recent, rid) / 2
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


def _scoring(weeks: list[PastWeek], records: dict[int, tuple[int, int, float]]) -> dict[int, float]:
    """Half the points for scaled from the bottom team to the top, half the season all-play win rate."""
    points = {rid: record[2] for rid, record in records.items()}
    low, high = min(points.values()), max(points.values())
    out = {}
    for rid in records:
        out[rid] = _scaled(points[rid], low, high) / 2 + _all_play_rate(weeks, rid) / 2
    return out
