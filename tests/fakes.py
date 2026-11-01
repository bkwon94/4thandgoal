"""
No-network stand-ins for the build inputs: Sleeper, news, nflverse, the expert search, and any URL fetch.
The pipeline tests and the golden build share them, so both run the same offline build.
"""
import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from cornerstone.models import ResearchOut
from cornerstone.nflverse import nflverse_week
from cornerstone.provider.base import Provider
from cornerstone.provider.raw import RawAheadWeek, RawPastWeek, RawWeek
from cornerstone.provider.sleeper import load_raw

NFLVERSE_FIXTURES = Path(__file__).parent / "fixtures" / "nflverse"
RAW_FIXTURES = Path(__file__).parent / "fixtures" / "2026" / "week-06" / "raw"
HISTORY_FIXTURES = Path(__file__).parent / "fixtures" / "2026" / "history"
# The recorded week 6 has no fetch time, so the live fetch gives this one.
FIXTURE_FETCHED = datetime(2026, 10, 21, 9, 30, tzinfo=ZoneInfo("America/New_York"))


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


class FixtureProvider:
    """A provider that reads the recorded week 6 files and the week 1 to 5 history. It never calls the network.

    The league id, the season, and the cache file do not change what it gives, because the fixtures hold one league.
    """

    def __init__(self, raw_dir: Path = RAW_FIXTURES, history_root: Path = HISTORY_FIXTURES,
                 fetched: datetime = FIXTURE_FETCHED):
        self.raw_dir = raw_dir
        self.history_root = history_root
        self.fetched = fetched

    def fetch_week(
            self, league_id: str, season: int, week: int, raw_dir: Path, players_cache: Path, tz: ZoneInfo) -> RawWeek:
        shutil.copytree(self.raw_dir, raw_dir, dirs_exist_ok=True)
        return load_raw(raw_dir)

    def fetch_live(self, league_id: str, players_cache: Path) -> tuple[RawWeek, datetime]:
        return load_raw(self.raw_dir), self.fetched

    def fetch_past_leg(self, league_id: str, season: int, week: int, out_dir: Path) -> RawPastWeek:
        saved = self.history_root / f"week-{week:02d}"
        shutil.copytree(saved, out_dir, dirs_exist_ok=True)
        return RawPastWeek.model_validate({f.stem: json.loads(f.read_text(encoding="utf-8"))
                                           for f in saved.glob("*.json")})

    def fetch_players(self, players_cache: Path) -> dict[str, dict]:
        return load_raw(self.raw_dir).players

    def fetch_projections(self, season: int, week: int) -> list[RawAheadWeek]:
        return load_raw(self.raw_dir).projections_ahead or []


# The annotation makes pyright prove that the fake has the five fetches of the protocol, with the same types.
FIXTURE_PROVIDER: Provider = FixtureProvider()
