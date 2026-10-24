"""
Loads the slow sources of the snapshot: the schedules, the depth charts, the id map, the points allowed, injuries, and
the expected points. A source that is not there is None, so the build never stops on one.
`missing` names each source that is not there, except the expected points.
"""
import csv
import logging
from pathlib import Path

from pydantic import BaseModel

from cornerstone.models import ExpectedPoints
from cornerstone.nflverse import (
    DEPTH_CHARTS_URL, FFIDS_URL, FFOPPORTUNITY_URL, INJURIES_URL, SCHEDULES_URL, TeamSchedule, cache_path,
    read_depth_charts, read_id_map, read_injuries, read_schedules,
)
from cornerstone.nflverse_expected import read_expected
from cornerstone.points_allowed import PositionAllowed, points_allowed

logger = logging.getLogger(__name__)


class SlowSources(BaseModel):
    """The slow sources of one snapshot. The depth chart lists gsis_ids, and `id_map` joins them to Sleeper ids."""
    # The Sleeper code of the NFL team keys each field, or the code of the defense for points allowed.
    schedules: dict[str, TeamSchedule] | None = None
    # Team to position to the ordered gsis_ids. Sleeper rosters hold Sleeper ids, so `id_map` joins the two.
    depth_charts: dict[str, dict[str, list[str]]] | None = None
    # Sleeper id to gsis_id.
    id_map: dict[str, str] | None = None
    points_allowed: dict[str, dict[str, PositionAllowed]] | None = None
    # The injury report status by gsis_id and week. `id_map` joins it to Sleeper ids, as for the depth chart.
    injuries: dict[str, dict[int, str]] | None = None
    # The expected window of each player by Sleeper id. Only the expected gap adjuster reads it.
    # That adjuster says in its own reason when the data is not there, so a None here is not in `missing`.
    expected: ExpectedPoints | None = None
    missing: list[str] = []


def _read(name: str, read, *args):
    # A bad file is a missing source, not an error: the slow sources only add facts.
    try:
        return read(*args)
    except (OSError, EOFError, KeyError, ValueError, csv.Error) as error:
        logger.warning("The %s source is unreadable (%s)", name, error)
        return None


def load_slow_sources(cache_dir: Path, season: int, week: int, history_root: Path,
                      scoring: dict[str, float] | None = None) -> SlowSources:
    """The slow sources from the cache and the history, with no network call.

    The nflverse fetch fills the cache. The points allowed count the weeks before `week`,
    because the stat lines of the current week are not final. The injury report must hold the week
    before `week` too, so a file that ends earlier counts as missing.
    `scoring` is the league scoring. The expected points rescale to it, so without it they are None.
    """
    schedules_path = cache_path(cache_dir, SCHEDULES_URL, season)
    depth_path = cache_path(cache_dir, DEPTH_CHARTS_URL, season)
    ffids_path = cache_path(cache_dir, FFIDS_URL, season)
    injuries_path = cache_path(cache_dir, INJURIES_URL, season)
    sources = {
        "schedules": _read("schedules", read_schedules, schedules_path, season) if schedules_path.exists() else None,
        "depth_charts": _read("depth_charts", read_depth_charts, depth_path) if depth_path.exists() else None,
        "id_map": _read("id_map", read_id_map, ffids_path) if ffids_path.exists() else None,
        "points_allowed": _read("points_allowed", points_allowed, history_root, week - 1),
        "injuries": _read("injuries", read_injuries, injuries_path, week - 1) if injuries_path.exists() else None,
    }
    expected_path = cache_path(cache_dir, FFOPPORTUNITY_URL, season)
    expected = None
    if scoring is not None and sources["id_map"] and expected_path.exists() and schedules_path.exists():
        # The id map joins the gsis ids of the file to Sleeper ids, as it does for the depth chart.
        sleeper_of_gsis = {gsis: pid for pid, gsis in sorted(sources["id_map"].items())}
        # Every grade input ends at the week before `week`, so the expected window does too.
        expected = _read("expected", read_expected, expected_path, schedules_path, season, week - 1, scoring,
                         sleeper_of_gsis)
    return SlowSources(**sources, expected=expected,
                       missing=[name for name, source in sources.items() if source is None])
