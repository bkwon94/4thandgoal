"""
The shared parts of the fact sheet: Context, the projected totals, the sentence ranges, the week gate, and the
text helpers that two chapters share. The fact tokens are in facts.tokens. Modules outside the sheet import from here.
"""
from collections.abc import Callable, Sequence
from datetime import date, timedelta

from facts.chapters import RANKINGS_CHAPTER
from facts.tokens import Nums
from league.client import Client
from league.lineup import allowed_positions, fill_slots
from league.models import (
    ChartValues,
    History,
    NflverseWeek,
    OddsResult,
    PlayerLine,
    Trade,
    Week,
    sub,
)
from league.snapshot import Snapshot
from league.standings_table import standings
from league.tunables import TREND_WEEKS
from week.facts_league import (
    awards,
    matchup_of_the_week,
    next_week,
    position_leaders,
    position_ranks,
    ranks_before,
    season_history,
)
from week.facts_matchup import matchup_facts, median_facts
from week.facts_nflverse import drop_lines
from week.sheet.port import ChapterSource

FIRST_WEEK = 6
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


def sentence_range(key: str, client: Client) -> tuple[int, int]:
    """The (min, max) sentences of the chapter `key`. The rankings range follows the team count of `client`."""
    if key == RANKINGS_CHAPTER:
        # One to three sentences for each team.
        return client.settings.team_count, 3 * client.settings.team_count
    return SENTENCE_RANGES[key]


def week_dates(season_start: date, week: int) -> str:
    thursday = season_start + timedelta(days=1 + 7 * (week - 1))
    monday = thursday + timedelta(days=4)
    return f"{thursday.strftime('%b %-d')} – {monday.strftime('%b %-d, %Y')}"


def check_week_is_buildable(week_target: int, last_scored: int, client: Client) -> str | None:
    # Playoff comes first: a playoff week is never buildable, scored or not.
    last = client.settings.last_regular_week
    if week_target > last:
        return f"Week {week_target} is a playoff week. Version 1 covers weeks {FIRST_WEEK} to {last}."
    if last_scored < week_target:
        return f"Sleeper has scored through week {last_scored}. Week {week_target} is not final."
    return None


def projected_totals(
    week: Week, client: Client, bye_weeks: dict[str, int] | None = None,
) -> dict[int, dict[int, float]]:
    """The projected total of each roster's best lineup in each week ahead, by roster ID and week.

    The roster is the current roster in rosters.json. The lineup picks by that week's projections, so a player
    with no projection that week counts 0 and a healthy bench player takes his slot.
    An injured starter at zero gives his slot to the best pool player at the slot's positions, so the shift measures
    the real roster, not a hole. `bye_weeks` is the bye week of each NFL team, and a bye week gives no cover.
    A roster with no projected player in a week has no total that week.
    A missing week gives the roster no shift. It does not count as a total of 0.
    The weeks stop at the last regular week of `client`, because the file runs to the end of the NFL season for the
    waiver board.
    A playoff week in the totals would move the projected pace of the odds why.
    """
    totals: dict[int, dict[int, float]] = {rid: {} for rid in week.rosters}
    for w, projections in sorted(week.projections_ahead.items()):
        if w > client.settings.last_regular_week:
            continue
        # The pool players with a projection above zero that week, best first, with the player id as the tie rule.
        pool = sorted(
            ((pid, projections[pid], position) for pid, position in week.pool.items() if projections.get(pid, 0.0) > 0),
            key=lambda item: (-item[1], item[0]),
        )
        # The injury status is one snapshot for every week ahead. A player on his bye would be at zero healthy too, so
        # his bye week is no hole from the injury. With no schedule, no bye is known, so every injury counts.
        on_bye = {pid for pid, (_, team) in week.roster_players.items() if team and (bye_weeks or {}).get(team) == w}
        injuries = {pid: status for pid, status in week.injuries.items() if pid not in on_bye}
        for rid, positions in week.rosters.items():
            if not any(pid in projections for pid in positions):
                continue
            points = {pid: projections.get(pid, 0.0) for pid in positions}
            slots = fill_slots(list(points), week.roster_positions, positions, points)
            starters = [pid for _, pid in slots if pid is not None]
            totals[rid][w] = sum(points[pid] for pid in starters) + _injury_cover(injuries, slots, points, pool)
    return totals


def _injury_cover(
    injuries: dict[str, str], slots: list[tuple[str, str | None]], points: dict[str, float],
    pool: list[tuple[str, float, str]],
) -> float:
    """The points the pool adds to one roster's best lineup in one week, in place of its injured starters.

    An injured starter is a starter at zero with an entry in `injuries`. His slot takes the best pool player at the
    slot's positions that no other slot of the roster took. A flex slot takes any of its positions.
    `pool` holds the player id, the projection, and the position of each pool player, best first.
    """
    added = 0.0
    taken: set[str] = set()
    for slot, pid in slots:
        # A healthy starter at zero has a bye or no game that week. Every roster takes its byes in turn, so the zero
        # is part of the real roster, not a hole from an injury.
        if pid is None or points[pid] or pid not in injuries:
            continue
        # The best lineup fills each slot with the best player left at its positions, so no bench player at the
        # slot's positions projects above zero. Only a pool player can be the better of the bench and the waivers.
        allowed = allowed_positions(slot)
        cover = next(((fa, value) for fa, value, position in pool if fa not in taken and position in allowed), None)
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
        odds_before: OddsResult | None = None,
        *,
        client: Client,
        sources: Sequence[ChapterSource] = (),
    ) -> None:
        self.week = week
        # The chapter list and the rankings chapter take only the context, so they read the team count from it.
        self.client = client
        # The chapters that other packages give the week, through the chapter port. The odds come from them too.
        self.sources = tuple(sources)
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
        self.table = standings(week, history, client=client)
        self.by_rank = {s.roster_id: s for s in self.table}
        self.before = ranks_before(week, self.table, history, median_game=client.settings.median_game)
        # A league with no median game has no median line, so no fact, chapter, or clause reads one.
        self.median = median_facts(week) if client.settings.median_game else None
        self.pick = matchup_of_the_week(week, self.mfacts, self.table, self.before, client=client)
        self.drops = drop_lines(week, nfl)
        self.nfl = nfl
        self.chart = chart
        # The bye facts read the position rank and the lineup value from it. None gives no rank and no bye cover.
        self.snapshot = snapshot
        self.nfl_up = nfl is not None and nfl.drops is not None
        self.awards = awards(week, self.mfacts)
        self.season_history = season_history(week, history)
        # The odds of a chapter source and the shootout storyline read the same projected lineups.
        self.projected = projected_totals(week, client, nfl.bye_weeks if nfl is not None else None)
        # The first source that gives odds sets them. A client with no source of odds, such as one with no rankings,
        # has none, so the impact fact has no odds part.
        self.odds = next((odds for source in self.sources if (odds := source.odds(self)) is not None), None)
        # The saved odds of the week before, for the odds part of the impact fact. None leaves that part out.
        self.odds_before = odds_before
        self.next = next_week(week, self.table, history, self.projected, nfl.bye_weeks if nfl is not None else None,
                              snapshot.position_rank if snapshot is not None else None, client=client)
        self.ranks = position_ranks(week)
        self.leaders = position_leaders(week, client.settings.positions)
        self.leader_positions = list(client.settings.positions)
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
