"""
Cache of past weeks of Sleeper data under data/{season}/history.
It fetches only the weeks that are not on disk.
"""
from collections.abc import Callable
from pathlib import Path

from cornerstone.sleeper import fetch_past_week

HISTORY_FILES: tuple[str, ...] = ("matchups", "transactions", "stats", "projections")


def history_root(repo: Path, season: int) -> Path:
    return repo / "data" / str(season) / "history"


def history_dir(root: Path, week: int) -> Path:
    return root / f"week-{week:02d}"


def _is_saved(directory: Path) -> bool:
    return all((directory / f"{name}.json").exists() for name in HISTORY_FILES)


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
