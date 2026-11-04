"""
Tests for the Provider protocol: the Sleeper provider and the fixture fake both satisfy it.
Pyright checks the annotated assignments here, and isinstance checks the same at runtime.
"""
import shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from cpc import cpc_client
from fakes import HISTORY_FIXTURES, FixtureProvider, fixture_nflverse, no_claims, no_news

from cornerstone.pipeline import run_build
from cornerstone.writer import WriterError
from league.history import fetch_history
from league.paths import history_root, week_dir
from league.provider.base import Provider
from league.provider.raw import RawPastWeek, RawWeek
from league.provider.sleeper import SleeperProvider

CLIENT = cpc_client()


class RecordedProvider(FixtureProvider):
    """The fixture provider. It keeps the league id and the timezone of each week fetch."""

    def __init__(self):
        super().__init__()
        self.week_calls: list[tuple[str, int, int, ZoneInfo]] = []

    def fetch_week(
            self, league_id: str, season: int, week: int, raw_dir: Path, tz: ZoneInfo,
            last_regular_week: int, last_season_week: int, points_key: str) -> RawWeek:
        self.week_calls.append((league_id, season, week, tz))
        return super().fetch_week(league_id, season, week, raw_dir, tz, last_regular_week, last_season_week,
                                  points_key)


def _no_claude(system, user, model):
    # Every attempt fails, so every chapter gets its template blurb and the build makes no Claude call.
    raise WriterError("this build makes no Claude call")


def test_the_sleeper_provider_satisfies_the_protocol(tmp_path):
    provider: Provider = SleeperProvider(tmp_path)
    assert isinstance(provider, Provider)


def test_the_fixture_provider_satisfies_the_protocol():
    provider: Provider = FixtureProvider()
    assert isinstance(provider, Provider)


def test_an_object_with_four_of_the_five_fetches_is_no_provider():
    class NoPlayers:
        def fetch_week(self, league_id, season, week, raw_dir, tz, last_regular_week, last_season_week,
                       points_key): ...
        def fetch_live(self, league_id): ...
        def fetch_past_leg(self, league_id, season, week, out_dir): ...
        def fetch_projections(self, season, week, last_regular_week, points_key): ...

    assert not isinstance(NoPlayers(), Provider)


def test_a_build_with_a_fetch_reads_the_league_id_and_the_timezone_from_the_config(tmp_path):
    provider = RecordedProvider()
    shutil.copytree(HISTORY_FIXTURES, history_root(tmp_path, 2026))

    run_build(tmp_path, 2026, 6, _no_claude, fetch=True, news=no_news, fetch_bytes=lambda url: None,
              nflverse=fixture_nflverse(tmp_path / "nflverse"), research=no_claims,
              started=datetime(2026, 10, 21, 10, 0, tzinfo=CLIENT.tz), client=cpc_client(at=tmp_path), provider=provider)

    assert provider.week_calls == [(CLIENT.league_id(2026), 2026, 6, CLIENT.tz)]
    assert (week_dir(tmp_path, 2026, 6) / "facts.json").exists()


def test_the_history_fetch_saves_each_missing_week_through_the_fixture_provider(tmp_path):
    root = tmp_path / "history"
    fetched = fetch_history(CLIENT.league_id(2026), 2026, 2, root, fetch=FixtureProvider().fetch_past_leg)

    assert fetched == [1, 2]
    assert (root / "week-02" / "matchups.json").exists()


def test_the_fixture_past_leg_gives_the_raw_models(tmp_path):
    past = FixtureProvider().fetch_past_leg(CLIENT.league_id(2026), 2026, 3, tmp_path / "week-03")
    assert isinstance(past, RawPastWeek)
    assert past.matchups
