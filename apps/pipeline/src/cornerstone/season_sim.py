"""
The app side of the season sim: it loads the inputs of the sim from the saved week and runs the sim package on them.
The inputs are those of the weekly odds, so the two draws read one league. The app hands the result to the report.
"""
from pathlib import Path

from league.client import Client
from league.models import History
from league.nflverse import SCHEDULES_URL, cache_path, download, read_schedules
from league.parse import parse_week
from league.paths import nflverse_cache_dir, raw_dir
from league.provider.sleeper import load_raw
from league.standings_table import season_records
from rankings.chapter import odds_inputs
from sim.season import SimResult, season_sim
from week.sheet import projected_totals


def schedule_file(nfl: Path, season: int) -> Path | None:
    """The cached NFL schedule of the NFL data `nfl`, at the cache path of each nflverse reader, so the report and the
    sim read one copy. Git ignores the cache, so a fresh worktree fetches it once.

    A saved file stands as it is: the bye weeks of a season do not change, so one input gives one output.
    """
    path = cache_path(nflverse_cache_dir(nfl), SCHEDULES_URL, season)
    if path.exists():
        return path
    return download(SCHEDULES_URL, path)


def week_sim(season: int, week: int, history: History, *, client: Client) -> SimResult | None:
    """The sim of the rest of the season after `week`, from the saved raw data of the week and the saved history.

    The scores and the remaining pairs come from odds_inputs of the weekly odds. The projected totals run through
    the last bracket week, with the bye weeks of the NFL schedule. None when the week gives no odds inputs.
    """
    raw = load_raw(raw_dir(client.folder, season, week))
    parsed = parse_week(raw, week=week, team_count=client.settings.team_count, points_key=client.settings.points_key)
    inputs = odds_inputs(parsed, history, client)
    if inputs is None:
        return None
    scores, remaining = inputs
    path = schedule_file(client.nfl_dir, season)
    schedules = read_schedules(path, season) if path is not None else None
    bye_weeks = {team: s.bye_week for team, s in schedules.items() if s.bye_week is not None} if schedules else None
    projected = projected_totals(parsed, client, bye_weeks, through=client.settings.last_season_week)
    records = season_records(history, week, median_game=client.settings.median_game)
    return season_sim(scores, records, remaining, season=season, week=week, settings=client.settings,
                      projected=projected)
