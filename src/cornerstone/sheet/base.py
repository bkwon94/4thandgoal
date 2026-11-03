"""
The shared parts of the fact sheet: the number tokens, Nums, fact, Context and the odds it builds, the chapter
tests, the week gate, and the text helpers that two chapters share. Modules outside the sheet import from here.
"""
import logging
import re
from collections.abc import Callable
from datetime import date, timedelta

from cornerstone.adjusters import allowed_positions, fill_slots
from cornerstone.config import LeagueConfig
from cornerstone.facts_league import (
    awards,
    matchup_of_the_week,
    next_week,
    position_leaders,
    position_ranks,
    ranks_before,
    season_history,
)
from cornerstone.facts_matchup import matchup_facts, median_facts
from cornerstone.facts_nflverse import drop_lines
from cornerstone.models import (
    Chapter,
    ChartValues,
    Fact,
    FactSheet,
    History,
    NflverseWeek,
    OddsResult,
    PlayerLine,
    Trade,
    Week,
    sub,
)
from cornerstone.numbers import ordinal, r2
from cornerstone.odds import playoff_odds
from cornerstone.power_rankings import power_rankings
from cornerstone.snapshot import Snapshot
from cornerstone.standings_table import season_records, standings
from cornerstone.tunables import TREND_WEEKS

logger = logging.getLogger(__name__)

FIRST_WEEK = 6
# The first week whose sheet holds the odds facts. Week 6 is the first week the tool builds. Its 6 scores
# per team are the fewest scores the engine reads for a team level. A week before it gets no odds.
ODDS_FROM_WEEK = 6
MOVE_WORDS = {"waiver": "waiver add", "free_agent": "free agent add", "trade": "trade"}
AWARD_TITLES = {
    "game_changer": "Game Changer",
    "top_scorer": "Top Scorer",
    "mvb": "MVB",
    "underperformer": "Underperformer",
    "overachiever": "Overachiever",
    "unlucky": "Unlucky",
    "lucky": "Lucky",
}
# The id prefix of every bye fact. GLOSSARY.md, "Bye line". The writer reads it to add the bye note.
BYE_FACT_PREFIX = "NX.bye."
# (min, max) sentences per chapter, from the spec.
SENTENCE_RANGES = {
    "motw": (4, 6),
    "game_changer": (3, 5),
    "awards": (2, 4),
    "position_leaders": (2, 4),
    "recap": (2, 3),
    "median": (2, 4),
    # The third sentence leaves room for the swing of the Must Watch games. The byes next week need up to three more.
    "next_week": (2, 6),
}
RANKINGS_CHAPTER = "rankings"
# The chapters about one or two teams, plus every recap_ chapter. Only these get the hard check on a
# repeated team name: the chapters about every team, such as awards and median, name many teams, and "they" is
# unclear there.
TWO_TEAM_CHAPTERS = ("motw", "game_changer")


def sentence_range(key: str, config: LeagueConfig) -> tuple[int, int]:
    """The (min, max) sentences of the chapter `key`. The rankings range follows the team count of `config`."""
    if key == RANKINGS_CHAPTER:
        # One to three sentences for each team.
        return config.team_count, 3 * config.team_count
    return SENTENCE_RANGES[key]


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


def fmt(x: float) -> str:
    """Shortest two-decimal form: 106.8 for 106.80, 21 for 21.0."""
    return f"{r2(x):.2f}".rstrip("0").rstrip(".")


def week_dates(season_start: date, week: int) -> str:
    thursday = season_start + timedelta(days=1 + 7 * (week - 1))
    monday = thursday + timedelta(days=4)
    return f"{thursday.strftime('%b %-d')} – {monday.strftime('%b %-d, %Y')}"


def check_week_is_buildable(week_target: int, last_scored: int, config: LeagueConfig) -> str | None:
    # Playoff comes first: a playoff week is never buildable, scored or not.
    last = config.last_regular_week
    if week_target > last:
        return f"Week {week_target} is a playoff week. Version 1 covers weeks {FIRST_WEEK} to {last}."
    if last_scored < week_target:
        return f"Sleeper has scored through week {last_scored}. Week {week_target} is not final."
    return None


class Nums:
    """Formats values for fact text and records each one, so `numbers` is exact."""

    def __init__(self) -> None:
        self.seen: list[str] = []

    def __call__(self, x: float) -> str:
        s = str(x) if isinstance(x, int) else fmt(x)
        self.seen.append(s)
        return s

    def ord(self, n: int) -> str:
        self.seen.append(str(n))
        return ordinal(n)

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


def week_odds(
    week: Week, history: History | None,
    inputs: tuple[dict[int, list[float]], dict[int, list[tuple[int, int]]]] | None,
    projected: dict[int, dict[int, float]] | None,
    config: LeagueConfig,
) -> OddsResult | None:
    """The engine's odds after this week, or None when `odds_inputs` gave no inputs.

    The engine runs once per build here, and the odds reach the saved facts, so a rewrite never runs it.
    """
    if inputs is None or history is None:
        return None
    scores, remaining = inputs
    return playoff_odds(
        scores, season_records(history, week.week), remaining, season=week.season, week=week.week,
        config=config, projected=projected,
    )


def odds_inputs(
    week: Week, history: History | None, config: LeagueConfig,
) -> tuple[dict[int, list[float]], dict[int, list[tuple[int, int]]]] | None:
    """The season scores and the remaining pairs the engine takes, or None where the sheet gives no odds."""
    if week.week < ODDS_FROM_WEEK or history is None or not history.complete():
        return None
    # A roster with no score in a week, such as a bye, adds no score for that week.
    scores = {
        rid: [history.weeks[n].scores[rid] for n in range(1, week.week + 1) if rid in history.weeks[n].scores]
        for rid in week.teams
    }
    # The engine reads the first remaining week as week N+1. After the last regular week, the next pairs are
    # playoff games, and the engine stops at the seeds, so they stay out.
    remaining = {week.week + 1: week.next_matchups} if week.week < config.last_regular_week else {}
    remaining.update(week.schedule)
    # A cached week can lack the schedule file. The engine would then end the season early and could
    # call a team clinched or out by mistake, so the sheet gives no odds.
    if set(remaining) != set(range(week.week + 1, config.last_regular_week + 1)):
        logger.warning("week %d has no full remaining schedule: no odds facts", week.week)
        return None
    return scores, remaining


def projected_totals(week: Week, config: LeagueConfig) -> dict[int, dict[int, float]]:
    """The projected total of each roster's best lineup in each week ahead, by roster ID and week.

    The roster is the current roster in rosters.json. The lineup picks by that week's projections, so a player
    with no projection that week counts 0 and a healthy bench player takes his slot.
    An injured starter at zero gives his slot to the best free agent at the slot's positions, so the shift measures
    the real roster, not a hole.
    A roster with no projected player in a week has no total that week.
    A missing week gives the roster no shift. It does not count as a total of 0.
    The weeks stop at the last regular week of `config`, because the file runs to the end of the NFL season for the
    waiver board.
    A playoff week in the totals would move the projected pace of the odds why.
    """
    totals: dict[int, dict[int, float]] = {rid: {} for rid in week.rosters}
    for w, projections in sorted(week.projections_ahead.items()):
        if w > config.last_regular_week:
            continue
        # The free agents with a projection above zero that week, best first, with the player id as the tie rule.
        pool = sorted(
            ((pid, projections[pid]) for pid in week.free_agents if projections.get(pid, 0.0) > 0),
            key=lambda item: (-item[1], item[0]),
        )
        for rid, positions in week.rosters.items():
            if not any(pid in projections for pid in positions):
                continue
            points = {pid: projections.get(pid, 0.0) for pid in positions}
            slots = fill_slots(list(points), week.roster_positions, positions, points)
            starters = [pid for _, pid in slots if pid is not None]
            totals[rid][w] = sum(points[pid] for pid in starters) + _injury_cover(week, slots, points, pool)
    return totals


def _injury_cover(
    week: Week, slots: list[tuple[str, str | None]], points: dict[str, float], pool: list[tuple[str, float]],
) -> float:
    """The points the free agents add to one roster's best lineup in one week, in place of its injured starters.

    An injured starter is a starter at zero with an injury status. His slot takes the best free agent at the slot's
    positions that no other slot of the roster took. A flex slot takes any of its positions.
    """
    added = 0.0
    taken: set[str] = set()
    for slot, pid in slots:
        # A healthy starter at zero has a bye or no game that week. Every roster takes its byes in turn, so the zero
        # is part of the real roster, not a hole from an injury.
        if pid is None or points[pid] or pid not in week.injuries:
            continue
        # The best lineup fills each slot with the best player left at its positions, so no bench player at the
        # slot's positions projects above zero. Only a free agent can be the better of the bench and the waivers.
        allowed = allowed_positions(slot)
        cover = next(((fa, value) for fa, value in pool if fa not in taken and week.free_agents[fa] in allowed), None)
        if cover is not None:
            taken.add(cover[0])
            added += cover[1]
    return added


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
        snapshot: Snapshot | None = None,
        today: date | None = None,
        *,
        config: LeagueConfig,
    ) -> None:
        self.week = week
        # The chapter list and the rankings chapter take only the context, so they read the team count from it.
        self.config = config
        # The publish date is a parameter so a build is reproducible. None reads the clock.
        self.today = today or date.today()
        self.history = history
        self.trades = trades if trades is not None else []
        self.news = news
        # The week before is in the history, so a recent add of that week shows in this week.
        self.moves = list(week.moves)
        if history is not None and week.week - 1 in history.weeks:
            self.moves += history.weeks[week.week - 1].moves
        self.mfacts = [matchup_facts(m, self.moves, week.week) for m in week.matchups]
        self.table = standings(week, history, config=config)
        self.by_rank = {s.roster_id: s for s in self.table}
        self.before = ranks_before(week, self.table, history)
        self.median = median_facts(week)
        self.pick = matchup_of_the_week(week, self.mfacts, self.table, self.before, config=config)
        self.drops = drop_lines(week, nfl)
        self.nfl = nfl
        self.chart = chart
        # The bye facts read the position rank and the lineup value from it. None gives no rank and no bye cover.
        self.snapshot = snapshot
        self.nfl_up = nfl is not None and nfl.drops is not None
        self.awards = awards(week, self.mfacts)
        self.season_history = season_history(week, history)
        # A gap in the history would shift every rank, so an incomplete history gives no power rankings.
        self.power = (
            power_rankings(history, week.week)[week.week] if history is not None and history.complete() else []
        )
        # The odds and the odds why read the same inputs, so the context builds them once.
        self.projected = projected_totals(week, config)
        inputs = odds_inputs(week, history, config)
        self.season_scores, self.remaining = inputs if inputs is not None else ({}, {})
        self.odds = week_odds(week, history, inputs, self.projected, config)
        # The shootout storyline reads the same projected lineups as the odds.
        self.next = next_week(week, self.table, history, self.projected, nfl.bye_weeks if nfl is not None else None,
                              snapshot.position_rank if snapshot is not None else None, config=config)
        self.ranks = position_ranks(week)
        self.leaders = position_leaders(week)
        self.scores = {s.roster_id: s.points for m in week.matchups for s in (m.a, m.b)}
        self.line_owner = {
            line.player_id: s.roster_id
            for m in week.matchups for s in (m.a, m.b) for line in s.lines
        }
        self.lines = {
            line.player_id: line for m in week.matchups for s in (m.a, m.b) for line in s.lines
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


def trend_text(name: str, beaten: int, n: Nums) -> str:
    if beaten >= 2:
        return f"{name} has beaten projection in {n(beaten)} of the last {n(TREND_WEEKS)} weeks."
    return f"{name} has missed projection in {n(TREND_WEEKS - beaten)} of the last {n(TREND_WEEKS)} weeks."


def weeks_text(count: int, n: Nums, adjective: str = "") -> str:
    return f"{n(count)} {adjective}week" + ("" if count == 1 else "s")
