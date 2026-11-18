"""
The app side of the season sim, the one odds engine: it runs the sim package on the inputs of a week. It gives the
weekly odds to the week build through the chapter port, the week sim file to the build, and the sim to the report.
"""
from pathlib import Path
from typing import NamedTuple

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


class SimInputs(NamedTuple):
    """The inputs of the season sim after one week, in the order of the arguments of `season_sim`."""
    scores: dict[int, list[float]]
    records: dict[int, tuple[int, int, float]]
    remaining: dict[int, list[tuple[int, int]]]
    projected: dict[int, dict[int, float]]


def week_inputs(season: int, week: int, history: History, *, client: Client) -> SimInputs | None:
    """The inputs of the sim after `week`, from the saved raw data of the week and the saved history.

    The bye weeks come from the NFL schedule. None when the week gives no odds inputs.
    """
    raw = load_raw(raw_dir(client.folder, season, week))
    parsed = parse_week(raw, week=week, team_count=client.settings.team_count, points_key=client.settings.points_key)
    path = schedule_file(client.nfl_dir, season)
    schedules = read_schedules(path, season) if path is not None else None
    bye_weeks = {team: s.bye_week for team, s in schedules.items() if s.bye_week is not None} if schedules else None
    return inputs_of_week(parsed, history, client=client, bye_weeks=bye_weeks)


def inputs_of_week(
    week: Week, history: History | None, *, client: Client, bye_weeks: dict[str, int] | None,
) -> SimInputs | None:
    """The inputs of the sim after the parsed `week`. None when the week gives no odds inputs.

    The scores and the remaining pairs come from odds_inputs of the weekly odds. The projected totals run through
    the last bracket week. `bye_weeks` holds the bye week of each NFL team, so a bye gives no cover in them.
    """
    inputs = odds_inputs(week, history, client)
    if inputs is None or history is None:
        return None
    scores, remaining = inputs
    projected = projected_totals(week, client, bye_weeks, through=client.settings.last_season_week)
    records = season_records(history, week.week, median_game=client.settings.median_game)
    return SimInputs(scores, records, remaining, projected)


def week_sim(
    season: int, week: int, history: History, *, client: Client, runs: int = SIM_RUNS,
) -> SimResult | None:
    """The sim of the rest of the season after `week`, from the saved raw data of the week and the saved history.

    None when the week gives no odds inputs. The sim draws `runs` seasons. The real build keeps the default of the
    sim tunables.
    """
    inputs = week_inputs(season, week, history, client=client)
    return _sim(inputs, season, week, client, runs)


def week_sim_with_pages(
    season: int, week: int, history: History, *, client: Client, runs: int = SIM_RUNS,
) -> SimResult | None:
    """The sim of the week file after `week`: the sim of `week_sim` with the page block of each team. None when the
    week gives no odds inputs.

    It reads the bye weeks from the NFL schedule, as `week_sim` and the midseason sim do, so each sim file reads one
    source. The nflverse extract of the build reads its bye weeks from the same cached schedule file.
    """
    inputs = week_inputs(season, week, history, client=client)
    if inputs is None:
        return None
    return _sim(inputs, season, week, client, runs, pages=sorted(inputs.records))


def sim_of_week(
    week: Week, history: History | None, *, client: Client, bye_weeks: dict[str, int] | None,
    runs: int = SIM_RUNS,
) -> SimResult | None:
    """The sim of the rest of the season after the parsed `week`. None when the week gives no odds inputs."""
    inputs = inputs_of_week(week, history, client=client, bye_weeks=bye_weeks)
    return _sim(inputs, week.season, week.week, client, runs)


def _sim(
    inputs: SimInputs | None, season: int, week: int, client: Client, runs: int, pages: list[int] | None = None,
) -> SimResult | None:
    if inputs is None:
        return None
    return season_sim(inputs.scores, inputs.records, inputs.remaining, season=season, week=week,
                      settings=client.settings, projected=inputs.projected, runs=runs, pages=pages or ())


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
