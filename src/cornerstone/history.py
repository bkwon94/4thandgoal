"""
Cache of past weeks of Sleeper data under data/{season}/history.
It fetches only the weeks that are not on disk.
"""
import json
from collections.abc import Callable
from pathlib import Path

from cornerstone.models import History
from cornerstone.parse import parse_past_week
from cornerstone.sleeper import fetch_past_week

HISTORY_FILES: tuple[str, ...] = ("matchups", "transactions", "stats", "projections")
UNOFFICIAL_FILES: tuple[str, ...] = ("stats", "projections")


def history_root(repo: Path, season: int) -> Path:
    return repo / "data" / str(season) / "history"


def history_dir(root: Path, week: int) -> Path:
    return root / f"week-{week:02d}"


def _is_saved(directory: Path) -> bool:
    if not all((directory / f"{name}.json").exists() for name in HISTORY_FILES):
        return False
    # The unofficial endpoints return an empty list on an outage, so an empty file is not saved data.
    return all(json.loads((directory / f"{name}.json").read_text()) for name in UNOFFICIAL_FILES)


def fetch_history(
    league_id: str,
    season: int,
    through: int,
    root: Path,
    force: bool = False,
    fetch: Callable[[str, int, int, Path], None] = fetch_past_week,
) -> list[int]:
    fetched = []
    for week in range(1, through + 1):
        directory = history_dir(root, week)
        if not force and _is_saved(directory):
            continue
        fetch(league_id, season, week, directory)
        fetched.append(week)
    return fetched


def _read_week(directory: Path) -> dict[str, object] | None:
    # A week with a missing file is left out, so a gap removes facts and never makes one wrong.
    if not all((directory / f"{name}.json").exists() for name in HISTORY_FILES):
        return None
    return {
        name: json.loads((directory / f"{name}.json").read_text())
        for name in HISTORY_FILES
    }


def load_history(root: Path, raw: dict[str, object], week: int) -> History:
    weeks = {}
    for past in range(1, week):
        saved = _read_week(history_dir(root, past))
        if saved is not None:
            weeks[past] = parse_past_week(saved, past)
    # The current week comes from the raw data of this run, not from the cache.
    weeks[week] = parse_past_week(raw, week)
    return History(week=week, weeks=weeks)
