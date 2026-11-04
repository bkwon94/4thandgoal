"""
No-network stand-ins for the build inputs: Sleeper, Claude, news, nflverse, the expert search, and any URL fetch.
The pipeline tests and the golden build share them, so both run the same offline build. Each port has its one fake here.
"""
import json
import shutil
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
from pydantic import BaseModel

from league.claude_errors import WriterError
from league.claude_port import Writer
from league.league_settings import LeagueSettings
from league.models import ResearchOut
from league.nflverse import nflverse_week
from league.provider.base import Provider
from league.provider.raw import RawAheadWeek, RawPastWeek, RawWeek
from league.provider.sleeper import league_settings, load_raw

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


def json_transport(body: Callable[[str, httpx.QueryParams], object]) -> httpx.MockTransport:
    """An httpx transport that answers each request with the JSON of `body(url, params)`. The URL has no query.

    A body that raises an httpx error fails the request, as a network failure does. It is not a patch of a port.
    """
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body(str(request.url.copy_with(query=None)), request.url.params))
    return httpx.MockTransport(handler)


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

    The league id, the season, and the points key do not change what it gives, because the fixtures hold one league.
    """

    def __init__(self, raw_dir: Path = RAW_FIXTURES, history_root: Path = HISTORY_FIXTURES,
                 fetched: datetime = FIXTURE_FETCHED):
        self.raw_dir = raw_dir
        self.history_root = history_root
        self.fetched = fetched

    def fetch_week(
            self, league_id: str, season: int, week: int, raw_dir: Path, tz: ZoneInfo,
            last_regular_week: int, last_season_week: int, points_key: str) -> RawWeek:
        shutil.copytree(self.raw_dir, raw_dir, dirs_exist_ok=True)
        return load_raw(raw_dir)

    def fetch_settings(self, league_id: str, cache: Path) -> LeagueSettings:
        return league_settings(load_raw(self.raw_dir).league)

    def fetch_live(self, league_id: str) -> tuple[RawWeek, datetime]:
        return load_raw(self.raw_dir), self.fetched

    def fetch_past_leg(self, league_id: str, season: int, week: int, out_dir: Path) -> RawPastWeek:
        saved = self.history_root / f"week-{week:02d}"
        shutil.copytree(saved, out_dir, dirs_exist_ok=True)
        return RawPastWeek.model_validate({f.stem: json.loads(f.read_text(encoding="utf-8"))
                                           for f in saved.glob("*.json")})

    def fetch_players(self) -> dict[str, dict]:
        return load_raw(self.raw_dir).players

    def fetch_projections(
            self, season: int, week: int, last_regular_week: int, points_key: str) -> list[RawAheadWeek]:
        return load_raw(self.raw_dir).projections_ahead or []


# The annotation makes pyright prove that the fake has the six fetches of the protocol, with the same types.
FIXTURE_PROVIDER: Provider = FixtureProvider()


@dataclass(frozen=True)
class WriterCall:
    """The arguments of one call to `Writer.parse`."""
    content: str | list[dict]
    output_model: type[BaseModel]
    system: str | None
    cache_ttl: str | None
    effort: str
    tools: list[dict] | None


class FakeWriter:
    """A writer that gives its answers in order and keeps each call in `calls`. It never calls Claude.

    With no answer left, it raises WriterError, as a failed Claude call does. So an empty FakeWriter fails each call.
    """

    def __init__(self, answers: list[BaseModel] | None = None):
        self.answers = list(answers or [])
        self.calls: list[WriterCall] = []

    def parse(
        self, content: str | list[dict], output_model: type[BaseModel], system: str | None = None,
        cache_ttl: str | None = None, effort: str = "high", tools: list[dict] | None = None,
    ) -> BaseModel:
        self.calls.append(WriterCall(content, output_model, system, cache_ttl, effort, tools))
        if not self.answers:
            raise WriterError(f"the fake writer has no answer left for {output_model.__name__}")
        answer = self.answers.pop(0)
        # A test that queues the wrong model fails here with a plain message, not later on a missing field.
        if not isinstance(answer, output_model):
            raise TypeError(
                f"the next answer is a {type(answer).__name__}, and the call asks for {output_model.__name__}")
        return answer


# The annotation makes pyright prove that the fake has the method of the Writer protocol, with the same types.
FAKE_WRITER: Writer = FakeWriter()
