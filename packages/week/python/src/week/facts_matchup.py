"""
Facts for one matchup and for the league median game.
Every number comes from code, and every derived number is exact to two decimals.
"""
from decimal import Decimal

from league.models import (
    Matchup,
    MatchupFacts,
    MedianFacts,
    Move,
    PlayerLine,
    Side,
    Week,
    sub,
)
from league.numbers import r2


def matchup_facts(m: Matchup, moves: list[Move], week: int) -> MatchupFacts:
    if m.a.points == m.b.points:
        winner_side = loser_side = None
        margin = 0.0
    else:
        winner_side, loser_side = (m.a, m.b) if m.a.points > m.b.points else (m.b, m.a)
        margin = sub(winner_side.points, loser_side.points)

    sides = (m.a, m.b)
    all_lines = [line for side in sides for line in side.lines]
    gap = lambda line: abs(sub(line.points, line.projection))

    # A line with no projection has no gap, so it can never drive the result.
    # A bench line decides nothing, and a tie has no result to drive.
    drivers = (
        sorted(
            (
                line
                for line in all_lines
                if line.started and line.projection is not None and gap(line) >= margin
            ),
            key=gap,
            reverse=True,
        )
        if winner_side
        else []
    )
    swing = (
        sorted(
            (line for line in winner_side.lines if line.started and line.points > margin),
            key=lambda line: line.points,
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
            s.roster_id: max((line for line in s.lines if line.started), key=lambda line: line.points)
            for s in sides
        },
        drivers=drivers,
        swing=swing,
        bench_regret=_bench_regret(winner_side, loser_side),
        recent_moves=_recent_moves(sides, moves, week),
    )


def _bench_regret(
    winner: Side | None, loser: Side | None
) -> list[tuple[PlayerLine, PlayerLine]]:
    """Pair each losing-side bench line with the weakest started line at its position when the swap flips the result."""
    if winner is None or loser is None:
        # A tie has no result to flip. A winner cannot regret a win.
        return []
    lead = Decimal(str(winner.points)) - Decimal(str(loser.points))
    pairs = []
    for bench in (line for line in loser.lines if not line.started):
        same_position = [
            line for line in loser.lines if line.started and line.position == bench.position
        ]
        if not same_position:
            continue
        starter = min(same_position, key=lambda line: line.points)
        gain = Decimal(str(bench.points)) - Decimal(str(starter.points))
        # A gain equal to the lead gives a tie, not a flip.
        if gain > lead:
            pairs.append((bench, starter))
    return pairs


def _recent_moves(sides: tuple[Side, Side], moves: list[Move], week: int) -> list[Move]:
    started = {(s.roster_id, line.player_id) for s in sides for line in s.lines if line.started}
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
