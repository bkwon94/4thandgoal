"""Builds every directory and label of the repo layout from the repo root or the site root.
The functions take no config yet. The layout does not name the league, so a later feature adds that segment here only.
"""
from pathlib import Path

WEEK_PREFIX = "week-"


def week_label(week: int) -> str:
    return f"{WEEK_PREFIX}{week:02d}"


def week_from_label(text: str) -> int:
    """The week number of a label such as `week-07`, or of a file stem that is a label."""
    return int(text.removeprefix(WEEK_PREFIX))


def season_root(repo: Path, season: int) -> Path:
    return repo / "data" / str(season)


def week_dir(repo: Path, season: int, week: int) -> Path:
    return season_root(repo, season) / week_label(week)


def raw_dir(repo: Path, season: int, week: int) -> Path:
    return week_dir(repo, season, week) / "raw"


def history_root(repo: Path, season: int) -> Path:
    return season_root(repo, season) / "history"


def history_dir(repo: Path, season: int, week: int) -> Path:
    return history_root(repo, season) / week_label(week)


def returns_path(repo: Path, season: int) -> Path:
    """The hand-kept returns file of the season: the return week by player id, beside the history."""
    return season_root(repo, season) / "returns.json"


def season_dir(site: Path, season: int) -> Path:
    return site / str(season)


def site_week_dir(site: Path, season: int, week: int) -> Path:
    return season_dir(site, season) / week_label(week)


def cache_dir(repo: Path) -> Path:
    return repo / "data" / "cache"


def players_cache(repo: Path) -> Path:
    return cache_dir(repo) / "players.json"


def nflverse_cache_dir(repo: Path) -> Path:
    """The one nflverse cache directory. The fetch fills it and the analyze command reads it."""
    return cache_dir(repo) / "nflverse"


def charts_dir(repo: Path) -> Path:
    return cache_dir(repo) / "charts"


def chart_image(repo: Path, week: int) -> Path:
    return charts_dir(repo) / f"{week_label(week)}.png"


def chart_read(repo: Path, week: int) -> Path:
    return charts_dir(repo) / f"{week_label(week)}.json"


def results_cache_dir(repo: Path) -> Path:
    return cache_dir(repo) / "results"
