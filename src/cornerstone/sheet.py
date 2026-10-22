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
    position_leaders,
    position_ranks,
    ranks_before,
    season_history,
    season_records,
    standings,
)
from cornerstone.facts_matchup import matchup_facts, median_facts
from cornerstone.facts_nflverse import drop_lines
from cornerstone.history import player_trend, points_per_game, red_zone, season_rank, snap_share, target_share
from cornerstone.models import (
    Bundle,
    Chapter,
    ChartValues,
    DropLine,
    Fact,
    FactSheet,
    History,
    NflverseWeek,
    PlayerLine,
    PowerRow,
    Standing,
    Trade,
    UsageShare,
    Week,
    WeekData,
    r2,
    sub,
)
from cornerstone.power_rankings import power_rankings
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
}
# (min, max) sentences per chapter, from the spec.
SENTENCE_RANGES = {
    "motw": (4, 6),
    "game_changer": (3, 5),
    "awards": (2, 4),
    "position_leaders": (2, 4),
    "recap": (2, 3),
    "median": (2, 4),
    "next_week": (1, 2),
    # One or two sentences for each of the 12 teams.
    "rankings": (12, 24),
}
RANKINGS_CHAPTER = "rankings"
COMPONENT_WORDS = {
    "standing": "standing", "form": f"the last {TREND_WEEKS} weeks", "schedule_played": "schedule played",
    "scoring": "scoring",
}
# The phrase for a team with the wins of the last playoff spot, keyed by its place against that spot.
# A team below it fills in its spots below the last playoff spot as a word, such as "two spots".
CUT_PHRASES = {
    "above": "level with the last playoff spot",
    "at": "in the last playoff spot",
    "below": "{spots} outside the playoff spots",
}
# The verifier lets a number word through only when a cited fact holds it, so the fact spells the spots out.
SPOT_WORDS = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven")
# The chapters about one or two teams, plus every recap_ chapter. Only these get the hard check on a
# repeated team name: the 12-team chapters, such as awards and median, name many teams, and "they" is
# unclear there.
TWO_TEAM_CHAPTERS = ("motw", "game_changer")


def two_team_chapter(key: str) -> bool:
    return key in TWO_TEAM_CHAPTERS or key.startswith("recap_")


def is_motw_recap(chapter: Chapter, sheet: FactSheet) -> bool:
    """True for the recap of the Matchup of the Week pairing.

    Both chapters hold the same matchup facts, so the writer repeats a sentence word for word.
    The check reads the two scopes, so it works on a saved sheet with no rebuild.
    """
    motw = next((c for c in sheet.chapters if c.key == "motw"), None)
    return (motw is not None and chapter.key.startswith("recap_")
            and set(chapter.scope_teams) == set(motw.scope_teams))


def is_game_changer_in_motw(sheet: FactSheet) -> bool:
    """True when the Game Changer plays for a team of the Matchup of the Week.

    The AW.game_changer fact names the team, so the check works on a saved sheet with no rebuild.
    """
    motw = next((c for c in sheet.chapters if c.key == "motw"), None)
    changer = sheet.facts.get("AW.game_changer")
    return motw is not None and changer is not None and bool(set(changer.teams) & set(motw.scope_teams))


def repeats_motw_headline(chapter: Chapter, sheet: FactSheet) -> bool:
    """True for the Matchup of the Week recap, and for game changer and awards when the Game Changer plays in it.

    The game changer or awards chapter then names the same game, so the writer repeats lines such as
    "without X, that is a loss".
    Outside the Matchup of the Week, the note would name a chapter that never told this game.
    """
    if is_motw_recap(chapter, sheet):
        return True
    return chapter.key in ("game_changer", "awards") and is_game_changer_in_motw(sheet)


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


def fact(fid: str, text: str, n: Nums, teams: list[str], players: list[str]) -> Fact:
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
        chart: ChartValues | None = None,
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
        self.chart = chart
        self.nfl_up = nfl is not None and nfl.drops is not None
        self.awards = awards(week, self.mfacts)
        self.next = next_week(week, self.table)
        self.season_history = season_history(week, history)
        # A gap in the history would shift every rank, so an incomplete history gives no power rankings.
        self.power = (
            power_rankings(history, week.week)[week.week] if history is not None and history.complete() else []
        )
        self.ranks = position_ranks(week)
        self.leaders = position_leaders(week)
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
        fact("W.week", week_text, n, [], []),
        fact("W.publish", publish, n2, [], []),
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
    return [fact("W.adds", text, n, teams, [line.name for line, _ in top])]


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
    return [fact("W.injured", text, Nums(), teams, [line.name for line, _ in found])]


def cut_phrase(rank: int, last_spot: int) -> str:
    """The fixed phrase for a team with the wins of the last playoff spot, from its rank."""
    if rank < last_spot:
        return CUT_PHRASES["above"]
    if rank == last_spot:
        return CUT_PHRASES["at"]
    distance = rank - last_spot
    word = SPOT_WORDS[distance - 1]
    spots = f"{word} spot" if distance == 1 else f"{word} spots"
    return CUT_PHRASES["below"].format(spots=spots)


def standings_facts(c: Context) -> list[Fact]:
    out = []
    last_spot = max((s.rank for s in c.table if s.in_playoffs), default=0)
    for s in c.table:
        n = Nums()
        cut = "in" if s.in_playoffs else "out of"
        side = "above" if s.games_from_cut > 0 else "below" if s.games_from_cut < 0 else "at"
        team = c.team(s.roster_id)
        gap = abs(s.games_from_cut)
        games = "game" if gap == 1 else "games"
        # "0 games at the cut" lets the writer say "still on the outside" for one tied team and "right at the cut"
        # for the next, and a reader sees a contradiction. One fixed phrase per spot keeps every chapter on one wording.
        if s.games_from_cut == 0:
            place = cut_phrase(s.rank, last_spot)
        else:
            place = f"{cut} the playoff spots, {n(gap)} {games} {side} the cut"
        text = (
            f"{team} is {n.ord(s.rank)} with a {n.record(s.wins, s.losses)} record "
            f"and {n(s.points_for)} points for, {place}."
        )
        out.append(fact(f"S.{s.rank}", text, n, [team], []))
    return out


def median_facts_sheet(c: Context) -> list[Fact]:
    m = c.median
    n = Nums()
    out = [fact("MED.value", f"The league median this week was {n(m.median)}.", n, [], [])]
    # Gaps use the exact median, as median_facts does, so a rounded median never shifts a gap.
    ordered = sorted(c.scores.values(), reverse=True)
    exact = (Decimal(str(ordered[5])) + Decimal(str(ordered[6]))) / 2
    for kind, rosters, word in (("above", m.above, "above"), ("below", m.below, "below")):
        for rid in rosters:
            n = Nums()
            gap = r2(abs(float(Decimal(str(c.scores[rid])) - exact)))
            team = c.team(rid)
            text = f"{team} scored {n(c.scores[rid])}, {n(gap)} {word} the median."
            out.append(fact(f"MED.{kind}.{rid}", text, n, [team], []))
    n = Nums()
    (up_id, up_gap), (down_id, down_gap) = m.closest_above, m.closest_below
    text = (
        f"{c.team(up_id)} cleared the median by {n(up_gap)}. "
        f"{c.team(down_id)} missed it by {n(down_gap)}."
    )
    out.append(fact("MED.closest", text, n, [c.team(up_id), c.team(down_id)], []))
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
    out = [fact(f"{mid}.result", text, n, teams, [])]
    for rid, line in f.top_scorer.items():
        n = Nums()
        team = c.team(rid)
        text = f"{c.who(line)} was the top scorer for {team} with {n(line.points)}."
        out.append(fact(f"{mid}.top.{rid}", text, n, [team], [line.name]))
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
            out.append(fact(f"M{f.matchup_id}.starter.{side.roster_id}.{line.player_id}", text, n, [team], [line.name]))
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
        out.append(fact(f"{mid}.driver.{line.player_id}", text, n, [team], [line.name]))
    for line in f.swing:
        n = Nums()
        team = c.team(f.winner)
        text = f"{line.name} is a swing player for {team}: {n(line.points)} exceeded the margin of {n(f.margin)}."
        out.append(fact(f"{mid}.swing.{line.player_id}", text, n, [team], [line.name]))
    for bench, starter in f.bench_regret:
        n = Nums()
        team = c.team(f.loser)
        text = (
            f"{team} left {bench.name} ({n(bench.points)}) on the bench behind "
            f"{starter.name} ({n(starter.points)}); the swap would have flipped the result."
        )
        out.append(fact(f"{mid}.regret.{bench.player_id}", text, n, [team], [bench.name, starter.name]))
    for mv in f.recent_moves:
        n = Nums()
        line = c.lines[mv.player_id]
        team = c.team(mv.roster_id)
        text = (
            f"{line.name} is a recent add: {line.name} started for {team} after a "
            f"{MOVE_WORDS[mv.kind]} in week {n(mv.week)} "
            f"and {c.against_projection(line, n)}."
        )
        out.append(fact(f"{mid}.move.{mv.player_id}", text, n, [team], [line.name]))
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
            out.append(fact(f"M{f.matchup_id}.inj.{line.player_id}", text, Nums(), [team], [line.name]))
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
        out.append(fact(f"{mid}.upset", text, n, [w, l], []))
    n = Nums()
    parts = []
    for rid in (m.a.roster_id, m.b.roster_id):
        s = c.by_rank[rid]
        parts.append(f"{c.team(rid)} is now {n.record(s.wins, s.losses)} ({n.ord(s.rank)}).")
    teams = [c.team(m.a.roster_id), c.team(m.b.roster_id)]
    out.append(fact(f"{mid}.records", " ".join(parts), n, teams, []))
    return out


def award_facts(c: Context) -> list[Fact]:
    out = []
    for aw in c.awards:
        n = Nums()
        team = c.team(aw.roster_id)
        text = f"{AWARD_TITLES[aw.key]}: {c.who(aw.line)}, {team}. {n.text(aw.reason)}"
        if aw.skipped:
            text += f" Skipped: {', '.join(aw.skipped)}."
        out.append(fact(f"AW.{aw.key}", text, n, [team], [aw.line.name, *aw.skipped]))
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
    return [fact("AW.game_changer.news", text, n, [], [gc.line.name])]


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
    return out



def rank_facts(c: Context) -> list[Fact]:
    out = []
    for r in c.ranks:
        n = Nums()
        line = c.lines[r.player_id]
        team = c.team(c.line_owner[r.player_id])
        text = f"{line.name} ranked {n(r.rank)} of {n(r.of)} among started {r.position}s this week, for {team}."
        out.append(fact(f"RANK.{r.player_id}", text, n, [team], [line.name]))
    return out


def leader_facts(c: Context) -> list[Fact]:
    out = []
    for lead in c.leaders:
        n = Nums()
        line = lead.line
        team = c.team(lead.roster_id)
        text = (
            f"{c.who(line)} scored {n(line.points)} for {team}, "
            f"{n.ord(lead.rank)} of {n(lead.of)} among started {lead.position}s this week."
        )
        out.append(fact(f"LEAD.{lead.position}.{lead.rank}", text, n, [team], [line.name]))
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
        out.append(fact(f"SOS.{s.roster_id}", text, n, [team], []))
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
            out.append(fact(f"H.{rid}.streak", f"{team} has {verb} {n(abs(h.streak))} straight.", n, [team], []))
        if h.trend is not None and r2(h.trend) != r2(h.average):
            n = Nums()
            side = "up" if h.trend > h.average else "down"
            text = (
                f"{team} has scored {n(h.trend)} per week over the last {n(TREND_WEEKS)} weeks, "
                f"{side} from a season average of {n(h.average)}."
            )
            out.append(fact(f"H.{rid}.trend", text, n, [team], []))
        # Week 1 has no earlier week, so no score there is a high or a low.
        if c.week.week > 1 and (h.new_high or h.new_low):
            n = Nums()
            kind = "high" if h.new_high else "low"
            text = f"{team}'s {n(c.scores[rid])} this week is a season {kind}."
            out.append(fact(f"H.{rid}.high", text, n, [team], []))
        n = Nums()
        out.append(fact(f"H.{rid}.avg", f"{team} averages {n(h.average)} per week this season.", n, [team], []))
    return out


def power_facts(rows: list[PowerRow], team: Callable[[int], str]) -> list[Fact]:
    """One fact per team: the power rank, the movement, and the four component ranks, as ordinals.

    It takes the rows and a name lookup, not a Context, so a saved week can get the facts from its history.
    """
    out = []
    for row in rows:
        n = Nums()
        name = team(row.roster_id)
        rank = n.ord(row.power_rank)
        if row.movement is None:
            move = "the first week of the power rankings"
        elif row.movement == 0:
            move = "no move from last week"
        else:
            places = "place" if abs(row.movement) == 1 else "places"
            side = "up" if row.movement > 0 else "down"
            move = f"{side} {n(abs(row.movement))} {places} from last week"
        # A component word may hold a number, such as the 3 of "the last 3 weeks", so Nums records it too.
        components = ", ".join(
            f"{n.ord(row.ranks[key])} in {n.text(word)}" for key, word in COMPONENT_WORDS.items()
        )
        text = f"{name} is {rank} in the power rankings, {move}: {components}."
        out.append(fact(f"PR.{row.roster_id}", text, n, [name], []))
    return out


def standing_ranks(table: list[Standing]) -> dict[int, int]:
    """The standing rank of each roster, by roster ID. The sheet and a saved week both read it from here."""
    return {s.roster_id: s.rank for s in table}


def rankings_chapter(
    facts: dict[str, Fact], rows: list[PowerRow], team: Callable[[int], str], standing_rank: dict[int, int],
) -> Chapter:
    """The rankings chapter: every team in power rank order, each with its PR, standing, streak, and trend facts.

    The history cap does not apply here: the spec gives each of the 12 teams its own streak and trend facts.
    """
    ids = [
        fid
        for row in rows
        for fid in (f"PR.{row.roster_id}", f"S.{standing_rank[row.roster_id]}",
                    f"H.{row.roster_id}.streak", f"H.{row.roster_id}.trend")
    ]
    low, high = SENTENCE_RANGES[RANKINGS_CHAPTER]
    return Chapter(
        key=RANKINGS_CHAPTER,
        title="Power rankings",
        fact_ids=[fid for fid in ids if fid in facts],
        scope_teams=[team(row.roster_id) for row in rows],
        # No fact in the chapter names a player, so a player name in the blurb is an unsupported claim.
        scope_players=[],
        min_sentences=low,
        max_sentences=high,
    )


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
        out.append(fact(f"P.{pid}.trend", _trend_text(line.name, beaten, n), n, [], [line.name]))
    return out


def _join(items: list[str]) -> str:
    """A, A and B, or A, B and C."""
    if len(items) < 2:
        return "".join(items)
    return f"{', '.join(items[:-1])} and {items[-1]}"


def _got_with_lines(c: Context, trade: Trade, rid: int) -> list[str]:
    """The player IDs a roster got that have a line this week."""
    return [pid for pid in _moved(trade, rid, True) if pid in c.lines]


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
    return fact(f"T{i}.sides", text, n, [c.team(r) for r in ids], players)


def _pregame_text(c: Context, pid: str) -> str | None:
    """The final NFL injury report status of this week, or None when the player has none."""
    if c.nfl is None or c.nfl.injuries is None:
        return None
    status = c.nfl.injuries.get(pid, {}).get(c.week.week)
    if status is None:
        return None
    return f"{c.lines[pid].name} was listed {status} on the final NFL injury report before his game this week."


def _player_trade_fact(c: Context, i: int, rid: int, pid: str, verb: str) -> Fact:
    """The points per game of a traded player and his position rank, from weeks 1 to N-1 only."""
    n = Nums()
    line = c.lines[pid]
    team = c.team(rid)
    through = c.week.week - 1
    # Without a history there is nothing before the trade to cite, so the fact only names the move.
    profile = points_per_game(c.history, pid, through) if c.history is not None else None
    if profile is None:
        text = f"{team} {verb} {line.name}."
    elif profile[1] == 0:
        text = f"{team} {verb} {line.name}: no scored game before the trade."
    else:
        text = (
            f"{team} {verb} {line.name}: {n(profile[0])} points per game over {n(profile[1])} "
            f"{'game' if profile[1] == 1 else 'games'} before the trade"
        )
        rank = season_rank(c.history, pid, through)
        if rank is not None:
            text += f", position rank {n(rank[0])} of {n(rank[1])} by season points"
        text += "."
    beaten = player_trend(c.history, pid, through=through) if c.history is not None else None
    if beaten is not None:
        text += " " + _trend_text(line.name, beaten, n)
    return fact(f"T{i}.{rid}.{verb}.{pid}", text, n, [team], [line.name])


def _team_fact(c: Context, i: int, rid: int) -> Fact | None:
    """The record and rank of the roster before the trade. A missing or partial history gives none."""
    through = c.week.week - 1
    if c.history is None or not c.history.complete() or through < 1:
        return None
    n = Nums()
    team = c.team(rid)
    wins, losses, _ = season_records(c.history, through)[rid]
    text = f"{team} was {n.record(wins, losses)}, {n.ord(c.before[rid])} of {n(12)}, before the trade."
    return fact(f"T{i}.{rid}.team", text, n, [team], [])


def _need_fact(c: Context, i: int, trade: Trade, rid: int) -> Fact:
    n = Nums()
    team = c.team(rid)
    side = next(s for m in c.week.matchups for s in (m.a, m.b) if s.roster_id == rid)
    positions = sorted({c.lines[pid].position for pid in (*trade.adds, *trade.drops) if pid in c.lines})
    depth = [f"{n(sum(l.position == pos for l in side.lines))} {pos}" for pos in positions]
    spots = max(0, c.week.roster_slots - len(side.lines))
    text = (
        f"{team} has {_join(depth)} after the trade and "
        f"{n(spots)} open roster {'spot' if spots == 1 else 'spots'}."
    )
    return fact(f"T{i}.{rid}.need", text, n, [team], [])


def _impact_fact(c: Context, i: int, trade: Trade, rid: int, pid: str) -> Fact | None:
    """What a player that the roster got scored this week, for the team that held him in the lineup."""
    # A later trade can move him on. Only a roster of this trade is in the scope of the chapter.
    owner = c.line_owner.get(pid)
    if owner not in trade.roster_ids:
        return None
    n = Nums()
    line = c.lines[pid]
    team = c.team(owner)
    where = "for" if line.started else "on the bench for"
    text = f"{line.name} scored {n(line.points)} this week {where} {team}."
    return fact(f"T{i}.{rid}.impact.{pid}", text, n, [team], [line.name])


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
    # A tie is neither a win nor a loss, and any gap would change it. No "decisive" or
    # "not enough" sentence is true for a tie, so a tied matchup gets no swing fact.
    if f.winner is None:
        return None
    # The trade decided the game only when it points the same way as the result: the winner gained
    # at least the margin, or the loser lost at least the margin.
    toward = float(x - y) if rid == f.winner else float(y - x)
    team = c.team(rid)
    others = [r for r in trade.roster_ids if r != rid]
    partners = c.team(others[0]) if len(others) == 1 else "its trade partners"
    text = (
        f"The players {team} got and started scored {n(float(x))} this week; "
        f"the players it gave that {partners} started scored {n(float(y))}. "
    )
    if r2(toward) >= r2(f.margin):
        side = "above" if r2(toward) > r2(f.margin) else "equal to"
        text += f"The gap is {n(toward)}, {side} the margin of {n(f.margin)} in its matchup."
    else:
        text += (
            f"In its matchup, that is a gap of {n(abs(float(x - y)))} against a margin of {n(f.margin)}, "
            "not enough to change the result."
        )
    teams = [team, *(c.team(r) for r in others)] if len(others) == 1 else [team]
    return fact(f"T{i}.{rid}.swing", text, n, teams, [l.name for l in (*got_started, *gave_started)])


def _share_fact(c: Context, i: int, pid: str, kind: str, share: UsageShare | None) -> Fact | None:
    """The snap share or target share of a player before the trade. `kind` is the fact ID suffix."""
    if share is None:
        return None
    n = Nums()
    name = c.lines[pid].name
    label = "snap share" if kind == "usage" else "target share"
    if share.direction is None:
        games = f"{n(share.weeks)} {'game' if share.weeks == 1 else 'games'}"
        text = f"{name}'s {label} was {n(share.percent)} percent over {games} before the trade."
    else:
        text = (
            f"{name}'s {label} was {n(share.percent)} percent over the last {n(2)} weeks before the trade, "
            f"{share.direction} from the {n(2)} weeks before that."
        )
    return fact(f"T{i}.{pid}.{kind}", text, n, [], [name])


def _redzone_fact(c: Context, i: int, pid: str, through: int) -> Fact | None:
    """The red-zone targets and carries of a player from week 1 to N-1."""
    zone = red_zone(c.history, pid, through)
    if zone is None:
        return None
    n = Nums()
    name = c.lines[pid].name
    targets, carries = zone
    text = (
        f"{name} had {n(targets)} red-zone {'target' if targets == 1 else 'targets'} and "
        f"{n(carries)} red-zone {'carry' if carries == 1 else 'carries'} this season before the trade."
    )
    return fact(f"T{i}.{pid}.redzone", text, n, [], [name])


def _injury_fact(c: Context, i: int, pid: str, through: int) -> Fact | None:
    """The NFL injury report of a player in weeks 1 to N-1. A week N entry is after the trade and never counts."""
    if c.nfl is None or c.nfl.injuries is None:
        return None
    reports = {w: status for w, status in c.nfl.injuries.get(pid, {}).items() if w <= through}
    if not reports:
        return None
    n = Nums()
    name = c.lines[pid].name
    count = _weeks(len(reports), n)
    if through in reports:
        text = (
            f"{name} was listed {reports[through]} on the NFL injury report in week {n(through)}, "
            f"and in {count} this season before the trade."
        )
    else:
        text = f"{name} was on the NFL injury report in {count} this season before the trade."
    return fact(f"T{i}.{pid}.injury", text, n, [], [name])


def _usage_facts(c: Context, i: int, trade: Trade) -> list[Fact]:
    """The usage, red-zone, and injury facts of each moved player with a line this week, from weeks 1 to N-1."""
    through = c.week.week - 1
    out = []
    for pid in dict.fromkeys((*trade.adds, *trade.drops)):
        if pid not in c.lines:
            continue
        position = c.lines[pid].position
        if c.history is not None:
            out.append(_share_fact(c, i, pid, "usage", snap_share(c.history, pid, through)))
            if position in ("RB", "WR", "TE"):
                out.append(_share_fact(c, i, pid, "targets", target_share(c.history, pid, through)))
            if position in ("QB", "RB", "WR", "TE"):
                out.append(_redzone_fact(c, i, pid, through))
        out.append(_injury_fact(c, i, pid, through))
    return [f for f in out if f is not None]


def _value_facts(c: Context, i: int, trade: Trade) -> list[Fact]:
    """The trade value of each moved player and the value each side gave and got. No facts without a chart."""
    if c.chart is None:
        return []
    values = c.chart.values
    # A player with no line has no name to cite, so he stays out of the sums and the unlisted names.
    moved = [pid for pid in dict.fromkeys((*trade.adds, *trade.drops)) if pid in c.lines]
    valued = [pid for pid in moved if pid in values]
    if not valued:
        return []
    out = []
    for pid in valued:
        n = Nums()
        name = c.lines[pid].name
        text = f"{name}'s trade value was {n(values[pid])} in the week of the trade."
        out.append(fact(f"T{i}.{pid}.value", text, n, [], [name]))
    unlisted = [c.lines[pid].name for pid in moved if pid not in values]
    for rid in trade.roster_ids:
        n = Nums()
        team = c.team(rid)

        def total(got: bool) -> float:
            # Decimal sums keep a half-point total exact.
            pids = [pid for pid in _moved(trade, rid, got) if pid in valued]
            return float(sum((Decimal(str(values[pid])) for pid in pids), Decimal(0)))

        text = f"{team} gave {n(total(False))} and got {n(total(True))} in trade value"
        if unlisted:
            text += f", with {_join(unlisted)} unlisted"
        if trade.draft_picks:
            text += "; the pick is not valued." if len(trade.draft_picks) == 1 else "; the picks are not valued."
        else:
            text += "."
        out.append(fact(f"T{i}.{rid}.value", text, n, [team], unlisted))
    return out


def _late_fact(c: Context, i: int, trade: Trade) -> Fact:
    """A late trade came after the lineups locked, so the points of its players went to the old rosters."""
    text = "The trade came after the lineups locked, so the lineups show the rosters from before it."
    return fact(f"T{i}.late", text, Nums(), [c.team(r) for r in trade.roster_ids], [])


def trade_facts(c: Context) -> list[Fact]:
    """The sides, impact, swing, and late facts of each trade, kept for the trade analyzer.
    The weekly sheet leaves them out, because the page shows the trade card with no recap."""
    out = []
    for i, trade in enumerate(c.trades, start=1):
        out.append(_sides_fact(c, i, trade))
        for rid in trade.roster_ids:
            got = _got_with_lines(c, trade, rid)
            out += [f for f in (_impact_fact(c, i, trade, rid, pid) for pid in got) if f is not None]
        if is_late(trade, c.week):
            out.append(_late_fact(c, i, trade))
            continue
        for rid in trade.roster_ids:
            swing = _swing_fact(c, i, trade, rid)
            if swing is not None:
                out.append(swing)
    return out


def grade_input_facts(c: Context) -> list[Fact]:
    """The grade inputs of each trade. The trade analyzer uses them; the weekly sheet does not.

    They are the got and gave profiles, the team record, the usage, injury, and value facts, and the need.
    """
    out = []
    for i, trade in enumerate(c.trades, start=1):
        for rid in trade.roster_ids:
            got = _got_with_lines(c, trade, rid)
            out += [_player_trade_fact(c, i, rid, pid, "got") for pid in got]
            out += [_player_trade_fact(c, i, rid, pid, "gave") for pid in _moved(trade, rid, False) if pid in c.lines]
            team = _team_fact(c, i, rid)
            if team is not None:
                out.append(team)
        out += _usage_facts(c, i, trade)
        # The chart is for the week of the trade, so late trades keep their value facts.
        out += _value_facts(c, i, trade)
        # A late trade happened after the lineups locked, so the lineup shows the roster from before it.
        if is_late(trade, c.week):
            continue
        for rid in trade.roster_ids:
            out.append(_need_fact(c, i, trade, rid))
    return out


def _drop_fact(c: Context, d: DropLine) -> list[Fact]:
    line, team = c.lines[d.player_id], c.team(d.roster_id)
    n = Nums()
    if d.targets is None:
        text = f"{line.name} dropped {_passes(d.drops, n)} this week."
    else:
        text = f"{line.name} dropped {n(d.drops)} of {n(d.targets)} targets this week."
    out = [fact(f"D.{d.player_id}", text, n, [team], [line.name])]
    if d.value is not None:
        n = Nums()
        text = (
            f"{line.name}'s drops were worth about {n(d.value)} points by the drop value method, "
            f"with {n(d.end_zone)} in the end zone."
        )
        out.append(fact(f"D.{d.player_id}.value", text, n, [team], [line.name]))
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
            f"{team}'s starters dropped {_passes(sum(d.drops for d in lost), n)} worth about "
            f"{n(float(value))}, at least the margin of {n(f.margin)}."
        )
        out.append(fact(f"M{f.matchup_id}.dropswing", text, n, [team], [c.lines[d.player_id].name for d in lost]))
    return out


def drop_facts(c: Context) -> list[Fact]:
    out = [fact for d in c.drops for fact in _drop_fact(c, d)]
    out += _dropswing_facts(c)
    if c.drops:
        n = Nums()
        top = c.drops[:3]
        parts = [
            f"{c.lines[d.player_id].name} ({c.team(d.roster_id)}), {n(d.drops)} {'drop' if d.drops == 1 else 'drops'}"
            for d in top
        ]
        out.append(fact("W.drops", "Most drops this week: " + "; ".join(parts) + ".", n,
                         [c.team(d.roster_id) for d in top], [c.lines[d.player_id].name for d in top]))
    return out


def _passes(count: int, n: Nums) -> str:
    return f"{n(count)} pass" + ("" if count == 1 else "es")


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
            out.append(fact(f"I.{pid}.pregame", pregame, Nums(), team, [line.name]))
        n = Nums()
        if week in weeks:
            text = f"{line.name} has been on the NFL injury report {_weeks(sum(w <= week for w in weeks), n)}."
        # A return claim needs proof of play: nflverse only lists the injured, so a gap alone is not a return.
        elif week - 1 in weeks and c.week.stats.get(pid, {}).get("gp", 0) > 0:
            earlier = _weeks(sum(w < week for w in weeks), n, "earlier ")
            text = f"{line.name} was on the NFL injury report in {earlier} this season and plays this week."
        else:
            continue
        out.append(fact(f"I.{pid}.history", text, n, team, [line.name]))
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

    def make(key, title, ids, rosters, rng, players=None) -> Chapter:
        return Chapter(
            key=key,
            title=title,
            fact_ids=_dedupe([i for i in ids if i in facts]),
            scope_teams=[c.team(r) for r in rosters],
            scope_players=_dedupe(players_of(rosters) if players is None else players),
            min_sentences=SENTENCE_RANGES[rng][0],
            max_sentences=SENTENCE_RANGES[rng][1],
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
    out.append(make(
        "position_leaders", "Position Leaders",
        _with_prefix(facts, "LEAD."),
        all_rosters, "position_leaders",
        players=[l.line.name for l in c.leaders],
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
    if c.power:
        out.append(rankings_chapter(facts, c.power, c.team, standing_ranks(c.table)))
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
        rank_facts(c), leader_facts(c), strength_facts(c), history_facts(c), player_trend_facts(c),
        drop_facts(c), injury_facts_nfl(c), power_facts(c.power, c.team),
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
        leaders=c.leaders,
        trades=trades if trades is not None else [],
        trade_players={pid: c.lines[pid].name for t in c.trades for pid in t.adds if pid in c.lines},
        drops=c.drops,
        drop_source=("nflverse" if c.nfl_up else "sleeper") if c.drops else "none",
    )
    return Bundle(data=data, sheet=FactSheet(facts=facts, chapters=chapters(c, facts)))


def write_bundle(b: Bundle, path: Path) -> None:
    path.write_text(b.model_dump_json(indent=2), encoding="utf-8")


def read_bundle(path: Path) -> Bundle:
    return Bundle.model_validate_json(path.read_text(encoding="utf-8"))
