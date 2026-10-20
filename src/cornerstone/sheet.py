"""
Builds the fact sheet and the bundle that the writer and the page read.
The fact sheet is the only input the writer sees, so each fact carries every number as the page shows it.
"""
import logging
import re
from collections.abc import Callable
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from cornerstone.facts_league import (
    TREND_WEEKS,
    _ordinal,
    awards,
    matchup_of_the_week,
    next_week,
    position_ranks,
    ranks_before,
    season_history,
    standings,
)
from cornerstone.facts_matchup import matchup_facts, median_facts
from cornerstone.facts_nflverse import drop_lines
from cornerstone.history import player_points, player_trend
from cornerstone.models import (
    Bundle,
    Chapter,
    DropLine,
    Fact,
    FactSheet,
    History,
    NflverseWeek,
    PlayerLine,
    Trade,
    Week,
    WeekData,
    r2,
    sub,
)
from cornerstone.sleeper import fetch_news
from cornerstone.trades import is_late

logger = logging.getLogger(__name__)

FIRST_WEEK = 6
LAST_WEEK = 14
# A chapter cites at most this many facts with an ID that starts with "H." or "P.", so the writer
# stays focused. The cap does not cover the position-rank facts.
HISTORY_FACTS_MAX = 6
# Slots kept for player trends, so the team facts cannot crowd them out of a chapter.
PLAYER_TREND_MAX = 2
NEWS_MAX_CHARS = 300
MOVE_WORDS = {"waiver": "waiver add", "free_agent": "free agent add", "trade": "trade"}
AWARD_TITLES = {
    "game_changer": "Game Changer",
    "top_scorer": "Top Scorer",
    "mvb": "MVB",
    "underperformer": "Underperformer",
    "overachiever": "Overachiever",
    "butterfingers": "Butterfingers",
}
# (min, max) sentences per chapter, from the spec.
SENTENCE_RANGES = {
    "motw": (4, 6),
    "game_changer": (3, 5),
    "awards": (2, 4),
    "recap": (2, 3),
    "median": (2, 4),
    "next_week": (1, 2),
    "trades": (4, 6),
}
# A record such as 33-30 is one token. A leading minus belongs to a negative number.
NUMBER_TOKEN = re.compile(r"\d+-\d+|(?<!\d)-?\d+(?:\.\d+)?|\d+(?:\.\d+)?")
PART_TOKEN = re.compile(r"\d+(?:\.\d+)?")
# Most telling first: a chapter over the cap keeps the front of this order.
HISTORY_KINDS = ("streak", "high", "trend", "avg")


def fmt(x: float) -> str:
    """Shortest two-decimal form: 106.8 for 106.80, 21 for 21.0."""
    return f"{r2(x):.2f}".rstrip("0").rstrip(".")


def week_dates(season_start: date, week: int) -> str:
    thursday = season_start + timedelta(days=1 + 7 * (week - 1))
    monday = thursday + timedelta(days=4)
    return f"{thursday.strftime('%b %-d')} – {monday.strftime('%b %-d, %Y')}"


def check_week_is_buildable(week_target: int, last_scored: int) -> str | None:
    # Playoff comes first: a playoff week is never buildable, scored or not.
    if week_target > LAST_WEEK:
        return f"Week {week_target} is a playoff week. Version 1 covers weeks {FIRST_WEEK} to {LAST_WEEK}."
    if last_scored < week_target:
        return f"Sleeper has scored through week {last_scored}. Week {week_target} is not final."
    return None


class Nums:
    """Formats values for fact text and records each one, so `numbers` is exact."""

    def __init__(self) -> None:
        self.seen: list[str] = []

    def __call__(self, x: float | int) -> str:
        s = str(x) if isinstance(x, int) else fmt(x)
        self.seen.append(s)
        return s

    def ord(self, n: int) -> str:
        self.seen.append(str(n))
        return _ordinal(n)

    def record(self, wins: int, losses: int) -> str:
        self.seen += [str(wins), str(losses), f"{wins}-{losses}"]
        return f"{wins}-{losses}"

    def text(self, raw: str) -> str:
        """Record the numbers in text that code already wrote. Rewrite decimals to the page form."""
        out = PART_TOKEN.sub(
            lambda m: fmt(float(m.group())) if "." in m.group() else m.group(), raw
        )
        for token in NUMBER_TOKEN.findall(out):
            # A record or a negative number also lists its plain parts.
            self.seen += [token, *(p for p in PART_TOKEN.findall(token) if p != token)]
        return out


def _fact(fid: str, text: str, n: Nums, teams: list[str], players: list[str]) -> Fact:
    return Fact(id=fid, text=text, numbers=n.seen, teams=teams, players=players)


class Context:
    """Lookups shared by every fact family."""

    def __init__(
        self,
        week: Week,
        news: Callable[[str], list[dict]],
        history: History | None = None,
        trades: list[Trade] | None = None,
        nfl: NflverseWeek | None = None,
    ) -> None:
        self.week = week
        self.history = history
        self.trades = trades if trades is not None else []
        self.news = news
        # The week before is in the history, so a recent add of that week shows in this week.
        self.moves = list(week.moves)
        if history is not None and week.week - 1 in history.weeks:
            self.moves += history.weeks[week.week - 1].moves
        self.mfacts = [matchup_facts(m, self.moves, week.week) for m in week.matchups]
        self.table = standings(week, history)
        self.by_rank = {s.roster_id: s for s in self.table}
        self.before = ranks_before(week, self.table, history)
        self.median = median_facts(week)
        self.pick = matchup_of_the_week(week, self.mfacts, self.table, self.before)
        self.drops = drop_lines(week, nfl)
        self.nfl = nfl
        self.nfl_up = nfl is not None and nfl.drops is not None
        self.awards = awards(week, self.mfacts, self.drops)
        self.next = next_week(week, self.table)
        self.season_history = season_history(week, history)
        self.ranks = position_ranks(week)
        self.scores = {s.roster_id: s.points for m in week.matchups for s in (m.a, m.b)}
        self.line_owner = {
            l.player_id: s.roster_id
            for m in week.matchups for s in (m.a, m.b) for l in s.lines
        }
        self.lines = {
            l.player_id: l for m in week.matchups for s in (m.a, m.b) for l in s.lines
        }

    def team(self, roster_id: int) -> str:
        return self.week.teams[roster_id].name

    def who(self, line: PlayerLine) -> str:
        where = f"{line.position}, {line.nfl_team}" if line.nfl_team else line.position
        return f"{line.name} ({where})"

    def against_projection(self, line: PlayerLine, n: Nums) -> str:
        """The 'scored X on a Y projection, Z over' clause, or the no-projection form."""
        if line.projection is None:
            return f"scored {n(line.points)} with no projection"
        gap = sub(line.points, line.projection)
        side = "over" if gap >= 0 else "under"
        return f"scored {n(line.points)} on a {n(line.projection)} projection, {n(abs(gap))} {side}"


def week_facts(c: Context) -> list[Fact]:
    w = c.week
    n = Nums()
    week_text = f"This is week {n(w.week)} of the {n(w.season)} season, {n.text(week_dates(w.season_start, w.week))}."
    n2 = Nums()
    publish = f"The report was published on {n2.text(date.today().strftime('%a %b %-d, %Y'))}."
    return [
        _fact("W.week", week_text, n, [], []),
        _fact("W.publish", publish, n2, [], []),
    ]


def recent_add_facts(c: Context) -> list[Fact]:
    """The top three started lines added in this week or the week before, by points."""
    found = []
    for f in c.mfacts:
        for mv in f.recent_moves:
            found.append((c.lines[mv.player_id], mv))
    top = sorted(found, key=lambda x: x[0].points, reverse=True)[:3]
    if not top:
        return []
    n = Nums()
    parts = [
        f"{c.who(line)} for {c.team(mv.roster_id)}, a {MOVE_WORDS[mv.kind]} in week {n(mv.week)}, "
        + c.against_projection(line, n)
        for line, mv in top
    ]
    text = "The top recent adds who started: " + "; ".join(parts) + "."
    teams = sorted({c.team(mv.roster_id) for _, mv in top})
    return [_fact("W.adds", text, n, teams, [line.name for line, _ in top])]


def injured_facts(c: Context) -> list[Fact]:
    """Every started line with a Sleeper injury status, league-wide."""
    found = [
        (line, c.team(side.roster_id))
        for m in c.week.matchups for side in (m.a, m.b) for line in side.lines
        if line.started and line.injury_status
    ]
    if not found:
        return []
    parts = [f"{line.name} ({team}, {line.injury_status})" for line, team in found]
    text = "Now on the injury report after this week's games: " + "; ".join(parts) + "."
    teams = sorted({team for _, team in found})
    return [_fact("W.injured", text, Nums(), teams, [line.name for line, _ in found])]


def standings_facts(c: Context) -> list[Fact]:
    out = []
    for s in c.table:
        n = Nums()
        cut = "in" if s.in_playoffs else "out of"
        side = "above" if s.games_from_cut > 0 else "below" if s.games_from_cut < 0 else "at"
        team = c.team(s.roster_id)
        gap = abs(s.games_from_cut)
        games = "game" if gap == 1 else "games"
        text = (
            f"{team} is {n.ord(s.rank)} with a {n.record(s.wins, s.losses)} record "
            f"and {n(s.points_for)} points for, {cut} the playoff spots, "
            f"{n(gap)} {games} {side} the cut."
        )
        out.append(_fact(f"S.{s.rank}", text, n, [team], []))
    return out


def median_facts_sheet(c: Context) -> list[Fact]:
    m = c.median
    n = Nums()
    out = [_fact("MED.value", f"The league median this week was {n(m.median)}.", n, [], [])]
    # Gaps use the exact median, as median_facts does, so a rounded median never shifts a gap.
    ordered = sorted(c.scores.values(), reverse=True)
    exact = (Decimal(str(ordered[5])) + Decimal(str(ordered[6]))) / 2
    for kind, rosters, word in (("above", m.above, "above"), ("below", m.below, "below")):
        for rid in rosters:
            n = Nums()
            gap = r2(abs(float(Decimal(str(c.scores[rid])) - exact)))
            team = c.team(rid)
            text = f"{team} scored {n(c.scores[rid])}, {n(gap)} {word} the median."
            out.append(_fact(f"MED.{kind}.{rid}", text, n, [team], []))
    n = Nums()
    (up_id, up_gap), (down_id, down_gap) = m.closest_above, m.closest_below
    text = (
        f"{c.team(up_id)} cleared the median by {n(up_gap)}. "
        f"{c.team(down_id)} missed it by {n(down_gap)}."
    )
    out.append(_fact("MED.closest", text, n, [c.team(up_id), c.team(down_id)], []))
    return out


def matchup_fact_family(c: Context) -> list[Fact]:
    out = []
    for f, m in zip(c.mfacts, c.week.matchups):
        out += _result_facts(c, f, m)
        out += _line_facts(c, f, m)
        out += _story_facts(c, f)
        out += _injury_facts(c, f, m)
        out += _context_facts(c, f, m)
    return out


def _result_facts(c, f, m) -> list[Fact]:
    n = Nums()
    mid = f"M{f.matchup_id}"
    a, b = c.team(m.a.roster_id), c.team(m.b.roster_id)
    if f.winner is None:
        text = f"{a} and {b} tied at {n(f.score_w)}."
        teams = [a, b]
    else:
        w, l = c.team(f.winner), c.team(f.loser)
        text = f"{w} beat {l} {n(f.score_w)} to {n(f.score_l)}, a margin of {n(f.margin)}."
        teams = [w, l]
    out = [_fact(f"{mid}.result", text, n, teams, [])]
    for rid, line in f.top_scorer.items():
        n = Nums()
        team = c.team(rid)
        text = f"{c.who(line)} was the top scorer for {team} with {n(line.points)}."
        out.append(_fact(f"{mid}.top.{rid}", text, n, [team], [line.name]))
    return out


def _line_facts(c, f, m) -> list[Fact]:
    out = []
    for side in (m.a, m.b):
        team = c.team(side.roster_id)
        for line in side.lines:
            if not line.started:
                continue
            n = Nums()
            text = f"{c.who(line)} started for {team} and {c.against_projection(line, n)}."
            out.append(_fact(f"M{f.matchup_id}.starter.{side.roster_id}.{line.player_id}", text, n, [team], [line.name]))
    return out


def _story_facts(c, f) -> list[Fact]:
    """Drivers, swing players, bench regret, and recent adds for one matchup."""
    mid = f"M{f.matchup_id}"
    out = []
    for line in f.drivers:
        n = Nums()
        team = c.team(c.line_owner[line.player_id])
        gap = abs(sub(line.points, line.projection))
        text = (
            f"{line.name} ({team}) is a margin driver: {n(line.points)} on a {n(line.projection)} "
            f"projection, a gap of {n(gap)} against a margin of {n(f.margin)}."
        )
        out.append(_fact(f"{mid}.driver.{line.player_id}", text, n, [team], [line.name]))
    for line in f.swing:
        n = Nums()
        team = c.team(f.winner)
        text = f"{line.name} is a swing player for {team}: {n(line.points)} exceeded the margin of {n(f.margin)}."
        out.append(_fact(f"{mid}.swing.{line.player_id}", text, n, [team], [line.name]))
    for bench, starter in f.bench_regret:
        n = Nums()
        team = c.team(f.loser)
        text = (
            f"{team} left {bench.name} ({n(bench.points)}) on the bench behind "
            f"{starter.name} ({n(starter.points)}); the swap would have flipped the result."
        )
        out.append(_fact(f"{mid}.regret.{bench.player_id}", text, n, [team], [bench.name, starter.name]))
    for mv in f.recent_moves:
        n = Nums()
        line = c.lines[mv.player_id]
        team = c.team(mv.roster_id)
        text = (
            f"{line.name} is a recent add: {line.name} started for {team} after a "
            f"{MOVE_WORDS[mv.kind]} in week {n(mv.week)} "
            f"and {c.against_projection(line, n)}."
        )
        out.append(_fact(f"{mid}.move.{mv.player_id}", text, n, [team], [line.name]))
    return out


def _injury_facts(c, f, m) -> list[Fact]:
    """One fact per started line with a Sleeper injury status in one matchup."""
    out = []
    for side in (m.a, m.b):
        team = c.team(side.roster_id)
        for line in side.lines:
            if not line.started or not line.injury_status:
                continue
            # The status comes from the players file fetched after the games, so it is post-game.
            # The fact must not imply that the player was hurt at kickoff.
            status = f"listed {line.injury_status}"
            if line.injury_body_part:
                status += f" ({line.injury_body_part})"
            text = (
                f"{line.name} is now {status} on Sleeper as of the Tuesday after this week's games. "
                "The status may have come from this game."
            )
            out.append(_fact(f"M{f.matchup_id}.inj.{line.player_id}", text, Nums(), [team], [line.name]))
    return out


def _context_facts(c, f, m) -> list[Fact]:
    mid = f"M{f.matchup_id}"
    out = []
    if f.winner is not None and c.before[f.winner] > c.before[f.loser]:
        n = Nums()
        w, l = c.team(f.winner), c.team(f.loser)
        text = (
            f"This was an upset: {w} was {n.ord(c.before[f.winner])} before this week "
            f"and {l} was {n.ord(c.before[f.loser])}."
        )
        out.append(_fact(f"{mid}.upset", text, n, [w, l], []))
    n = Nums()
    parts = []
    for rid in (m.a.roster_id, m.b.roster_id):
        s = c.by_rank[rid]
        parts.append(f"{c.team(rid)} is now {n.record(s.wins, s.losses)} ({n.ord(s.rank)}).")
    teams = [c.team(m.a.roster_id), c.team(m.b.roster_id)]
    out.append(_fact(f"{mid}.records", " ".join(parts), n, teams, []))
    return out


def award_facts(c: Context) -> list[Fact]:
    out = []
    for aw in c.awards:
        n = Nums()
        team = c.team(aw.roster_id)
        text = f"{AWARD_TITLES[aw.key]}: {c.who(aw.line)}, {team}. {n.text(aw.reason)}"
        if aw.skipped:
            text += f" Skipped: {', '.join(aw.skipped)}."
        out.append(_fact(f"AW.{aw.key}", text, n, [team], [aw.line.name, *aw.skipped]))
    gc = next((a for a in c.awards if a.key == "game_changer"), None)
    if gc:
        out += _news_facts(c, gc)
    return out


def _news_facts(c: Context, gc) -> list[Fact]:
    # News is an unofficial endpoint. A failure must never stop a build.
    try:
        items = c.news(gc.line.player_id)
        # Items arrive in no promised order, and "published" is epoch milliseconds as a string.
        newest = max(items, key=lambda i: int(i.get("published") or 0), default={})
    except Exception:
        logger.exception("News fetch failed for %s", gc.line.name)
        return []
    description = (newest.get("metadata") or {}).get("description") or ""
    if not description:
        return []
    n = Nums()
    text = f"Latest news on {gc.line.name}: {n.text(_cut_at_word(description, NEWS_MAX_CHARS))}"
    return [_fact("AW.game_changer.news", text, n, [], [gc.line.name])]


def _cut_at_word(text: str, limit: int) -> str:
    """Cut at the last whitespace before the limit, so no word or number is cut in half."""
    if len(text) <= limit:
        return text
    head = text[:limit]
    space = max(head.rfind(" "), head.rfind("\n"), head.rfind("\t"))
    return (head[:space] if space > 0 else head).rstrip()


def pick_facts(c: Context) -> list[Fact]:
    m = next(m for m in c.week.matchups if m.matchup_id == c.pick.matchup_id)
    a, b = c.team(m.a.roster_id), c.team(m.b.roster_id)
    text = f"Matchup of the Week is {a} vs {b}, chosen for {c.pick.reason}."
    return [_fact("PICK", text, Nums(), [a, b], [])]


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
        out.append(_fact(f"NX.{nx.a}v{nx.b}", text, n, [c.team(nx.a), c.team(nx.b)], []))
    return out



def rank_facts(c: Context) -> list[Fact]:
    out = []
    for r in c.ranks:
        n = Nums()
        line = c.lines[r.player_id]
        team = c.team(c.line_owner[r.player_id])
        text = f"{line.name} ranked {n(r.rank)} of {n(r.of)} among started {r.position}s this week, for {team}."
        out.append(_fact(f"RANK.{r.player_id}", text, n, [team], [line.name]))
    return out


def strength_facts(c: Context) -> list[Fact]:
    out = []
    for s in c.table:
        if s.schedule_strength is None:
            continue
        n = Nums()
        team = c.team(s.roster_id)
        # Version 1 knows only the next opponent, so the fact names next week, not the rest of the season.
        text = (
            f"{team}'s opponent next week has a win rate of {n(s.schedule_strength)}, "
            f"ranked {n(s.strength_rank)} of {n(12)}, toughest first."
        )
        out.append(_fact(f"SOS.{s.roster_id}", text, n, [team], []))
    return out


def history_facts(c: Context) -> list[Fact]:
    """Streak, trend, season high or low, and season average of each team.

    A missing or incomplete history gives no facts, so a fact is never wrong.
    """
    if c.history is None or not c.history.complete():
        return []
    out = []
    for h in c.season_history:
        team = c.team(h.roster_id)
        rid = h.roster_id
        if abs(h.streak) >= 2:
            n = Nums()
            verb = "won" if h.streak > 0 else "lost"
            out.append(_fact(f"H.{rid}.streak", f"{team} has {verb} {n(abs(h.streak))} straight.", n, [team], []))
        if h.trend is not None and r2(h.trend) != r2(h.average):
            n = Nums()
            side = "up" if h.trend > h.average else "down"
            text = (
                f"{team} has scored {n(h.trend)} per week over the last {n(TREND_WEEKS)} weeks, "
                f"{side} from a season average of {n(h.average)}."
            )
            out.append(_fact(f"H.{rid}.trend", text, n, [team], []))
        # Week 1 has no earlier week, so no score there is a high or a low.
        if c.week.week > 1 and (h.new_high or h.new_low):
            n = Nums()
            kind = "high" if h.new_high else "low"
            text = f"{team}'s {n(c.scores[rid])} this week is a season {kind}."
            out.append(_fact(f"H.{rid}.high", text, n, [team], []))
        n = Nums()
        out.append(_fact(f"H.{rid}.avg", f"{team} averages {n(h.average)} per week this season.", n, [team], []))
    return out


def _trend_text(name: str, beaten: int, n: Nums) -> str:
    if beaten >= 2:
        return f"{name} has beaten projection in {n(beaten)} of the last {n(TREND_WEEKS)} weeks."
    return f"{name} has missed projection in {n(TREND_WEEKS - beaten)} of the last {n(TREND_WEEKS)} weeks."


def player_trend_facts(c: Context) -> list[Fact]:
    """One trend fact for each started line. A missing or incomplete history gives none."""
    if c.history is None or not c.history.complete():
        return []
    out = []
    for pid, line in c.lines.items():
        beaten = player_trend(c.history, pid)
        if not line.started or beaten is None:
            continue
        n = Nums()
        out.append(_fact(f"P.{pid}.trend", _trend_text(line.name, beaten, n), n, [], [line.name]))
    return out


def _join(items: list[str]) -> str:
    """A, A and B, or A, B and C."""
    if len(items) < 2:
        return "".join(items)
    return f"{', '.join(items[:-1])} and {items[-1]}"


def _moved(trade: Trade, rid: int, got: bool) -> list[str]:
    """The player IDs a roster got or gave, in the order of `adds`."""
    if got:
        return [pid for pid, owner in trade.adds.items() if owner == rid]
    return [pid for pid in trade.adds if trade.drops.get(pid) == rid]


def _items(c: Context, trade: Trade, rid: int, got: bool, n: Nums) -> list[str]:
    """The players, then the picks, that a roster got or gave. Players keep the order of `adds`."""
    # A player with no line was on no roster at lineup lock, so the week has no points to cite for him.
    # He stays in the sides text under a plain label, and gets no got or gave fact.
    names = [c.lines[pid].name if pid in c.lines else "an unlisted player" for pid in _moved(trade, rid, got)]
    picks = [
        f"{n(int(p.season))} round {n(p.round)} pick" for p in trade.draft_picks
        if (p.owner_id if got else p.previous_owner_id) == rid
    ]
    return names + picks


def _sides_fact(c: Context, i: int, trade: Trade) -> Fact:
    n = Nums()
    ids = trade.roster_ids
    if len(ids) == 2:
        a, b = ids
        text = (
            f"{c.team(a)} traded {_join(_items(c, trade, a, False, n))} to {c.team(b)} "
            f"for {_join(_items(c, trade, a, True, n))}."
        )
    else:
        clauses = [f"{c.team(r)} got {_join(_items(c, trade, r, True, n))}" for r in ids]
        text = f"In a {n(len(ids))}-team trade, {'; '.join(clauses)}."
    players = [c.lines[pid].name for pid in trade.adds if pid in c.lines]
    return _fact(f"T{i}.sides", text, n, [c.team(r) for r in ids], players)


def _pregame_text(c: Context, pid: str) -> str | None:
    """The final NFL injury report status of this week, or None when the player has none."""
    if c.nfl is None or c.nfl.injuries is None:
        return None
    status = c.nfl.injuries.get(pid, {}).get(c.week.week)
    if status is None:
        return None
    return f"{c.lines[pid].name} was listed {status} on the final NFL injury report before his game this week."


def _player_trade_fact(c: Context, i: int, rid: int, pid: str, verb: str) -> Fact:
    n = Nums()
    line = c.lines[pid]
    team = c.team(rid)
    clauses = [f"{n(line.points)} this week"]
    # A season total from a partial history would be wrong, so a gap drops the clause.
    complete = c.history is not None and c.history.complete()
    weeks = [c.history.weeks[w] for w in range(1, c.week.week + 1)] if complete else []
    # A week with no roster points and empty stats is an outage of the stats endpoint, not a 0.
    if complete and not any(player_points(w, pid) is None and not w.stats for w in weeks):
        total = sum(Decimal(str(player_points(w, pid) or 0)) for w in weeks)
        clauses.append(f"{n(float(total))} this season")
    rank = next((r for r in c.ranks if r.player_id == pid), None)
    if rank is not None:
        clauses.append(f"position rank {n(rank.rank)} of {n(rank.of)}")
    text = f"{team} {verb} {line.name}: {', '.join(clauses)}."
    pregame = _pregame_text(c, pid)
    if pregame is not None:
        text += " " + pregame
    beaten = player_trend(c.history, pid) if complete else None
    if beaten is not None:
        text += " " + _trend_text(line.name, beaten, n)
    return _fact(f"T{i}.{rid}.{verb}.{pid}", text, n, [team], [line.name])


def _need_fact(c: Context, i: int, trade: Trade, rid: int) -> Fact:
    n = Nums()
    team = c.team(rid)
    side = next(s for m in c.week.matchups for s in (m.a, m.b) if s.roster_id == rid)
    positions = sorted({c.lines[pid].position for pid in (*trade.adds, *trade.drops) if pid in c.lines})
    depth = [f"{n(sum(l.position == pos for l in side.lines))} {pos}" for pos in positions]
    spots = max(0, c.week.roster_slots - len(side.lines))
    standing = c.by_rank[rid]
    text = (
        f"{team} is {n.record(standing.wins, standing.losses)}, {n.ord(standing.rank)} of {n(12)}, "
        f"with {_join(depth)} after the trade and {n(spots)} open roster {'spot' if spots == 1 else 'spots'}."
    )
    return _fact(f"T{i}.{rid}.need", text, n, [team], [])


def _swing_fact(c: Context, i: int, trade: Trade, rid: int) -> Fact | None:
    """The points of the traded starters against the margin of the roster's matchup."""
    # A player with no line counts 0, so he is left out of both sums.
    got = [c.lines[pid] for pid in _moved(trade, rid, True) if pid in c.lines]
    gave = [c.lines[pid] for pid in _moved(trade, rid, False) if pid in c.lines]
    # A later trade can move a player on, so a line counts only for the roster that holds it in the lineup.
    # The roster that got him must own the line. The roster that got him from the giver must own it for "gave".
    got_started = [l for l in got if l.started and c.line_owner[l.player_id] == rid]
    gave_started = [
        l for l in gave if l.started and c.line_owner[l.player_id] == trade.adds[l.player_id]
    ]
    if not got_started and not gave_started:
        return None
    n = Nums()
    x = sum((Decimal(str(l.points)) for l in got_started), Decimal(0))
    y = sum((Decimal(str(l.points)) for l in gave_started), Decimal(0))
    f = next(f for f, m in zip(c.mfacts, c.week.matchups) if rid in (m.a.roster_id, m.b.roster_id))
    # The trade decided the game only when it points the same way as the result: the winner gained
    # at least the margin, or the loser lost at least the margin. A tie has no direction.
    toward = float(x - y) if rid == f.winner else float(y - x) if rid == f.loser else None
    team = c.team(rid)
    others = [r for r in trade.roster_ids if r != rid]
    partners = c.team(others[0]) if len(others) == 1 else "its trade partners"
    text = (
        f"The players {team} got and started scored {n(float(x))} this week; "
        f"the players it gave that {partners} started scored {n(float(y))}. "
    )
    if toward is not None and r2(toward) >= r2(f.margin):
        side = "above" if r2(toward) > r2(f.margin) else "equal to"
        text += f"The gap is {n(toward)}, {side} the margin of {n(f.margin)} in its matchup."
    else:
        text += (
            f"In its matchup, that is a gap of {n(abs(float(x - y)))} against a margin of {n(f.margin)}, "
            "not enough to change the result."
        )
    teams = [team, *(c.team(r) for r in others)] if len(others) == 1 else [team]
    return _fact(f"T{i}.{rid}.swing", text, n, teams, [l.name for l in (*got_started, *gave_started)])


def trade_facts(c: Context) -> list[Fact]:
    out = []
    for i, trade in enumerate(c.trades, start=1):
        out.append(_sides_fact(c, i, trade))
        for rid in trade.roster_ids:
            out += [_player_trade_fact(c, i, rid, pid, "got") for pid in _moved(trade, rid, True) if pid in c.lines]
            out += [_player_trade_fact(c, i, rid, pid, "gave") for pid in _moved(trade, rid, False) if pid in c.lines]
        # A late trade happened after the lineups locked, so the lineup shows the roster from before it.
        if is_late(trade, c.week):
            continue
        for rid in trade.roster_ids:
            out.append(_need_fact(c, i, trade, rid))
            swing = _swing_fact(c, i, trade, rid)
            if swing is not None:
                out.append(swing)
    return out


def _drop_fact(c: Context, d: DropLine) -> list[Fact]:
    line, team = c.lines[d.player_id], c.team(d.roster_id)
    n = Nums()
    if d.targets is None:
        text = f"{line.name} dropped {n(d.drops)} passes this week."
    else:
        text = f"{line.name} dropped {n(d.drops)} of {n(d.targets)} targets this week."
    out = [_fact(f"D.{d.player_id}", text, n, [team], [line.name])]
    if d.value is not None:
        n = Nums()
        text = (
            f"{line.name}'s drops were worth about {n(d.value)} points by the drop value method, "
            f"with {n(d.end_zone)} in the end zone."
        )
        out.append(_fact(f"D.{d.player_id}.value", text, n, [team], [line.name]))
    return out


def _dropswing_facts(c: Context) -> list[Fact]:
    """The losing side's started drop value against the margin. Only nflverse gives a value."""
    out = []
    for f in c.mfacts:
        if f.loser is None or not c.nfl_up:
            continue
        lost = [d for d in c.drops if d.roster_id == f.loser and d.matchup_id == f.matchup_id]
        value = sum((Decimal(str(d.value)) for d in lost), Decimal(0))
        if not lost or value < Decimal(str(f.margin)):
            continue
        n = Nums()
        team = c.team(f.loser)
        text = (
            f"{team}'s starters dropped {n(sum(d.drops for d in lost))} passes worth about "
            f"{n(float(value))}, at least the margin of {n(f.margin)}."
        )
        out.append(_fact(f"M{f.matchup_id}.dropswing", text, n, [team], [c.lines[d.player_id].name for d in lost]))
    return out


def drop_facts(c: Context) -> list[Fact]:
    out = [fact for d in c.drops for fact in _drop_fact(c, d)]
    out += _dropswing_facts(c)
    if c.drops:
        n = Nums()
        top = c.drops[:3]
        parts = [f"{c.lines[d.player_id].name} ({c.team(d.roster_id)}), {n(d.drops)}" for d in top]
        out.append(_fact("W.drops", "Most drops this week: " + "; ".join(parts) + ".", n,
                         [c.team(d.roster_id) for d in top], [c.lines[d.player_id].name for d in top]))
    return out


def _weeks(count: int, n: Nums, adjective: str = "") -> str:
    return f"{n(count)} {adjective}week" + ("" if count == 1 else "s")


def injury_facts_nfl(c: Context) -> list[Fact]:
    """The pre-game status and the report history of each started player. None without nflverse."""
    if c.nfl is None or c.nfl.injuries is None:
        return []
    week = c.week.week
    out = []
    for pid, line in c.lines.items():
        weeks = c.nfl.injuries.get(pid)
        if not line.started or not weeks:
            continue
        team = [c.team(c.line_owner[pid])]
        pregame = _pregame_text(c, pid)
        if pregame is not None:
            out.append(_fact(f"I.{pid}.pregame", pregame, Nums(), team, [line.name]))
        n = Nums()
        if week in weeks:
            text = f"{line.name} has been on the report {_weeks(sum(w <= week for w in weeks), n)}."
        # A return claim needs proof of play: nflverse only lists the injured, so a gap alone is not a return.
        elif week - 1 in weeks and c.week.stats.get(pid, {}).get("gp", 0) > 0:
            earlier = _weeks(sum(w < week for w in weeks), n, "earlier ")
            text = f"{line.name} was on the NFL injury report in {earlier} this season and plays this week."
        else:
            continue
        out.append(_fact(f"I.{pid}.history", text, n, team, [line.name]))
    return out


def _history_ids(facts: dict[str, Fact], rosters, kinds, players=()) -> list[str]:
    """History and player trend fact IDs, most telling first, cut to the cap.

    The team facts keep the slots the player trends leave.
    """
    trends = [f"P.{p}.trend" for p in players if f"P.{p}.trend" in facts][:PLAYER_TREND_MAX]
    ids = [f"H.{r}.{k}" for k in kinds for r in rosters]
    teams = [i for i in ids if i in facts][: HISTORY_FACTS_MAX - len(trends)]
    return teams + trends


def _with_prefix(facts: dict[str, Fact], *prefixes: str) -> list[str]:
    return [fid for fid in facts if any(fid == p or fid.startswith(p) for p in prefixes)]


def _dedupe(ids: list[str]) -> list[str]:
    return list(dict.fromkeys(ids))


def chapters(c: Context, facts: dict[str, Fact]) -> list[Chapter]:
    week = c.week
    roster_ids = {m.matchup_id: (m.a.roster_id, m.b.roster_id) for m in week.matchups}
    all_rosters = list(week.teams)

    def players_of(rosters) -> list[str]:
        return [
            l.name
            for m in week.matchups for s in (m.a, m.b) if s.roster_id in rosters for l in s.lines
        ]

    def started_ids(rosters) -> list[str]:
        return [
            l.player_id
            for m in week.matchups for s in (m.a, m.b) if s.roster_id in rosters
            for l in s.lines if l.started
        ]

    def make(key, title, ids, rosters, rng, grade_keys=()) -> Chapter:
        return Chapter(
            key=key,
            title=title,
            fact_ids=_dedupe([i for i in ids if i in facts]),
            scope_teams=[c.team(r) for r in rosters],
            scope_players=players_of(rosters),
            min_sentences=SENTENCE_RANGES[rng][0],
            max_sentences=SENTENCE_RANGES[rng][1],
            grade_keys=list(grade_keys),
        )

    def drop_ids(keep) -> list[str]:
        return [fid for d in c.drops if keep(d) for fid in (f"D.{d.player_id}", f"D.{d.player_id}.value")]

    def injury_ids(pids) -> list[str]:
        return [fid for p in pids for fid in (f"I.{p}.pregame", f"I.{p}.history")]

    def standings_ids(rosters) -> list[str]:
        return [f"S.{c.by_rank[r].rank}" for r in rosters]

    out = []
    pair = roster_ids[c.pick.matchup_id]
    out.append(make(
        "motw", "Matchup of the Week",
        _with_prefix(facts, f"M{c.pick.matchup_id}.") + ["PICK"] + standings_ids(pair)
        + [f"RANK.{p}" for p in started_ids(pair)]
        + _history_ids(facts, pair, HISTORY_KINDS, started_ids(pair))
        + drop_ids(lambda d: d.matchup_id == c.pick.matchup_id) + injury_ids(started_ids(pair)),
        pair, "motw",
    ))
    gc = next((a for a in c.awards if a.key == "game_changer"), None)
    if gc:
        pair = roster_ids[gc.matchup_id]
        out.append(make(
            "game_changer", "Game Changer",
            ["AW.game_changer", "AW.game_changer.news"] + _with_prefix(facts, f"M{gc.matchup_id}.")
            + [f"RANK.{gc.line.player_id}"] + _history_ids(facts, [], (), [gc.line.player_id])
            + drop_ids(lambda d: d.player_id == gc.line.player_id) + injury_ids([gc.line.player_id]),
            pair, "game_changer",
        ))
    out.append(make(
        "awards", "Awards",
        _with_prefix(facts, "AW.") + ["W.adds", "W.injured"] + [f"RANK.{a.line.player_id}" for a in c.awards]
        + [f"M{mid}.result" for mid in roster_ids]
        + _history_ids(facts, [], (), [a.line.player_id for a in c.awards])
        + ["W.drops"] + drop_ids(lambda d: d.player_id in {a.line.player_id for a in c.awards})
        + injury_ids([a.line.player_id for a in c.awards]),
        all_rosters, "awards",
    ))
    for mid, pair in roster_ids.items():
        title = " vs ".join(c.team(r) for r in pair)
        out.append(make(
            f"recap_{mid}", title,
            _with_prefix(facts, f"M{mid}.") + standings_ids(pair)
            + _history_ids(facts, pair, HISTORY_KINDS, started_ids(pair))
            + drop_ids(lambda d, mid=mid: d.matchup_id == mid) + injury_ids(started_ids(pair)),
            pair, "recap",
        ))
    if c.trades:
        trade_rosters = _dedupe([r for t in c.trades for r in t.roster_ids])
        out.append(make(
            "trades", "Trades",
            _with_prefix(facts, "T") + standings_ids(trade_rosters),
            trade_rosters, "trades",
            grade_keys=[f"T{i}.{r}" for i, t in enumerate(c.trades, start=1) for r in t.roster_ids],
        ))
    out.append(make(
        "median", "The Median Game",
        _with_prefix(facts, "MED.") + _with_prefix(facts, "S.")
        + _history_ids(facts, all_rosters, ("high",)),
        all_rosters, "median",
    ))
    out.append(make(
        "next_week", "Next Week",
        _with_prefix(facts, "NX.", "S.", "SOS.")
        + _history_ids(facts, [r for nx in c.next for r in (nx.a, nx.b)], ("streak", "trend")),
        all_rosters, "next_week",
    ))
    return out


def build_bundle(
    week: Week,
    news: Callable[[str], list[dict]] = fetch_news,
    history: History | None = None,
    trades: list[Trade] | None = None,
    nfl: NflverseWeek | None = None,
) -> Bundle:
    c = Context(week, news, history, trades, nfl)
    families = (
        week_facts(c), recent_add_facts(c), injured_facts(c), standings_facts(c), median_facts_sheet(c),
        matchup_fact_family(c), award_facts(c), pick_facts(c), next_facts(c),
        rank_facts(c), strength_facts(c), history_facts(c), player_trend_facts(c), trade_facts(c),
        drop_facts(c), injury_facts_nfl(c),
    )
    facts = {f.id: f for family in families for f in family}
    data = WeekData(
        season=week.season,
        week=week.week,
        dates=week_dates(week.season_start, week.week),
        publish_date=date.today().strftime("%a %b %-d, %Y"),
        teams=week.teams,
        matchups=c.mfacts,
        median=c.median,
        table=c.table,
        awards=c.awards,
        pick=c.pick,
        next=c.next,
        history=c.season_history,
        ranks=c.ranks,
        trades=trades if trades is not None else [],
        drops=c.drops,
        drop_source=("nflverse" if c.nfl_up else "sleeper") if c.drops else "none",
    )
    return Bundle(data=data, sheet=FactSheet(facts=facts, chapters=chapters(c, facts)))


def write_bundle(b: Bundle, path: Path) -> None:
    path.write_text(b.model_dump_json(indent=2), encoding="utf-8")


def read_bundle(path: Path) -> Bundle:
    return Bundle.model_validate_json(path.read_text(encoding="utf-8"))
