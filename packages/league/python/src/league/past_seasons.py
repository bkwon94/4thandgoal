"""
The weekly player files of the last complete seasons, kept in the nflverse cache with no max age.
A past season never changes, so a file that is on disk is never downloaded again.
"""
import logging
from collections.abc import Callable
from pathlib import Path

from league.nflverse import STATS_PLAYER_URL, cache_path, download

logger = logging.getLogger(__name__)

# The history claims read this many complete seasons before the season of the trade.
PAST_SEASON_COUNT = 3
# A past file is final, so no age makes it stale. One trillion seconds is longer than any file lives.
NEVER_STALE_SECONDS = 10**12


def past_seasons(season: int) -> list[int]:
    """The complete seasons before `season`, oldest first."""
    return list(range(season - PAST_SEASON_COUNT, season))


def past_stats_path(cache_dir: Path, past_season: int) -> Path:
    return cache_path(cache_dir, STATS_PLAYER_URL, past_season)


def fetch_past_seasons(cache_dir: Path, season: int, fetch: Callable[[str], bytes]) -> list[int]:
    """Download each past season file that is not in the cache. Return the seasons it downloaded.

    A failed download logs and leaves a gap, so the sheet gives no split for that season.
    """
    downloaded = []
    for past in past_seasons(season):
        path = past_stats_path(cache_dir, past)
        if path.exists():
            continue
        url = STATS_PLAYER_URL.format(season=past)
        logger.info("Downloading the past season file of %d", past)
        if download(url, path, max_age_seconds=NEVER_STALE_SECONDS, fetch=fetch) is not None:
            downloaded.append(past)
    return downloaded
