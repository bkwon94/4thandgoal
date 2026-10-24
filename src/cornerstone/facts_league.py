"""
League-wide facts: standings, awards, Matchup of the Week, next week, position ranks, and position leaders.
Every number comes from code, and every derived number is exact to two decimals.
"""
import logging
from collections import defaultdict
from decimal import Decimal

from cornerstone.facts_matchup import median_facts
from cornerstone.models import (
    Award,
    History,
    MatchupFacts,
    NextMatchup,
    PastWeek,
    Pick,
    PlayerLine,
    PositionLeader,
    PositionRank,
    SeasonHistory,
    Standing,
    Week,
    r2,
    sub,
)
from cornerstone.tunables import PLAYOFF_SPOTS

logger = logging.getLogger(__name__)

TEAM_COUNT = 12
# The team trend is the mean of this many latest weeks.
TREND_WEEKS = 3
# A recent move adds this many points to the Game Changer score.
MOVE_BONUS = 5
UNDERPERFORMER_MIN_PROJECTION = 10
# Weights for the Matchup of the Week signals.
WEIGHTS = {"closeness": 0.4, "upset": 0.25, "table": 0.2, "stakes": 0.15}
REASONS = {
    "closeness": "Closest Finish",
    "upset": "Upset",
    "table": "Top of the Table",
    "stakes": "Playoff Stakes",
}


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


def standings(week: Week, history: History | None = None) -> list[Standing]:
    if history is not None and history.complete():
        records = season_records(history, week.week)
    else:
        if history is not None:
            logger.warning("history incomplete: standings from rosters.json")
        records = {
            t.roster_id: (t.wins, t.losses, t.points_for) for t in week.teams.values()
        }
    ordered = standings_order(records)
    cut_wins = records[ordered[PLAYOFF_SPOTS - 1]][0]
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
            in_playoffs=i + 1 <= PLAYOFF_SPOTS,
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


def ranks_before(
    week: Week, table: list[Standing], history: History | None = None
) -> dict[int, int]:
    """Rank of each roster before this week.

    A complete history ranks the records of the weeks before this one. Without it, this
    removes the week from the totals. Week 1 has no earlier record, so it also subtracts.
    """
    if history is not None and history.complete() and week.week > 1:
        records = season_records(history, week.week - 1)
        ordered = sorted(records, key=lambda rid: (-records[rid][0], -records[rid][2]))
        return {rid: i + 1 for i, rid in enumerate(ordered)}

    wins = {s.roster_id: s.wins for s in table}
    losses = {s.roster_id: s.losses for s in table}
    points = {s.roster_id: s.points_for for s in table}

    def take_off(roster_id: int, won: bool | None) -> None:
        if won is True:
            wins[roster_id] -= 1
        elif won is False:
            losses[roster_id] -= 1

    for m in week.matchups:
        # A tie against the opponent is neither a win nor a loss.
        for side, other in ((m.a, m.b), (m.b, m.a)):
            if side.points != other.points:
                take_off(side.roster_id, side.points > other.points)
            points[side.roster_id] = sub(points[side.roster_id], side.points)
    median = median_facts(week)
    for rid in median.above:
        take_off(rid, True)
    for rid in median.below:
        take_off(rid, False)

    ordered = sorted(wins, key=lambda rid: (-wins[rid], -points[rid]))
    return {rid: i + 1 for i, rid in enumerate(ordered)}


def upset_signal(winner_rank_before: int, loser_rank_before: int) -> float:
    """An upset is a winner ranked below the loser before the week."""
    return max(0, (winner_rank_before - loser_rank_before) / (TEAM_COUNT - 1))


def _table_signal(rank_a: int, rank_b: int) -> float:
    return 1 - (rank_a + rank_b - 3) / (2 * (TEAM_COUNT - 1))


def _stakes_signal(a: Standing, b: Standing) -> float:
    return 1.0 if min(abs(a.games_from_cut), abs(b.games_from_cut)) <= 1 else 0.0


def matchup_of_the_week(
    week: Week,
    mfacts: list[MatchupFacts],
    table: list[Standing],
    before: dict[int, int] | None = None,
) -> Pick:
    by_roster = {s.roster_id: s for s in table}
    if before is None:
        before = ranks_before(week, table)
    max_margin = max(f.margin for f in mfacts)
    best: tuple[float, float, Pick] | None = None
    for f, m in zip(mfacts, week.matchups):
        a, b = by_roster[m.a.roster_id], by_roster[m.b.roster_id]
        raw = {
            "closeness": 1 - f.margin / max_margin if max_margin else 1.0,
            "upset": (
                upset_signal(before[f.winner], before[f.loser])
                if f.winner is not None
                else 0.0
            ),
            "table": _table_signal(a.rank, b.rank),
            "stakes": _stakes_signal(a, b),
        }
        scores = {k: r2(WEIGHTS[k] * v) for k, v in raw.items()}
        top = max(scores, key=lambda k: scores[k])
        pick = Pick(matchup_id=f.matchup_id, reason=REASONS[top], scores=scores)
        total = sum(WEIGHTS[k] * v for k, v in raw.items())
        # Highest total wins. A tie in total goes to the smallest margin.
        if best is None or (total, -f.margin) > (best[0], -best[1]):
            best = (total, f.margin, pick)
    return best[2]


def next_week(week: Week, table: list[Standing]) -> list[NextMatchup]:
    by_roster = {s.roster_id: s for s in table}
    scored = []
    for a_id, b_id in week.next_matchups:
        a, b = by_roster[a_id], by_roster[b_id]
        stakes = _stakes_signal(a, b)
        score = (
            WEIGHTS["table"] * _table_signal(a.rank, b.rank)
            + WEIGHTS["stakes"] * stakes
        )
        scored.append((score, a, b, stakes))
    # sorted() is stable, so a tie keeps the order of the schedule.
    top_two = {
        id(item) for item in sorted(scored, key=lambda x: -x[0])[:2]
    }
    out = []
    for item in scored:
        score, a, b, stakes = item
        must_watch = id(item) in top_two
        reason = None
        if must_watch:
            hi, lo = sorted((a.rank, b.rank))
            reason = f"{_ordinal(hi)} vs {_ordinal(lo)}"
            if stakes:
                reason += ", near the playoff cut"
        out.append(
            NextMatchup(a=a.roster_id, b=b.roster_id, must_watch=must_watch, reason=reason)
        )
    return out


def _ordinal(n: int) -> str:
    if n % 100 in (11, 12, 13):
        return f"{n}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _located_lines(week: Week) -> list[tuple[PlayerLine, int, int]]:
    """Every line with its roster id and matchup id."""
    return [
        (line, side.roster_id, m.matchup_id)
        for m in week.matchups
        for side in (m.a, m.b)
        for line in side.lines
    ]


def awards(week: Week, mfacts: list[MatchupFacts]) -> list[Award]:
    located = _located_lines(week)
    started = [x for x in located if x[0].started]
    projections_up = any(x[0].projection is not None for x in started)

    # Each ranking lists (located line, reason) from best to worst.
    rankings: list[tuple[str, list[tuple[tuple[PlayerLine, int, int], str]]]] = []

    swing = [
        ((line, f.winner, f.matchup_id), f)
        for f in mfacts
        for line in f.swing
    ]
    if projections_up:
        def game_changer_score(item) -> float:
            (line, rid, _), f = item
            moved = any(
                mv.player_id == line.player_id and mv.roster_id == rid
                for mv in f.recent_moves
            )
            return sub(line.points, line.projection) + (MOVE_BONUS if moved else 0)

        gc = sorted(
            (i for i in swing if i[0][0].projection is not None),
            key=game_changer_score,
            reverse=True,
        )
    else:
        gc = sorted(swing, key=lambda i: i[0][0].points, reverse=True)
    rankings.append(
        ("game_changer", [(loc, _game_changer_reason(loc, f, projections_up)) for loc, f in gc])
    )

    rankings.append((
        "top_scorer",
        [
            (x, f"{x[0].name} scored {x[0].points}, the most of any starter this week.")
            for x in sorted(started, key=lambda x: x[0].points, reverse=True)
        ],
    ))
    rankings.append((
        "mvb",
        [
            (x, f"{x[0].name} scored {x[0].points} on the bench, the most of any bench player this week.")
            for x in sorted(
                (x for x in located if not x[0].started),
                key=lambda x: x[0].points,
                reverse=True,
            )
        ],
    ))
    if projections_up:
        with_projection = [x for x in started if x[0].projection is not None]
        rankings.append((
            "underperformer",
            [
                (x, f"{x[0].name} scored {x[0].points} on a {x[0].projection} projection, {sub(x[0].projection, x[0].points)} under.")
                for x in sorted(
                    (x for x in with_projection if x[0].projection >= UNDERPERFORMER_MIN_PROJECTION),
                    key=lambda x: sub(x[0].projection, x[0].points),
                    reverse=True,
                )
            ],
        ))
        rankings.append((
            "overachiever",
            [
                (x, f"{x[0].name} scored {x[0].points} on a {x[0].projection} projection, {sub(x[0].points, x[0].projection)} over.")
                for x in sorted(
                    with_projection,
                    key=lambda x: sub(x[0].points, x[0].projection),
                    reverse=True,
                )
            ],
        ))

    picked: set[str] = set()
    out = []
    for key, ranked in rankings:
        skipped: list[str] = []
        for (line, rid, mid), reason in ranked:
            if line.player_id in picked:
                skipped.append(line.name)
                continue
            picked.add(line.player_id)
            out.append(
                Award(key=key, line=line, roster_id=rid, matchup_id=mid, reason=reason, skipped=skipped)
            )
            break
    return out


def _game_changer_reason(loc, f: MatchupFacts, projections_up: bool) -> str:
    line, rid, _ = loc
    win = f"in a {r2(f.margin)}-point win"
    if not projections_up:
        return f"{line.name} scored {line.points} {win}."
    moved = any(
        mv.player_id == line.player_id and mv.roster_id == rid for mv in f.recent_moves
    )
    tail = " after a recent roster move" if moved else ""
    return (
        f"{line.name} scored {line.points} on a {line.projection} projection, "
        f"{sub(line.points, line.projection)} over, {win}{tail}."
    )


def _started_by_position(week: Week) -> dict[str, list[tuple[PlayerLine, int]]]:
    """Started lines with their roster ids, grouped by position, best first.

    The name breaks a tie, so the order is stable from one build to the next.
    The ranks and the leaders both read this one order, so they never disagree.
    """
    groups: dict[str, list[tuple[PlayerLine, int]]] = defaultdict(list)
    for line, roster_id, _ in _located_lines(week):
        if line.started:
            groups[line.position].append((line, roster_id))
    for entries in groups.values():
        entries.sort(key=lambda x: (-x[0].points, x[0].name))
    return groups


def position_ranks(week: Week) -> list[PositionRank]:
    out = []
    for position, ordered in _started_by_position(week).items():
        out.extend(
            PositionRank(player_id=line.player_id, position=position, rank=i + 1, of=len(ordered))
            for i, (line, _) in enumerate(ordered)
        )
    return out


LEADER_POSITIONS = ("QB", "RB", "WR", "TE", "DEF")


def position_leaders(week: Week) -> list[PositionLeader]:
    """The top three started lines at each position, in lineup order."""
    groups = _started_by_position(week)
    out = []
    for position in LEADER_POSITIONS:
        ordered = groups[position]
        out.extend(
            PositionLeader(line=line, position=position, rank=i + 1, of=len(ordered), roster_id=rid)
            for i, (line, rid) in enumerate(ordered[:3])
        )
    return out


def season_history(week: Week, history: History | None = None) -> list[SeasonHistory]:
    """The season so far of each roster. With no complete history it covers this week only."""
    if history is not None and history.complete():
        return _full_season_history(history, week.week)
    scores = {s.roster_id: s.points for m in week.matchups for s in (m.a, m.b)}
    return [
        SeasonHistory(
            roster_id=rid,
            high=pts,
            low=pts,
            weeks_over={t: int(pts > t) for t in (100, 110, 120)},
            new_high=True,
            new_low=True,
        )
        for rid, pts in sorted(scores.items())
    ]


def _full_season_history(history: History, through: int) -> list[SeasonHistory]:
    """Highs, lows, average, trend, and streak over weeks 1 to `through`."""
    out = []
    for rid in sorted(history.weeks[through].scores):
        # A roster with no score in a week, such as a bye, adds no entry for that week.
        weekly = [
            (number, Decimal(str(history.weeks[number].scores[rid])))
            for number in range(1, through + 1)
            if rid in history.weeks[number].scores
        ]
        points = [p for _, p in weekly]
        earlier, now = points[:-1], points[-1]
        recent = points[-TREND_WEEKS:]
        out.append(
            SeasonHistory(
                roster_id=rid,
                high=float(max(points)),
                low=float(min(points)),
                weeks_over={t: sum(p > t for p in points) for t in (100, 110, 120)},
                new_high=all(now > p for p in earlier),
                new_low=all(now < p for p in earlier),
                average=r2(float(sum(points) / len(points))),
                trend=r2(float(sum(recent) / len(recent))),
                streak=_streak(history, rid, through),
            )
        )
    return out


def _streak(history: History, roster_id: int, through: int) -> int:
    """Wins (positive) or losses (negative) in a row, newest week back. Head-to-head only."""
    run = 0
    for number in range(through, 0, -1):
        game = head_to_head(history.weeks[number], roster_id)
        if game is None:
            continue
        _, result = game
        if result == 0 or (run and result != (1 if run > 0 else -1)):
            break
        run += result
    return run


def week_median(week: PastWeek) -> Decimal:
    """The exact median score of one week, the line of the median game."""
    ordered = sorted((Decimal(str(p)) for p in week.scores.values()), reverse=True)
    # The same median as median_facts: the mean of the 6th and 7th scores.
    return (ordered[5] + ordered[6]) / 2


def head_to_head(week: PastWeek, roster_id: int) -> tuple[int, int] | None:
    """The opponent and the result of one head-to-head game: 1 a win, -1 a loss, 0 a tie.

    None when the roster has no pair that week, such as a bye. The median game is not in it.
    """
    opponent = next(
        (b if a == roster_id else a for a, b in week.pairs if roster_id in (a, b)), None
    )
    if opponent is None:
        return None
    mine, theirs = week.scores[roster_id], week.scores[opponent]
    return opponent, (mine > theirs) - (mine < theirs)
