"""
Facts for one matchup and for the league median game.
Every number comes from code, and every derived number is exact to two decimals.
"""
from decimal import Decimal

from cornerstone.models import (
    Matchup,
    MatchupFacts,
    MedianFacts,
    Move,
    PlayerLine,
    Side,
    Week,
    r2,
    sub,
)


def matchup_facts(m: Matchup, moves: list[Move], week: int) -> MatchupFacts:
    if m.a.points == m.b.points:
        winner_side = loser_side = None
        margin = 0.0
    else:
        winner_side, loser_side = (m.a, m.b) if m.a.points > m.b.points else (m.b, m.a)
        margin = sub(winner_side.points, loser_side.points)

    sides = (m.a, m.b)
    all_lines = [line for side in sides for line in side.lines]
    gap = lambda line: abs(sub(line.points, line.projection))  # noqa: E731

    # A line with no projection has no gap, so it can never drive the result.
    drivers = sorted(
        (l for l in all_lines if l.projection is not None and gap(l) >= margin),
        key=gap,
        reverse=True,
    )
    swing = (
        sorted(
            (l for l in winner_side.lines if l.started and l.points > margin),
            key=lambda l: l.points,
            reverse=True,
        )
        if winner_side
        else []
    )
    return MatchupFacts(
        matchup_id=m.matchup_id,
        winner=winner_side.roster_id if winner_side else None,
        loser=loser_side.roster_id if loser_side else None,
        score_w=(winner_side or m.a).points,
        score_l=(loser_side or m.b).points,
        margin=margin,
        # max() returns the first maximum, so a tie goes to the first in roster order.
        top_scorer={
            s.roster_id: max((l for l in s.lines if l.started), key=lambda l: l.points)
            for s in sides
        },
        drivers=drivers,
        swing=swing,
        bench_regret=_bench_regret(m),
        recent_moves=_recent_moves(sides, moves, week),
    )


def _bench_regret(m: Matchup) -> list[tuple[PlayerLine, PlayerLine]]:
    """Pair each bench line with the weakest started line at its position when the swap flips the winner."""
    diff = Decimal(str(m.a.points)) - Decimal(str(m.b.points))
    if diff == 0:
        # No winner exists, so no swap can flip one.
        return []
    pairs = []
    for side, sign in ((m.a, 1), (m.b, -1)):
        for bench in (l for l in side.lines if not l.started):
            same_position = [
                l for l in side.lines if l.started and l.position == bench.position
            ]
            if not same_position:
                continue
            starter = min(same_position, key=lambda l: l.points)
            swing = Decimal(str(bench.points)) - Decimal(str(starter.points))
            new_diff = diff + sign * swing
            # The result flips only when the other side now wins outright.
            if (diff > 0 and new_diff < 0) or (diff < 0 and new_diff > 0):
                pairs.append((bench, starter))
    return pairs


def _recent_moves(sides: tuple[Side, Side], moves: list[Move], week: int) -> list[Move]:
    started = {(s.roster_id, l.player_id) for s in sides for l in s.lines if l.started}
    return [
        mv
        for mv in moves
        if (mv.roster_id, mv.player_id) in started and mv.week in (week, week - 1)
    ]


def median_facts(week: Week) -> MedianFacts:
    """Median is the mean of the 6th and 7th scores, sorted high to low."""
    scored = [(s.roster_id, s.points) for m in week.matchups for s in (m.a, m.b)]
    ordered = sorted((p for _, p in scored), reverse=True)
    exact = (Decimal(str(ordered[5])) + Decimal(str(ordered[6]))) / 2

    # Gaps use the exact median, not the rounded one. A rounded median shifts a gap by a cent.
    def gap(points: float) -> float:
        return r2(float(Decimal(str(points)) - exact))

    # A score equal to the median is in neither list.
    above = [(r, gap(p)) for r, p in scored if Decimal(str(p)) > exact]
    below = [(r, -gap(p)) for r, p in scored if Decimal(str(p)) < exact]
    return MedianFacts(
        median=r2(float(exact)),
        above=[r for r, _ in above],
        below=[r for r, _ in below],
        closest_above=min(above, key=lambda x: x[1]),
        closest_below=min(below, key=lambda x: x[1]),
    )
