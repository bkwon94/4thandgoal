"""
Shared pytest fixtures for the Cornerstone Weekly tests.
They give tests the path to the recorded Sleeper data and the saved week data.
The `week_8` fixture builds the bundle of week 8 from them.
"""
import json
import re
import shutil
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from cpc import cpc_client
from fakes import FakeWriter, no_news

from league.history import load_history
from league.models import ChartValues, InjuryPlay, NflverseWeek
from league.nflverse import nflverse_week
from league.parse import parse_trades, parse_week
from league.paths import chart_read, history_root, week_dir
from league.provider.raw import RawWeek
from league.provider.sleeper import load_raw
from league.snapshot import week_snapshot
from league.trades import default_cutoff, trades_for_week

CLIENT = cpc_client()

ET = ZoneInfo("America/New_York")


def build_bundle(*args, **kwargs):
    """The week build of the pipeline, imported at the call. The API tests load this file, and the API env holds no
    core package, so an import at load of the wire code, which imports the rankings package, fails there (AT-31)."""
    from cornerstone.sheet import build_bundle as build

    return build(*args, **kwargs)

# The trend reason gives share percents and the air yards per target, such as "52%" and "6.1 air yards per target".
_TREND_NUMBERS = re.compile(r"\b\d+%|\b\d+\.\d air yards per target")


def save_chart_read(nfl: Path, week: int, read: Path) -> None:
    """Save the chart read file `read` as the saved read of `week` for the chart of the client, under `nfl`."""
    path = chart_read(nfl, CLIENT.chart, week)
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(read, path)


def strip_trend_numbers(reason: str) -> str:
    """The trend reason with its share percents and air yards removed, so a check can find any other number."""
    return _TREND_NUMBERS.sub("", reason)


def with_carries(snap, player_id: str, carries: dict[int, float]):
    """The snapshot with the player's carries set to `carries`, keyed by week. His team's carries change with his."""
    weeks = dict(snap.stats.weeks)
    for week, count in carries.items():
        past = weeks[week]
        stats = {**past.stats, player_id: {**past.stats[player_id], "rush_att": count}}
        weeks[week] = past.model_copy(update={"stats": stats})
    return snap.model_copy(update={"stats": snap.stats.model_copy(update={"weeks": weeks})})


# The week 6 players file holds the rostered players only, so the free agent tests add these. Each back has a stat
# line in the saved weeks but 80001, so each but 80001 has a position rank. The status fields follow Sleeper.
FREE_AGENTS = {
    # Achane is Inactive with no out tag, so the waiver pool leaves him out.
    "9226": {"full_name": "De'Von Achane", "position": "RB", "team": "MIA", "status": "Inactive", "active": True},
    # Rodriguez is on injured reserve with no out tag, so the waiver pool leaves him out.
    "10219": {"full_name": "Chris Rodriguez", "position": "RB", "team": "JAX", "status": "Injured Reserve",
              "active": True},
    "9225": {"full_name": "Tank Bigsby", "position": "RB", "team": "PHI", "status": "Active", "active": True},
    # Perine is Inactive and out, so the waiver pool keeps him as a stash.
    "4147": {"full_name": "Samaje Perine", "position": "RB", "team": "CIN", "status": "Inactive", "active": True,
             "injury_status": "IR"},
    # Gainwell has no NFL team, so the waiver pool leaves him out.
    "7567": {"full_name": "Kenny Gainwell", "position": "RB", "team": None, "status": "Active", "active": True},
    "80001": {"full_name": "No Line Back", "position": "RB", "team": "KC", "status": "Active", "active": True},
    "2505": {"full_name": "Darren Waller", "position": "TE", "team": "CAR", "status": "Active", "active": True},
}


def with_free_agents(raw: RawWeek, players: dict[str, dict] | None = None) -> RawWeek:
    """The raw data with FREE_AGENTS, or `players`, added to the players file."""
    return raw.model_copy(update={"players": {**raw.players, **(FREE_AGENTS if players is None else players)}})


@pytest.fixture
def free_agent_raw_dir(tmp_path, fixture_raw_dir) -> Path:
    """A copy of the week 6 raw folder with FREE_AGENTS in its players file."""
    raw_dir = tmp_path / "raw"
    shutil.copytree(fixture_raw_dir, raw_dir)
    players = raw_dir / "players.json"
    players.write_text(json.dumps({**json.loads(players.read_text()), **FREE_AGENTS}))
    return raw_dir


@pytest.fixture
def fake_writer() -> FakeWriter:
    """A writer with no answer. A test that must not call Claude passes it and asserts `calls == []`."""
    return FakeWriter()


@pytest.fixture
def fixture_raw_dir() -> Path:
    return Path(__file__).parent / "fixtures" / "2026" / "week-06" / "raw"


@pytest.fixture
def fixture_history_root() -> Path:
    return Path(__file__).parent / "fixtures" / "2026" / "history"


@pytest.fixture
def hbundle(fixture_raw_dir, fixture_history_root):
    raw = load_raw(fixture_raw_dir)
    return build_bundle(parse_week(raw), news=lambda pid: [],
                        history=load_history(fixture_history_root, raw, week=6),
                        snapshot=week_snapshot(raw, fixture_history_root, 6, client=CLIENT), client=CLIENT)


def _window(raw, h):
    # The window ends at noon on purpose. It keeps the Tuesday trade as the sixth trade, the only late trade in the fixture.
    return trades_for_week(parse_trades(raw.transactions), h.weeks[5].trades,
                           default_cutoff(date(2026, 9, 9), 6, ET), datetime(2026, 10, 20, 12, 0, tzinfo=ET))


def _trade_bundle(raw_dir, history_root, nfl=None):
    """The week 6 bundle with history and trades. A given nflverse week adds the drop facts."""
    raw = load_raw(raw_dir)
    h = load_history(history_root, raw, week=6)
    return build_bundle(parse_week(raw), news=lambda pid: [], history=h, trades=_window(raw, h), nfl=nfl,
                        snapshot=week_snapshot(raw, history_root, 6, client=CLIENT), client=CLIENT)


@pytest.fixture
def tbundle(fixture_raw_dir, fixture_history_root):
    return _trade_bundle(fixture_raw_dir, fixture_history_root)


@pytest.fixture
def chart_week6() -> ChartValues:
    path = Path(__file__).parent / "fixtures" / "charts" / "week-06.json"
    return ChartValues.model_validate_json(path.read_text(encoding="utf-8"))


@pytest.fixture
def dbundle(fixture_raw_dir, fixture_history_root, nfl_week6):
    return _trade_bundle(fixture_raw_dir, fixture_history_root, nfl=nfl_week6)


@pytest.fixture
def fixture_nflverse_dir() -> Path:
    return Path(__file__).parent / "fixtures" / "nflverse"


@pytest.fixture
def nfl_week6(fixture_nflverse_dir, fixture_raw_dir, tmp_path) -> NflverseWeek:
    raw = load_raw(fixture_raw_dir)
    # The fetch raises, so the test fails if the code tries the network instead of the cache.
    def no_network(url):
        raise AssertionError(f"network call to {url}")
    cache = tmp_path / "nflverse"
    cache.mkdir()
    for f in fixture_nflverse_dir.iterdir():
        shutil.copy(f, cache / f.name)
    starters = sorted({p for entry in raw.matchups for p in entry.starters or [] if p != "0"})
    return nflverse_week(2026, 6, starters, raw.players, cache, fetch=no_network,
                         scoring=raw.league.scoring_settings)


# The week 6 fixture has no kickoff times, so the game story tests set their own. Every team plays the early Sunday
# games but New England and San Francisco, which play on Monday night. Then matchup 3 flips on Monday: Amon-Ra Dawg
# Your Team leads by 12.24 after Sunday, and Drake Maye (NE) and the 49ers defense win it for Maye d'force B with U.
STORY_SUNDAY = datetime(2026, 10, 18, 13, 0, tzinfo=ET)
STORY_MONDAY = datetime(2026, 10, 19, 20, 15, tzinfo=ET)
# Ladd McConkey (M5) is listed Out with a concussion in the fixture, so he gets the injury play.
STORY_PLAY = InjuryPlay(quarter=1, clock="03:06", away="LAC", home="KC")


@pytest.fixture
def story_nfl(fixture_raw_dir) -> NflverseWeek:
    """An nflverse week with only the injury play and the kickoffs, the two inputs of the game story facts."""
    week = parse_week(load_raw(fixture_raw_dir))
    teams = {line.nfl_team for m in week.matchups for s in (m.a, m.b) for line in s.lines if line.nfl_team}
    kickoffs = {t: STORY_MONDAY if t in ("NE", "SF") else STORY_SUNDAY for t in teams}
    return NflverseWeek(sources={}, gsis={}, drops=None, injuries=None, injury_plays={"11635": STORY_PLAY},
                        kickoffs=kickoffs)


@pytest.fixture
def story_bundle(fixture_raw_dir, story_nfl):
    return build_bundle(parse_week(load_raw(fixture_raw_dir)), news=lambda pid: [], nfl=story_nfl, client=CLIENT)


SAVED = Path(__file__).resolve().parents[3] / "clients" / "cpc" / "data" / "2026"


def saved_repo(tmp_path, week):
    """A folder of links to the saved raw data of `week`, the saved history, and the saved facts of the week before.
    cpc_client(at=folder) reads it."""
    for path in (week_dir(tmp_path, 2026, week), history_root(tmp_path, 2026).parent):
        path.mkdir(parents=True, exist_ok=True)
    (week_dir(tmp_path, 2026, week) / "raw").symlink_to(SAVED / f"week-{week:02d}" / "raw")
    history_root(tmp_path, 2026).symlink_to(SAVED / "history")
    before = week_dir(tmp_path, 2026, week - 1)
    before.mkdir(parents=True)
    shutil.copy(SAVED / f"week-{week - 1:02d}" / "facts.json", before / "facts.json")
    return tmp_path


@pytest.fixture(scope="module")
def week_8(tmp_path_factory):
    """The week 8 bundle from the saved week 8 data, with the saved week 7 odds as the odds before."""
    # The import sits here, not at the top: the API tests load this file, and the API env holds no waiver package, which
    # the build imports. Only the pipeline tests take this fixture.
    from cornerstone.pipeline import make_bundle

    repo = saved_repo(tmp_path_factory.mktemp("repo"), 8)
    bundle, _ = make_bundle(2026, 8, news=no_news, client=cpc_client(at=repo))
    return bundle


# The midseason build of CPC week 8 takes about 3 s, and most midseason tests only read what it writes. Each fixture
# below builds once per session, or once per xdist worker, for one set of inputs. The tests that only read the build
# share it. A test that writes or changes the build folder keeps its own build in `tmp_path`.
@pytest.fixture(scope="session")
def cpc_midseason(tmp_path_factory):
    """The client and the midseason.json of one CPC week 8 build with a writer that fails each call, at 500 runs."""
    # The import sits here, not at the top: the API tests load this file, and the API env holds no midseason package.
    from test_midseason import CPC_PROVIDER, _call, _cpc_week_8, build_week_8

    client = _cpc_week_8(tmp_path_factory.mktemp("cpc-midseason"))
    return client, build_week_8(_call(), client=client, provider=CPC_PROVIDER)


@pytest.fixture(scope="session")
def cpc_midseason_full(tmp_path_factory):
    """The client and the midseason.json of one CPC week 8 build with a writer that fails each call, at SIM_RUNS."""
    from test_midseason import CPC_PROVIDER, _call, _cpc_week_8, build_week_8

    from sim.tunables import SIM_RUNS

    client = _cpc_week_8(tmp_path_factory.mktemp("cpc-midseason-full"))
    return client, build_week_8(_call(), client=client, provider=CPC_PROVIDER, sim_runs=SIM_RUNS)


@pytest.fixture(scope="session")
def cpc_midseason_clean(tmp_path_factory):
    """The client, the midseason.json, and the writer of one clean CPC week 8 build at SIM_RUNS. The writer gives the
    answers of CLEAN_BUILD, so each prose block keeps the blurb of the writer. A test reads `writer.calls`."""
    from functools import partial

    from test_midseason import CLEAN_BUILD, CPC_PROVIDER, _cpc_week_8, build_week_8

    from facts.writer import claude_call
    from sim.tunables import SIM_RUNS

    client = _cpc_week_8(tmp_path_factory.mktemp("cpc-midseason-clean"))
    writer = FakeWriter(list(CLEAN_BUILD))
    out = build_week_8(partial(claude_call, writer=writer), client=client, provider=CPC_PROVIDER, sim_runs=SIM_RUNS)
    return client, out, writer
