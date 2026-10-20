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
from cornerstone.models import (
    Bundle,
    Chapter,
    Fact,
    FactSheet,
    PlayerLine,
    Week,
    WeekData,
    r2,
    sub,
)
from cornerstone.sleeper import fetch_news

logger = logging.getLogger(__name__)

FIRST_WEEK = 6
LAST_WEEK = 14
NEWS_MAX_CHARS = 300
MOVE_WORDS = {"waiver": "waiver add", "free_agent": "free agent add", "trade": "trade"}
AWARD_TITLES = {
    "game_changer": "Game Changer",
    "top_scorer": "Top Scorer",
    "mvb": "MVB",
    "underperformer": "Underperformer",
    "overachiever": "Overachiever",
}
# (min, max) sentences per chapter, from the spec.
SENTENCE_RANGES = {
    "motw": (4, 6),
    "game_changer": (3, 5),
    "awards": (2, 4),
    "recap": (2, 3),
    "median": (2, 4),
    "next_week": (1, 2),
}
# A record such as 33-30 is one token. A leading minus belongs to a negative number.
NUMBER_TOKEN = re.compile(r"\d+-\d+|(?<!\d)-?\d+(?:\.\d+)?|\d+(?:\.\d+)?")
PART_TOKEN = re.compile(r"\d+(?:\.\d+)?")


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

    def __init__(self, week: Week, news: Callable[[str], list[dict]]) -> None:
        self.week = week
        self.news = news
        self.mfacts = [matchup_facts(m, week.moves, week.week) for m in week.matchups]
        self.table = standings(week)
        self.by_rank = {s.roster_id: s for s in self.table}
        self.before = ranks_before(week, self.table)
        self.median = median_facts(week)
        self.pick = matchup_of_the_week(week, self.mfacts, self.table)
        self.awards = awards(week, self.mfacts)
        self.next = next_week(week, self.table)
        self.history = season_history(week)
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


def standings_facts(c: Context) -> list[Fact]:
    out = []
    for s in c.table:
        n = Nums()
        cut = "in" if s.in_playoffs else "out of"
        side = "above" if s.games_from_cut > 0 else "below" if s.games_from_cut < 0 else "at"
        team = c.team(s.roster_id)
        text = (
            f"{team} is {n.ord(s.rank)} with a {n.record(s.wins, s.losses)} record "
            f"and {n(s.points_for)} points for, {cut} the playoff spots, "
            f"{n(abs(s.games_from_cut))} games {side} the cut."
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
            f"{line.name} started for {team} after a {MOVE_WORDS[mv.kind]} in week {n(mv.week)} "
            f"and {c.against_projection(line, n)}."
        )
        out.append(_fact(f"{mid}.move.{mv.player_id}", text, n, [team], [line.name]))
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
    except Exception:
        logger.exception("News fetch failed for %s", gc.line.name)
        return []
    # Items arrive in no promised order, and "published" is epoch milliseconds as a string.
    newest = max(items, key=lambda i: int(i.get("published") or 0), default={})
    description = (newest.get("metadata") or {}).get("description") or ""
    if not description:
        return []
    n = Nums()
    text = f"Latest news on {gc.line.name}: {n.text(description[:NEWS_MAX_CHARS])}"
    return [_fact("AW.game_changer.news", text, n, [], [gc.line.name])]


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


def history_facts(c: Context) -> list[Fact]:
    out = []
    for h in c.history:
        n = Nums()
        team = c.team(h.roster_id)
        text = (
            f"{team} scored {n(h.high)} this week, a season high so far, with "
            f"{n(h.weeks_over[100])} weeks over {n(100)}, {n(h.weeks_over[110])} over {n(110)}, "
            f"{n(h.weeks_over[120])} over {n(120)}."
        )
        out.append(_fact(f"HIST.{h.roster_id}", text, n, [team], []))
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
        text = (
            f"{team} has a remaining schedule strength of {n(s.schedule_strength)}, "
            f"ranked {n(s.strength_rank)} of {n(12)}."
        )
        out.append(_fact(f"SOS.{s.roster_id}", text, n, [team], []))
    return out


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

    def make(key, title, ids, rosters, rng) -> Chapter:
        return Chapter(
            key=key,
            title=title,
            fact_ids=_dedupe([i for i in ids if i in facts]),
            scope_teams=[c.team(r) for r in rosters],
            scope_players=players_of(rosters),
            min_sentences=SENTENCE_RANGES[rng][0],
            max_sentences=SENTENCE_RANGES[rng][1],
        )

    def standings_ids(rosters) -> list[str]:
        return [f"S.{c.by_rank[r].rank}" for r in rosters]

    out = []
    pair = roster_ids[c.pick.matchup_id]
    out.append(make(
        "motw", "Matchup of the Week",
        _with_prefix(facts, f"M{c.pick.matchup_id}.") + ["PICK"] + standings_ids(pair)
        + [f"HIST.{r}" for r in pair] + [f"RANK.{p}" for p in started_ids(pair)],
        pair, "motw",
    ))
    gc = next((a for a in c.awards if a.key == "game_changer"), None)
    if gc:
        pair = roster_ids[gc.matchup_id]
        out.append(make(
            "game_changer", "Game Changer",
            ["AW.game_changer", "AW.game_changer.news"] + _with_prefix(facts, f"M{gc.matchup_id}.")
            + [f"RANK.{gc.line.player_id}"],
            pair, "game_changer",
        ))
    out.append(make(
        "awards", "Awards",
        _with_prefix(facts, "AW.") + ["W.adds"] + [f"RANK.{a.line.player_id}" for a in c.awards]
        + [f"M{mid}.result" for mid in roster_ids],
        all_rosters, "awards",
    ))
    for mid, pair in roster_ids.items():
        title = " vs ".join(c.team(r) for r in pair)
        out.append(make(f"recap_{mid}", title, _with_prefix(facts, f"M{mid}.") + standings_ids(pair), pair, "recap"))
    out.append(make(
        "median", "The Median Game",
        _with_prefix(facts, "MED.") + _with_prefix(facts, "S."), all_rosters, "median",
    ))
    out.append(make(
        "next_week", "Next Week",
        _with_prefix(facts, "NX.", "S.", "SOS."), all_rosters, "next_week",
    ))
    return out


def build_bundle(week: Week, news: Callable[[str], list[dict]] = fetch_news) -> Bundle:
    c = Context(week, news)
    families = (
        week_facts(c), recent_add_facts(c), standings_facts(c), median_facts_sheet(c),
        matchup_fact_family(c), award_facts(c), pick_facts(c), next_facts(c),
        history_facts(c), rank_facts(c), strength_facts(c),
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
        history=c.history,
        ranks=c.ranks,
    )
    return Bundle(data=data, sheet=FactSheet(facts=facts, chapters=chapters(c, facts)))


def write_bundle(b: Bundle, path: Path) -> None:
    path.write_text(b.model_dump_json(indent=2), encoding="utf-8")


def read_bundle(path: Path) -> Bundle:
    return Bundle.model_validate_json(path.read_text(encoding="utf-8"))
