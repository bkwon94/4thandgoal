"""Builds every directory and label of the repo layout: the client folders, the shared NFL data, and the site.
A client folder clients/<slug> holds the data of its league. The NFL data at data/nfl is the same for each client.
"""
from pathlib import Path

_WEEK_PREFIX = "week-"


def week_label(week: int) -> str:
    return f"{_WEEK_PREFIX}{week:02d}"


def week_from_label(text: str) -> int:
    """The week number of a label such as `week-07`, or of a file stem that is a label."""
    return int(text.removeprefix(_WEEK_PREFIX))


def client_dir(root: Path, slug: str) -> Path:
    """The folder of the client `slug` under the repo root."""
    return root / "clients" / slug


def nfl_dir(root: Path) -> Path:
    """The shared NFL data folder under the repo root. No client owns it."""
    return root / "data" / "nfl"


def _season_root(client: Path, season: int) -> Path:
    return client / "data" / str(season)


def league_file(client: Path, season: int) -> Path:
    """The provider league file of the season. The League settings of the season come from it."""
    return _season_root(client, season) / "league.json"


def week_dir(client: Path, season: int, week: int) -> Path:
    return _season_root(client, season) / week_label(week)


def raw_dir(client: Path, season: int, week: int) -> Path:
    return week_dir(client, season, week) / "raw"


def history_root(client: Path, season: int) -> Path:
    return _season_root(client, season) / "history"


def history_week_dir(root: Path, week: int) -> Path:
    """A week under a given history root, for the readers that hold the root and not the client folder."""
    return root / week_label(week)


def history_dir(client: Path, season: int, week: int) -> Path:
    return history_week_dir(history_root(client, season), week)


def history_raw_dir(root: Path, week: int) -> Path:
    """The raw directory of a week, which sits beside the history root: <client>/data/{season}/week-NN/raw."""
    return root.parent / week_label(week) / "raw"


def returns_path(nfl: Path, season: int) -> Path:
    """The hand-kept Returns file of the season: the return week by player id. GLOSSARY.md, "Returns file"."""
    return nfl / str(season) / "returns.json"


def build_dir(client: Path) -> Path:
    """The build folder of the client: each page and season file the build writes. Publish copies from it.
    Why: each client has its own folder, so the build of one client never overwrites the files of another."""
    return client / "build"


def season_dir(site: Path, season: int) -> Path:
    return site / str(season)


def site_week_dir(site: Path, season: int, week: int) -> Path:
    return season_dir(site, season) / week_label(week)


def _cache_dir(nfl: Path) -> Path:
    return nfl / "cache"


def provider_cache_dir(nfl: Path) -> Path:
    """The cache dir of the provider adapter. It holds the players file, which every league of the repo shares."""
    return _cache_dir(nfl)


def nflverse_cache_dir(nfl: Path) -> Path:
    """The one nflverse cache directory. The fetch fills it and the analyze command reads it."""
    return _cache_dir(nfl) / "nflverse"


def charts_dir(nfl: Path, chart: str) -> Path:
    """The cache of the chart `chart`. Clients that read different charts share data/nfl, so each chart has its own dir."""
    return _cache_dir(nfl) / "charts" / chart


def chart_image(nfl: Path, chart: str, week: int) -> Path:
    return charts_dir(nfl, chart) / f"{week_label(week)}.png"


def chart_read(nfl: Path, chart: str, week: int) -> Path:
    return charts_dir(nfl, chart) / f"{week_label(week)}.json"


def results_cache_dir(root: Path) -> Path:
    """The cache of the API results under the repo root. It is not NFL data, so it sits outside data/nfl."""
    return root / "data" / "cache" / "results"
