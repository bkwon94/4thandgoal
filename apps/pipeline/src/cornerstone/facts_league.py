"""
League-wide models: awards, ranks before the week, Matchup of the Week, next week, position ranks, and position leaders.
Every number comes from code, and every derived number is exact to two decimals.
The models are not facts. The sheet reads them through Context, so this module is not a fact group.
"""
import logging
from collections import Counter, defaultdict
from collections.abc import Callable
from decimal import Decimal

from cornerstone.facts_matchup import median_facts
from cornerstone.tunables import (
    AWARDS_PER_PLAYER,
    KEY_STARTER_SHORT_STARTS,
    KEY_STARTER_STARTS,
    KEY_STARTER_WEEKS,
    SHOOTOUT_TOP,
    STORYLINE_WEIGHTS,
)
from league.client import Client
from league.models import (
    Award,
    ByePlayer,
    History,
    MatchupFacts,
    NextMatchup,
    Pick,
    PlayerLine,
    PositionLeader,
    PositionRank,
    SeasonHistory,
    Standing,
    Storyline,
    Week,
    sub,
)
from league.numbers import one_decimal, ordinal, r2
from league.standings_table import head_to_head, season_records
from league.tunables import TREND_WEEKS

logger = logging.getLogger(__name__)

# A recent move adds this many points to the Game Changer score.
MOVE_BONUS = 5
UNDERPERFORMER_MIN_PROJECTION = 10
# Weights for the Matchup of the Week signals.
WEIGHTS = {"closeness": 0.4, "upset": 0.25, "table": 0.2, "stakes": 0.15}
# A team on this many head-to-head wins or losses in a row puts a streak on the line. GLOSSARY.md, "Streak on the line".
STREAK_ON_THE_LINE = 3
# Both teams ranked this high or higher in the standings meet at the top of the table.
TABLE_TOP = 4
REASONS = {
    "closeness": "Closest Finish",
    "upset": "Upset",
    "table": "Top of the Table",
    "stakes": "Playoff Stakes",
}


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


def upset_signal(winner_rank_before: int, loser_rank_before: int, *, client: Client) -> float:
    """An upset is a winner ranked below the loser before the week."""
    return max(0, (winner_rank_before - loser_rank_before) / (client.settings.team_count - 1))


def _table_signal(rank_a: int, rank_b: int, *, client: Client) -> float:
    return 1 - (rank_a + rank_b - 3) / (2 * (client.settings.team_count - 1))


def _stakes_signal(a: Standing, b: Standing) -> float:
    return 1.0 if min(abs(a.games_from_cut), abs(b.games_from_cut)) <= 1 else 0.0


def matchup_of_the_week(
    week: Week,
    mfacts: list[MatchupFacts],
    table: list[Standing],
    before: dict[int, int] | None = None,
    *,
    client: Client,
) -> Pick:
    """Pick the matchup with the highest weighted total of the four signals.

    The label names the signal in which the pick ranks first among all matchups, by raw
    value. A lone first is a lead. A tie for first is a lead only when fewer than half of
    the matchups share the top value. A 0-or-1 signal that most games share says nothing
    about this pick. With more than one lead, the larger weighted score wins. With no lead,
    the signal in which the pick comes nearest to the best value names it, as a ratio of
    the pick value to the best value. A tie in the ratio goes to the larger weighted score.
    A signal that is no lead because most games share its top value stays out of this too.
    The weights do not name the pick alone, because the winner alone misleads: closeness
    carries 40 percent, so it is the largest part of almost every winner, even when
    another game was closer.
    """
    by_roster = {s.roster_id: s for s in table}
    if before is None:
        before = ranks_before(week, table)
    max_margin = max(f.margin for f in mfacts)
    signals = []
    for f, m in zip(mfacts, week.matchups):
        a, b = by_roster[m.a.roster_id], by_roster[m.b.roster_id]
        signals.append({
            "closeness": 1 - f.margin / max_margin if max_margin else 1.0,
            "upset": (
                upset_signal(before[f.winner], before[f.loser], client=client)
                if f.winner is not None
                else 0.0
            ),
            "table": _table_signal(a.rank, b.rank, client=client),
            "stakes": _stakes_signal(a, b),
        })
    best_raw = {k: max(raw[k] for raw in signals) for k in WEIGHTS}
    shared = {k: sum(raw[k] == best_raw[k] for raw in signals) for k in WEIGHTS}
    best: tuple[float, float, Pick] | None = None
    for f, raw in zip(mfacts, signals):
        scores = {k: r2(WEIGHTS[k] * v) for k, v in raw.items()}
        leads = [k for k in raw if raw[k] == best_raw[k] and 2 * shared[k] < len(signals)]
        if leads:
            top = max(leads, key=lambda k: scores[k])
        else:
            # Only signals that can lead for a pick may name it.
            open_signals = [k for k in raw if 2 * shared[k] < len(signals)] or list(raw)
            top = max(
                open_signals,
                key=lambda k: (raw[k] / best_raw[k] if best_raw[k] else 0.0, scores[k]),
            )
        pick = Pick(matchup_id=f.matchup_id, reason=REASONS[top], scores=scores)
        total = sum(WEIGHTS[k] * v for k, v in raw.items())
        # Highest total wins. A tie in total goes to the smallest margin.
        if best is None or (total, -f.margin) > (best[0], -best[1]):
            best = (total, f.margin, pick)
    return best[2]


# A kicker or a defense is never a key starter. GLOSSARY.md, "Key starter".
KEY_STARTER_POSITIONS = ("QB", "RB", "WR", "TE")


def _starts(pid: str, weeks: list[list[str]]) -> int:
    """The starts of the player in the latest completed weeks the key starter rule reads.

    `weeks` holds the starters of each completed week, oldest first.
    """
    return sum(pid in starters for starters in weeks[-KEY_STARTER_WEEKS:])


def key_starters(weeks: list[list[str]], roster: dict[str, str]) -> set[str]:
    """The key starters of a roster: the players it started in enough of its latest completed weeks.

    `weeks` holds the starters of each completed week, oldest first. `roster` maps each player on the roster
    at build time to his position. A start is any place in the starters list, the flex slot too.
    """
    recent = weeks[-KEY_STARTER_WEEKS:]
    if len(recent) < KEY_STARTER_SHORT_STARTS:
        return set()
    bar = KEY_STARTER_STARTS if len(recent) >= KEY_STARTER_WEEKS else KEY_STARTER_SHORT_STARTS
    return {
        pid for pid, position in roster.items()
        if position in KEY_STARTER_POSITIONS and _starts(pid, weeks) >= bar
    }


def _byes(
    week: Week, history: History | None, bye_weeks: dict[str, int] | None,
    rank: Callable[[str], int | None] | None = None,
) -> dict[int, list[ByePlayer]]:
    """The players of each roster whose NFL team has its bye next week, key starters first.

    `rank` gives the position rank of a player. Without it, no player has a rank.
    Thin data gives no lists and one log line, so the page shows no bye line it cannot back.
    """
    if not bye_weeks:
        logger.warning("no NFL schedule: the next-week games have no bye lists")
        return {}
    completed = sorted(w for w in (history.weeks if history is not None else {}) if w <= week.week)
    if len(completed) < KEY_STARTER_SHORT_STARTS:
        logger.warning("history has %d completed weeks: the next-week games have no bye lists", len(completed))
        return {}
    out = {}
    for roster_id, roster in week.rosters.items():
        weeks = [history.weeks[w].starters.get(roster_id, []) for w in completed]
        keys = key_starters(weeks, roster)
        # The roster players give the name and the NFL team, so a player with no lineup line, such as a player
        # added after the games, is on the list too. A player with no NFL team the build knows has no bye.
        on_bye = [
            ByePlayer(player_id=pid, name=week.roster_players[pid][0], position=position, key=pid in keys,
                      rank=rank(pid) if rank is not None else None,
                      starts=_starts(pid, weeks), weeks=min(len(weeks), KEY_STARTER_WEEKS))
            for pid, position in roster.items()
            if pid in week.roster_players and bye_weeks.get(week.roster_players[pid][1]) == week.week + 1
        ]
        # Key starters come first, then the rest by position rank, then by name. A player with no rank comes last.
        out[roster_id] = sorted(on_bye, key=lambda p: (not p.key, p.rank is None, p.rank or 0, p.name))
    return out


def next_week(
    week: Week, table: list[Standing], history: History | None = None,
    projected: dict[int, dict[int, float]] | None = None, bye_weeks: dict[str, int] | None = None,
    rank: Callable[[str], int | None] | None = None,
    *,
    client: Client,
) -> list[NextMatchup]:
    """The next-week games in schedule order, each with its storylines. The top two by storyline score are Must Watch.

    `projected` is the best projected lineup of each roster by week, as `projected_totals` gives it.
    `bye_weeks` is the bye week of each NFL team. Each side of a game lists its players on bye next week.
    `rank` gives the position rank of a player, so the players on bye who are not key starters sort by it.
    A tie in the score goes to the smaller gap in the standings, then to the schedule order.
    """
    byes = _byes(week, history, bye_weeks, rank)
    by_roster = {s.roster_id: s for s in table}
    ahead = {rid: by_week[week.week + 1] for rid, by_week in (projected or {}).items() if week.week + 1 in by_week}
    # A tie in the total goes to the lower roster id, so the top four is the same on every build.
    top = set(sorted(ahead, key=lambda rid: (-ahead[rid], rid))[:SHOOTOUT_TOP])
    games = []
    for a_id, b_id in week.next_matchups:
        a, b = by_roster[a_id], by_roster[b_id]
        stories = _storylines(week, a, b, history)
        if a_id in top and b_id in top:
            stories.append(_story("shootout", totals=(one_decimal(ahead[a_id]), one_decimal(ahead[b_id]))))
        games.append((a, b, _sorted_storylines(stories)))
    # sorted() is stable, so a tie in score and gap keeps the order of the schedule.
    ranked = sorted(
        range(len(games)),
        key=lambda i: (-sum(s.weight for s in games[i][2]), abs(games[i][0].rank - games[i][1].rank)),
    )
    top_two = set(ranked[:2])
    out = []
    for i, (a, b, stories) in enumerate(games):
        must_watch = i in top_two
        out.append(NextMatchup(
            a=a.roster_id, b=b.roster_id, must_watch=must_watch,
            reason=_reason(week, a, b, stories) if must_watch else None, storylines=stories,
            a_byes=byes.get(a.roster_id, []), b_byes=byes.get(b.roster_id, []),
        ))
    return out


def _storylines(week: Week, a: Standing, b: Standing, history: History | None) -> list[Storyline]:
    """The storylines of one next-week game that read the history and the standings."""
    out = []
    if history is not None and history.complete():
        for side in (a, b):
            # The streak reads head-to-head games only, so the median game never counts.
            run = streak(history, side.roster_id, week.week)
            if abs(run) >= STREAK_ON_THE_LINE:
                out.append(_story("streak", roster_id=side.roster_id, length=run))
        met = _first_meeting(history, a.roster_id, b.roster_id, week.week)
        if met is not None:
            number, winner, loser, margin = met
            out.append(_story("rematch", roster_id=winner, week=number, margin=margin))
            # A tie has no loser, so it gives no revenge.
            if loser is not None:
                out.append(_story("revenge", roster_id=loser, week=number, margin=margin))
    near = [s.roster_id for s in (a, b) if abs(s.games_from_cut) <= 1]
    if near:
        out.append(_story("cut", teams=near))
    if a.rank <= TABLE_TOP and b.rank <= TABLE_TOP:
        out.append(_story("table"))
    return out


def _first_meeting(
    history: History, a: int, b: int, through: int
) -> tuple[int, int | None, int | None, float] | None:
    """The week, the winner, the loser, and the margin of the earliest head-to-head game of a and b this season.

    A tie has no winner and no loser. None when the two have not met.
    """
    for number in range(1, through + 1):
        game = head_to_head(history.weeks[number], a)
        if game is None or game[0] != b:
            continue
        scores = history.weeks[number].scores
        margin = abs(sub(scores[a], scores[b]))
        if game[1] == 0:
            return number, None, None, margin
        winner, loser = (a, b) if game[1] > 0 else (b, a)
        return number, winner, loser, margin
    return None


def _sorted_storylines(stories: list[Storyline]) -> list[Storyline]:
    """Highest weight first. A tie in weight keeps the tunable order."""
    order = list(STORYLINE_WEIGHTS)
    return sorted(stories, key=lambda s: (-s.weight, order.index(s.kind)))


def _story(kind: str, **fields) -> Storyline:
    return Storyline(kind=kind, weight=STORYLINE_WEIGHTS[kind], **fields)


def _reason(week: Week, a: Standing, b: Standing, stories: list[Storyline]) -> str:
    """One sentence on the top two storylines, with the numbers. A game with no storyline names the two ranks."""
    if not stories:
        hi, lo = sorted((a.rank, b.rank))
        return f"{ordinal(hi)} vs {ordinal(lo)}"
    clauses = [_clause(week, a, b, s) for s in stories[:2]]
    if len(clauses) == 1:
        text = " ".join(x for x in clauses[0] if x)
    elif clauses[0][0] is not None and clauses[0][0] == clauses[1][0]:
        # One team leads both clauses, so the second clause drops its name.
        text = f"{clauses[0][0]} {clauses[0][1]} and {clauses[1][1]}"
    else:
        second = clauses[1]
        if stories[0].kind == stories[1].kind == "streak":
            # The second streak drops the verb, so two long team names still fit in 25 words.
            second = (second[0], second[1].removeprefix("puts ").removesuffix(" on the line"))
        text = f"{' '.join(x for x in clauses[0] if x)}, and {' '.join(x for x in second if x)}"
    # A reason that starts with a team name keeps the case of the name.
    if not any(text.startswith(t.name) for t in week.teams.values()):
        text = text[0].upper() + text[1:]
    return text


def _clause(week: Week, a: Standing, b: Standing, s: Storyline) -> tuple[str | None, str]:
    """The subject and the predicate of one storyline in the reason. The subject is a team name or None."""
    name = {rid: t.name for rid, t in week.teams.items()}
    if s.kind == "streak":
        kind = "win" if s.length > 0 else "loss"
        return name[s.roster_id], f"puts a {abs(s.length)}-game {kind} streak on the line"
    if s.kind == "cut":
        if len(s.teams) == 2:
            return None, "both sit near the cut"
        return name[s.teams[0]], "sits near the cut"
    if s.kind == "rematch":
        if s.roster_id is None:
            return None, f"a week {s.week} rematch that ended in a tie"
        return None, f"a week {s.week} rematch {name[s.roster_id]} won by {s.margin:g}"
    if s.kind == "revenge":
        return name[s.roster_id], "seeks revenge"
    if s.kind == "shootout":
        x, y = s.totals
        return None, f"lineups project {x:.1f} and {y:.1f} in a projected shootout"
    hi, lo = sorted((a.rank, b.rank))
    return None, f"{ordinal(hi)} and {ordinal(lo)} meet at the top of the table"


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
                (
                    x,
                    (f"{x[0].name} scored {x[0].points} on a {x[0].projection} projection, "
                     f"{sub(x[0].projection, x[0].points)} under."),
                )
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
                (
                    x,
                    (f"{x[0].name} scored {x[0].points} on a {x[0].projection} projection, "
                     f"{sub(x[0].points, x[0].projection)} over."),
                )
                for x in sorted(
                    with_projection,
                    key=lambda x: sub(x[0].points, x[0].projection),
                    reverse=True,
                )
            ],
        ))

    # Each award picks its own winner, so one player can win two awards. A reader expects the top scorer to be
    # the top scorer, so the Top Scorer tile must stay true.
    # The cap is AWARDS_PER_PLAYER. The awards pick in list order, and a later award skips a player who holds the
    # cap and takes the next name. Top Scorer picks second, so the cap never moves it, and its tile stays true.
    awards_held: Counter[str] = Counter()
    out = []
    for key, ranked in rankings:
        pick = next((x for x in ranked if awards_held[x[0][0].player_id] < AWARDS_PER_PLAYER), None)
        if pick:
            (line, rid, mid), reason = pick
            awards_held[line.player_id] += 1
            out.append(Award(key=key, line=line, roster_id=rid, matchup_id=mid, reason=reason))
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
                streak=streak(history, rid, through),
            )
        )
    return out


def streak(history: History, roster_id: int, through: int) -> int:
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
