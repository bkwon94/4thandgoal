"""
The app side of the season sim, the one odds engine: it runs the sim package on the inputs of a week. It gives the
weekly odds to the week build through the chapter port, and it hands the sim of a saved week to the midseason report.
"""
from pathlib import Path

from league.client import Client
from league.models import Chapter, Fact, History, OddsResult, Week
from league.nflverse import SCHEDULES_URL, cache_path, download, read_schedules
from league.parse import parse_week
from league.paths import nflverse_cache_dir, raw_dir
from league.provider.sleeper import load_raw
from league.standings_table import season_records
from rankings.chapter import odds_inputs
from sim.season import SimResult, season_sim, weekly_odds
from sim.tunables import SIM_RUNS
from week.sheet import Context, projected_totals


def schedule_file(nfl: Path, season: int) -> Path | None:
    """The cached NFL schedule of the NFL data `nfl`, at the cache path of each nflverse reader, so the report and the
    sim read one copy. Git ignores the cache, so a fresh worktree fetches it once.

    A saved file stands as it is: the bye weeks of a season do not change, so one input gives one output.
    """
    path = cache_path(nflverse_cache_dir(nfl), SCHEDULES_URL, season)
    if path.exists():
        return path
    return download(SCHEDULES_URL, path)


def week_sim(
    season: int, week: int, history: History, *, client: Client, runs: int = SIM_RUNS,
) -> SimResult | None:
    """The sim of the rest of the season after `week`, from the saved raw data of the week and the saved history.

    The scores and the remaining pairs come from odds_inputs of the weekly odds. The projected totals run through
    the last bracket week, with the bye weeks of the NFL schedule. None when the week gives no odds inputs.
    The sim draws `runs` seasons. The real build keeps the default of the sim tunables.
    """
    raw = load_raw(raw_dir(client.folder, season, week))
    parsed = parse_week(raw, week=week, team_count=client.settings.team_count, points_key=client.settings.points_key)
    path = schedule_file(client.nfl_dir, season)
    schedules = read_schedules(path, season) if path is not None else None
    bye_weeks = {team: s.bye_week for team, s in schedules.items() if s.bye_week is not None} if schedules else None
    return sim_of_week(parsed, history, client=client, bye_weeks=bye_weeks, runs=runs)


def sim_of_week(
    week: Week, history: History | None, *, client: Client, bye_weeks: dict[str, int] | None,
    runs: int = SIM_RUNS,
) -> SimResult | None:
    """The sim of the rest of the season after the parsed `week`. None when the week gives no odds inputs.

    `bye_weeks` holds the bye week of each NFL team, so a bye gives no cover in the projected totals.
    """
    inputs = odds_inputs(week, history, client)
    if inputs is None or history is None:
        return None
    scores, remaining = inputs
    projected = projected_totals(week, client, bye_weeks, through=client.settings.last_season_week)
    records = season_records(history, week.week, median_game=client.settings.median_game)
    return season_sim(scores, records, remaining, season=week.season, week=week.week, settings=client.settings,
                      projected=projected, runs=runs)


class SimOdds:
    """The odds of the week from the season sim, through the chapter port of week.sheet.port (ADR 0037).

    The sim runs once per build here, and the odds reach the saved facts, so a rewrite never runs it. It gives no
    facts and no chapter: the rankings chapter writes the odds facts from these odds.
    """

    def odds(self, c: Context) -> OddsResult | None:
        bye_weeks = c.nfl.bye_weeks if c.nfl is not None else None
        sim = sim_of_week(c.week, c.history, client=c.client, bye_weeks=bye_weeks)
        return weekly_odds(sim) if sim is not None else None

    def facts(self, c: Context) -> list[Fact]:
        return []

    def chapter(self, c: Context, facts: dict[str, Fact]) -> Chapter | None:
        return None


SIM_ODDS = SimOdds()
