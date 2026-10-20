"""
Cache of past weeks of Sleeper data under data/{season}/history.
It fetches only the weeks that are not on disk.
"""
import json
import shutil
from collections.abc import Callable
from pathlib import Path

from cornerstone.facts_league import TREND_WEEKS
from cornerstone.models import History, PastWeek
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



def player_points(past: PastWeek, player_id: str) -> float | None:
    """Points of a player in a past week. The roster points come first, then the stat line."""
    if player_id in past.points:
        return past.points[player_id]
    return (past.stats.get(player_id) or {}).get("pts_half_ppr")


def player_trend(history: History, player_id: str) -> int | None:
    """The count of the last 3 weeks in which the player beat the projection.

    It is None when any of the 3 weeks lacks points or a projection, so a gap never gives a wrong count.
    """
    beaten = 0
    for week in range(history.week - TREND_WEEKS + 1, history.week + 1):
        past = history.weeks.get(week)
        if past is None:
            return None
        points = player_points(past, player_id)
        projection = past.projections.get(player_id)
        if points is None or projection is None:
            return None
        beaten += points > projection
    return beaten


def save_week_to_history(raw_dir: Path, out_dir: Path) -> None:
    """Put a built week into the history, so the next week reads it from disk.

    The files are copies, not symlinks. A refetch or a move of the raw directory must not change the history.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in HISTORY_FILES:
        shutil.copyfile(raw_dir / f"{name}.json", out_dir / f"{name}.json")
    matchups = json.loads((raw_dir / "matchups.json").read_text(encoding="utf-8"))
    players = json.loads((raw_dir / "players.json").read_text(encoding="utf-8"))
    injuries = {}
    for roster in matchups:
        for player_id in roster["players"]:
            status = (players.get(player_id) or {}).get("injury_status")
            if status:
                injuries[player_id] = status
    (out_dir / "injuries.json").write_text(json.dumps(injuries, indent=2), encoding="utf-8")
