"""
No-network stand-ins for the build inputs: news, nflverse, the expert search, and any URL fetch.
The pipeline tests and the golden build share them, so both run the same offline build.
"""
import shutil
import tempfile
from pathlib import Path

from cornerstone.models import ResearchOut
from cornerstone.nflverse import nflverse_week

NFLVERSE_FIXTURES = Path(__file__).parent / "fixtures" / "nflverse"


def no_news(player_id):
    return []


def no_network(url):
    raise AssertionError(f"network call to {url}")


def no_claims(system, user):
    return ResearchOut(claims=[])


def fixture_nflverse(cache: Path):
    """A fetcher that reads the recorded nflverse files through the real parser. Each call gets a fresh copy under
    `cache`, so one call never sees the files another call wrote. The caller owns `cache` and removes it."""
    def fetch(season, week, player_ids, players, teams, scoring):
        cache.mkdir(parents=True, exist_ok=True)
        fresh = Path(tempfile.mkdtemp(dir=cache))
        for f in NFLVERSE_FIXTURES.iterdir():
            shutil.copy(f, fresh / f.name)
        return nflverse_week(season, week, player_ids, players, fresh, teams, fetch=no_network, scoring=scoring)
    return fetch
