"""
Loads the slow sources of the snapshot: the schedules, the depth charts, the id map, the points allowed, injuries,
the expected points, and the WOPR. A source that is not there is None, so the build never stops on one.
`missing` names each source that is not there. The expected points and the WOPR go by the names of their files.
"""
import csv
import logging
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from league.league_settings import DEFAULT_POINTS_KEY
from league.models import ExpectedPoints
from league.nflverse import (
    DEPTH_CHARTS_URL,
    FFIDS_URL,
    FFOPPORTUNITY_URL,
    INJURIES_URL,
    SCHEDULES_URL,
    STATS_PLAYER_URL,
    TeamSchedule,
    cache_path,
    read_depth_charts,
    read_id_map,
    read_injuries,
    read_kickoffs,
    read_schedules,
)
from league.nflverse_expected import read_expected
from league.nflverse_players import read_player_weeks
from league.points_allowed import PositionAllowed, points_allowed

logger = logging.getLogger(__name__)


class SlowSources(BaseModel):
    """The slow sources of one snapshot. The depth chart lists gsis_ids, and `id_map` joins them to Sleeper ids."""
    # The Sleeper code of the NFL team keys each field, or the code of the defense for points allowed.
    schedules: dict[str, TeamSchedule] | None = None
    # Team to position to the ordered gsis_ids. Sleeper rosters hold Sleeper ids, so `id_map` joins the two.
    depth_charts: dict[str, dict[str, list[str]]] | None = None
    # The scrape time of the newest depth chart. The Week line names no step-up from a chart that is too old.
    depth_chart_dt: datetime | None = None
    # Sleeper id to gsis_id.
    id_map: dict[str, str] | None = None
    points_allowed: dict[str, dict[str, PositionAllowed]] | None = None
    # The injury report status by gsis_id and week. `id_map` joins it to Sleeper ids, as for the depth chart.
    injuries: dict[str, dict[int, str]] | None = None
    # The expected window of each player by Sleeper id. Only the expected gap adjuster reads it.
    # That adjuster says in its own reason when the data is not there. A None here is "expected_points" in `missing`,
    # so the sources line shows that the grade did not read the file.
    expected: ExpectedPoints | None = None
    # The WOPR by Sleeper id and week. Only the trend adjuster reads it, as a tiebreak before red-zone use.
    # Without it, red-zone use breaks the tie. A None here is "player_weeks" in `missing`, the name of its file.
    wopr: dict[str, dict[int, int]] | None = None
    # The kickoff of each NFL team's game of `week`, from the schedules file. Only the in-progress label reads it.
    # A team with no kickoff has a game that counts as final, so a None here is no source in `missing`.
    kickoffs: dict[str, datetime] | None = None
    missing: list[str] = []


def _read(name: str, read, *args):
    # A bad file is a missing source, not an error: the slow sources only add facts.
    try:
        return read(*args)
    except (OSError, EOFError, KeyError, ValueError, csv.Error) as error:
        logger.warning("The %s source is unreadable (%s)", name, error)
        return None


def load_slow_sources(cache_dir: Path, season: int, week: int, history_root: Path,
                      scoring: dict[str, float] | None = None,
                      points_key: str = DEFAULT_POINTS_KEY) -> SlowSources:
    """The slow sources from the cache and the history, with no network call.

    The nflverse fetch fills the cache. The points allowed count the weeks before `week`,
    because the stat lines of the current week are not final. The injury report must hold the week
    before `week` too, so a file that ends earlier counts as missing.
    `scoring` is the league scoring. The expected points rescale to it, so without it they are None.
    The points allowed read the stat lines at `points_key`, the points key of the League settings.
    The WOPR comes from the nflverse weekly player file. It ends at `week` when the file has it, else at the week
    before.
    The kickoffs are of the games of `week`, so the snapshot can tell a game in progress from a final one.
    """
    schedules_path = cache_path(cache_dir, SCHEDULES_URL, season)
    depth_path = cache_path(cache_dir, DEPTH_CHARTS_URL, season)
    ffids_path = cache_path(cache_dir, FFIDS_URL, season)
    injuries_path = cache_path(cache_dir, INJURIES_URL, season)
    depth = _read("depth_charts", read_depth_charts, depth_path) if depth_path.exists() else None
    sources = {
        "schedules": _read("schedules", read_schedules, schedules_path, season) if schedules_path.exists() else None,
        "depth_charts": depth.charts if depth else None,
        "id_map": _read("id_map", read_id_map, ffids_path) if ffids_path.exists() else None,
        "points_allowed": _read("points_allowed", points_allowed, history_root, week - 1, points_key),
        "injuries": _read("injuries", read_injuries, injuries_path, week - 1) if injuries_path.exists() else None,
    }
    # The id map joins the gsis ids of the nflverse files to Sleeper ids, as it does for the depth chart.
    sleeper_of_gsis = {gsis: pid for pid, gsis in sorted((sources["id_map"] or {}).items())}
    expected_path = cache_path(cache_dir, FFOPPORTUNITY_URL, season)
    expected = None
    if scoring is not None and sleeper_of_gsis and expected_path.exists() and schedules_path.exists():
        # The expected window ends at the week before `week`, so it never reads the known games of `week`.
        # The expected points file is a Tuesday source: it keeps its weekly lag, unlike the WOPR.
        expected = _read("expected", read_expected, expected_path, schedules_path, season, week - 1, scoring,
                         sleeper_of_gsis)
    stats_player_path = cache_path(cache_dir, STATS_PLAYER_URL, season)
    wopr = None
    if sleeper_of_gsis and stats_player_path.exists():
        wopr = _read("wopr", _read_wopr, stats_player_path, week - 1, sleeper_of_gsis)
    kickoffs = _read("kickoffs", read_kickoffs, schedules_path, season, week) if schedules_path.exists() else None
    # The two go by the names of their files in `missing`, because the sources line names the files the grade read.
    named = {**sources, "expected_points": expected, "player_weeks": wopr}
    return SlowSources(**sources, depth_chart_dt=depth.dt if depth else None, expected=expected, wopr=wopr,
                       kickoffs=kickoffs,
                       missing=[name for name, source in named.items() if source is None])


def _read_wopr(path: Path, through: int, sleeper_of_gsis: dict[str, str]) -> dict[str, dict[int, int]] | None:
    """The WOPR by Sleeper id and week, from week 1 to `through`, plus the week after when the file has it.

    The week after is the trade week, so the known games read its rows. None when the file has no row for `through`.
    """
    # nflverse adds the rows of the trade week some time after its games, so the file may end at `through`.
    rows = read_player_weeks(path, 1, through + 1, sleeper_of_gsis)
    if rows is None:
        rows = read_player_weeks(path, 1, through, sleeper_of_gsis)
    if rows is None:
        return None
    out: dict[str, dict[int, int]] = {}
    for (pid, week), row in sorted(rows.items()):
        out.setdefault(pid, {})[week] = row.wopr
    return out
