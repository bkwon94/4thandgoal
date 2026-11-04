"""
Builds the facts about next week: the pick, the next matchups, the byes, and the storylines.
The next week chapter reads them.
"""
from collections.abc import Callable

from facts.chapters import BYE_FACT_PREFIX
from facts.tokens import Nums, fact
from league.client import Client
from league.lineup import bye_covers_for_roster
from league.models import (
    ByePlayer,
    Fact,
    NextMatchup,
    Standing,
    Storyline,
)
from league.numbers import count_noun, one_decimal_text
from league.snapshot import Snapshot
from week.facts_nflverse import shootouts
from week.sheet.base import Context


def facts(context: Context, client: Client) -> list[Fact]:
    """The pick, the next matchups, the storylines, the byes, and the shootouts.

    The Matchup of the Week chapter reads the pick. The next week chapter reads the rest.
    """
    return pick_facts(context) + next_facts(context) + shootout_facts(context)


def pick_facts(c: Context) -> list[Fact]:
    m = next(m for m in c.week.matchups if m.matchup_id == c.pick.matchup_id)
    a, b = c.team(m.a.roster_id), c.team(m.b.roster_id)
    text = f"Matchup of the Week is {a} vs {b}, chosen for {c.pick.reason}."
    return [fact("PICK", text, Nums(), [a, b], [])]


def next_facts(c: Context) -> list[Fact]:
    out = []
    for nx in c.next:
        n = Nums()
        sa, sb = c.by_rank[nx.a], c.by_rank[nx.b]
        text = (
            f"Next week {c.team(nx.a)} ({n.record(sa.wins, sa.losses)}, {n.ord(sa.rank)}) "
            f"plays {c.team(nx.b)} ({n.record(sb.wins, sb.losses)}, {n.ord(sb.rank)})."
        )
        if nx.must_watch:
            text += f" Must Watch: {n.text(nx.reason)}."
        out.append(fact(f"NX.{nx.a}v{nx.b}", text, n, [c.team(nx.a), c.team(nx.b)], []))
    return out + storyline_facts(c.next, c.by_rank, c.team) + bye_facts(c)


def _ranked(position: str, rank: int | None, n: Nums) -> str:
    """The position with its rank, such as QB4, or the position alone for a player with no rank."""
    return position if rank is None else f"{position}{n(rank)}"


def bye_facts(c: Context) -> list[Fact]:
    """One fact per player on bye next week, id `NX.bye.<roster>.<pid>`, and one per team with nobody on bye.

    GLOSSARY.md, "Bye line". The starts read the same weeks as the key starter rule, so a benched star shows too.
    Each key starter on bye gets a bye cover fact, id `NX.bye.<roster>.<pid>.cover`. A build with no snapshot has no
    lineup value, so it gives no cover fact.
    A week with nobody on bye on any roster gives no fact. Thin data gives empty lists too, so it gives no fact, and
    the writer never reads a "nobody on bye" line it cannot back.
    """
    sides = [(rid, byes) for nx in c.next for rid, byes in ((nx.a, nx.a_byes), (nx.b, nx.b_byes))]
    if not any(byes for _, byes in sides):
        return []
    bye_week = c.week.week + 1
    out = []
    for rid, byes in sides:
        team = c.team(rid)
        n = Nums()
        if not byes:
            text = f"Nobody on {team} is on bye in week {n(bye_week)}."
            out.append(fact(f"{BYE_FACT_PREFIX}{rid}.none", text, n, [team], []))
            continue
        covers = bye_covers_for_roster(c.snapshot, rid, byes) if c.snapshot is not None else None
        for p in byes:
            n = Nums()
            text = (f"{p.name}, {_ranked(p.position, p.rank, n)}, is on bye in week {n(bye_week)} and started "
                    f"{n(p.starts)} of the last {n(p.weeks)} weeks for {team}.")
            out.append(fact(f"{BYE_FACT_PREFIX}{rid}.{p.player_id}", text, n, [team], [p.name]))
            if p.key and covers is not None:
                out.append(_cover_fact(c.snapshot, rid, team, p, covers[p.player_id]))
    return out


def _cover_fact(snapshot: Snapshot, roster_id: int, team: str, starter: ByePlayer, cover: str | None) -> Fact:
    """The bye cover fact of one key starter on bye. GLOSSARY.md, "Bye cover"."""
    n = Nums()
    fid = f"{BYE_FACT_PREFIX}{roster_id}.{starter.player_id}.cover"
    if cover is None:
        return fact(fid, f"With {starter.name} on bye, no bench player can fill his slot.", n, [team], [starter.name])
    player = snapshot.players[cover]
    text = (f"With {starter.name} on bye, his slot falls to {player.name}, "
            f"{_ranked(player.position, snapshot.position_rank(cover), n)}, "
            f"with {_note_decimal(snapshot.lineup_value(cover), n)} a game.")
    return fact(fid, text, n, [team], [starter.name, player.name])


def storyline_facts(
    games: list[NextMatchup], by_rank: dict[int, Standing], team: Callable[[int], str]
) -> list[Fact]:
    """One fact per storyline kind of each next-week game, id `NX.<a>v<b>.<kind>`. GLOSSARY.md, "Storyline".

    Two streaks in one game share the streak fact, so each kind has one id per game.
    """
    out = []
    for nx in games:
        kinds = list(dict.fromkeys(s.kind for s in nx.storylines))
        for kind in kinds:
            n = Nums()
            stories = [s for s in nx.storylines if s.kind == kind]
            text = " ".join(_storyline_text(nx, s, by_rank, team, n) for s in stories)
            out.append(fact(f"NX.{nx.a}v{nx.b}.{kind}", text, n, [team(nx.a), team(nx.b)], []))
    return out


def _storyline_text(
    nx: NextMatchup, s: Storyline, by_rank: dict[int, Standing], team: Callable[[int], str], n: Nums
) -> str:
    a, b = team(nx.a), team(nx.b)
    if s.kind == "streak":
        other = b if s.roster_id == nx.a else a
        verb = "won" if s.length > 0 else "lost"
        return (f"{team(s.roster_id)} has {verb} {n(abs(s.length))} head-to-head games in a row, "
                f"so the streak is on the line against {other}.")
    if s.kind == "cut":
        sides = []
        for rid in s.teams:
            gap = by_rank[rid].games_from_cut
            if gap == 0:
                sides.append(f"{team(rid)} sits at the playoff cut.")
            else:
                side = "above" if gap > 0 else "below"
                sides.append(f"{team(rid)} sits {n(abs(gap))} game {side} the playoff cut.")
        return " ".join(sides) + " The game is near the cut."
    if s.kind == "shootout":
        x, y = s.totals
        return (f"{a} projects {_note_decimal(x, n)} and {b} projects {_note_decimal(y, n)} for next week. "
                "Both best lineups rank in the top four of the league, so the game is a shootout.")
    if s.kind == "table":
        return (f"{a} ({n.ord(by_rank[nx.a].rank)}) and {b} ({n.ord(by_rank[nx.b].rank)}) both rank in the top "
                "four, so the game is at the top of the table.")
    if s.kind == "rematch":
        if s.roster_id is None:
            return f"{a} and {b} met in week {n(s.week)} and tied. Next week is a rematch."
        return (f"{a} and {b} met in week {n(s.week)}, and {team(s.roster_id)} won by {n(s.margin)}. "
                "Next week is a rematch.")
    winner = b if s.roster_id == nx.a else a
    return (f"{team(s.roster_id)} lost to {winner} by {n(s.margin)} in week {n(s.week)}, "
            "so next week is a chance at revenge.")


# The writer reads one number to pick a shootout, so a long list of names adds no value past this cap.
SHOOTOUT_NAMES_MAX = 8


def _last_games(count: int, n: Nums) -> str:
    return "its last game" if count == 1 else f"its last {n(count)} games"


def _note_decimal(x: float, n: Nums) -> str:
    # The text form lives in `numbers`. This wrapper records the number, so the check of the numbers still sees it.
    s = one_decimal_text(x)
    n.seen.append(s)
    return s


def _note_count(count: int, word: str, n: Nums) -> str:
    # The wording lives in `numbers`. This wrapper records the count, so the check of the numbers still sees it.
    n.seen.append(str(count))
    return count_noun(count, word)


def shootout_facts(c: Context) -> list[Fact]:
    """One fact per shootout of next week, with the league starters in that game by roster.

    The lineups of next week are not set yet, so a starter is a player in a starting lineup of this week.
    """
    out = []
    for s in shootouts(c.nfl):
        n = Nums()
        # Short sentences, and the unit once, so the writer cannot turn the rate into a percent.
        text = (
            f"{s.away} at {s.home} next week is a shootout. {s.away}'s pass rate over expected is "
            f"{_note_decimal(s.away_rate, n)} percentage points over {_last_games(s.away_games, n)}. "
            f"{s.home}'s is {_note_decimal(s.home_rate, n)} over {_last_games(s.home_games, n)}."
        )
        starters = [
            (side.roster_id, line.name)
            for m in c.week.matchups for side in (m.a, m.b) for line in side.lines
            if line.started and line.nfl_team in (s.away, s.home)
        ]
        shown: dict[int, list[str]] = {}
        for rid, name in starters[:SHOOTOUT_NAMES_MAX]:
            shown.setdefault(rid, []).append(name)
        if starters:
            rosters = {rid for rid, _ in starters}
            text += (
                f" {_note_count(len(starters), 'league starter', n)} on {_note_count(len(rosters), 'roster', n)}: "
                + "; ".join(f"{c.team(rid)} ({', '.join(names)})" for rid, names in shown.items())
            )
            more = len(starters) - SHOOTOUT_NAMES_MAX
            text += f"; and {n(more)} more." if more > 0 else "."
        else:
            text += " No league starter plays in that game."
        out.append(fact(f"NX.shootout.{s.away}v{s.home}", text, n, [c.team(rid) for rid in shown],
                        [name for names in shown.values() for name in names]))
    return out
