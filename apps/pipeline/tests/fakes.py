"""
No-network stand-ins for the build inputs: Sleeper, Claude, Jev, news, nflverse, the expert search, and any URL fetch.
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
from pydantic import BaseModel, TypeAdapter

from league.claude_errors import WriterError
from league.claude_port import Writer
from league.jev_port import Jev, JevAnswers, JevError, NoulQuestion
from league.league_settings import LeagueSettings
from league.models import ResearchOut
from league.nflverse import nflverse_week
from league.provider.base import Provider
from league.provider.raw import RawAheadWeek, RawDraft, RawPastWeek, RawRoster, RawWeek
from league.provider.sleeper import DRAFT_FILE, PICKS_FILE, league_settings, load_draft, load_raw

NFLVERSE_FIXTURES = Path(__file__).parent / "fixtures" / "nflverse"
RAW_FIXTURES = Path(__file__).parent / "fixtures" / "2026" / "week-06" / "raw"
HISTORY_FIXTURES = Path(__file__).parent / "fixtures" / "2026" / "history"
# The real drafts of 2026 as Sleeper sent them on 2026-11-05: the CPC auction and the NorCal snake.
CPC_DRAFT_FIXTURES = Path(__file__).parent / "fixtures" / "2026" / "draft" / "cpc"
NORCAL_DRAFT_FIXTURES = Path(__file__).parent / "fixtures" / "2026" / "draft" / "norcal"
# The full transactions of CPC weeks 1 to 8, as Sleeper gave them on 2026-11-05, after the waiver run of each week.
CPC_TRANSACTIONS = Path(__file__).parent / "fixtures" / "2026" / "cpc-transactions"
# The full transactions of NorCal weeks 1 to 8, as Sleeper gave them on 2026-11-05.
NORCAL_TRANSACTIONS = Path(__file__).parent / "fixtures" / "2026" / "norcal-transactions"
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
    """A provider that reads the recorded week 6 files, the week 1 to 5 history, and the CPC draft. It never calls the
    network.

    The league id, the season, and the points key do not change what it gives, because the fixtures hold one league.
    With `transactions`, a past leg gives the file week-NN.json of that folder as its transactions, so a test reads
    the full week that Sleeper gives after the waiver run. With `rosters_now`, the live fetch gives the rosters of that
    file in place of the rosters of the raw week, so a test reads the rosters of a later day.
    """

    def __init__(self, raw_dir: Path = RAW_FIXTURES, history_root: Path = HISTORY_FIXTURES,
                 fetched: datetime = FIXTURE_FETCHED, transactions: Path | None = None,
                 draft_dir: Path = CPC_DRAFT_FIXTURES, rosters_now: Path | None = None):
        self.raw_dir = raw_dir
        self.history_root = history_root
        self.fetched = fetched
        self.draft_dir = draft_dir
        self.transactions = transactions
        self.rosters_now = rosters_now

    def fetch_week(
            self, league_id: str, season: int, week: int, raw_dir: Path, tz: ZoneInfo,
            last_regular_week: int, last_season_week: int, points_key: str) -> RawWeek:
        shutil.copytree(self.raw_dir, raw_dir, dirs_exist_ok=True)
        return load_raw(raw_dir)

    def fetch_settings(self, league_id: str, cache: Path) -> LeagueSettings:
        return league_settings(load_raw(self.raw_dir).league)

    def fetch_live(self, league_id: str) -> tuple[RawWeek, datetime]:
        raw = load_raw(self.raw_dir)
        if self.rosters_now is not None:
            rosters = TypeAdapter(list[RawRoster]).validate_json(self.rosters_now.read_text(encoding="utf-8"))
            raw = raw.model_copy(update={"rosters": rosters})
        return raw, self.fetched

    def fetch_past_leg(self, league_id: str, season: int, week: int, out_dir: Path) -> RawPastWeek:
        saved = self.history_root / f"week-{week:02d}"
        shutil.copytree(saved, out_dir, dirs_exist_ok=True)
        files = {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in saved.glob("*.json")}
        if self.transactions is not None:
            shutil.copy(self.transactions / f"week-{week:02d}.json", out_dir / "transactions.json")
            files["transactions"] = json.loads((out_dir / "transactions.json").read_text(encoding="utf-8"))
        return RawPastWeek.model_validate(files)

    def fetch_players(self) -> dict[str, dict]:
        return load_raw(self.raw_dir).players

    def fetch_projections(
            self, season: int, week: int, last_regular_week: int, points_key: str) -> list[RawAheadWeek]:
        return load_raw(self.raw_dir).projections_ahead or []

    def fetch_draft(self, league_id: str, out_dir: Path) -> RawDraft:
        out_dir.mkdir(parents=True, exist_ok=True)
        for name in (DRAFT_FILE, PICKS_FILE):
            shutil.copy(self.draft_dir / name, out_dir / name)
        return load_draft(out_dir)


# The annotation makes pyright prove that the fake has the seven fetches of the protocol, with the same types.
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


@dataclass(frozen=True)
class JevRequest:
    """The arguments of one call to `Jev.ask`."""
    state: dict
    questions: dict[str, NoulQuestion]


class FakeJev:
    """A Jev that gives `yes` for each question, or the value in `answers` for its key, and keeps each request in
    `requests`. It never calls TypeSafe.

    With `error`, each call raises that JevError, as a failed TypeSafe call does.
    """

    MODEL = "jev-fake"

    def __init__(self, yes: float = 0.9, answers: dict[str, float] | None = None, error: JevError | None = None):
        self.yes = yes
        self.answers = dict(answers or {})
        self.error = error
        self.requests: list[JevRequest] = []

    def ask(self, state: dict, questions: dict[str, NoulQuestion]) -> JevAnswers:
        self.requests.append(JevRequest(state, questions))
        if self.error is not None:
            raise self.error
        nouls = {key: self.answers.get(key, self.yes) for key in questions}
        return JevAnswers(model=self.MODEL, nouls=nouls, input_tokens=100 * len(questions))


# The annotation makes pyright prove that the fake has the method of the Jev protocol, with the same types.
FAKE_JEV: Jev = FakeJev()
