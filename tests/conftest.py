"""
Shared pytest fixtures for the Cornerstone Weekly tests.
They give tests the path to the recorded Sleeper data.
"""
import json
import re
import shutil
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from cornerstone.config import cornerstone_config
from cornerstone.history import load_history
from cornerstone.models import ChartValues, NflverseWeek
from cornerstone.nflverse import nflverse_week
from cornerstone.parse import parse_trades, parse_week
from cornerstone.provider.raw import RawWeek
from cornerstone.provider.sleeper import load_raw
from cornerstone.sheet import build_bundle
from cornerstone.snapshot import week_snapshot
from cornerstone.trades import default_cutoff, trades_for_week

CONFIG = cornerstone_config()

ET = ZoneInfo("America/New_York")

# The trend reason gives share percents, WOPR values, and the weeks behind them, such as "52%", "WOPR 55", and
# "weeks 4 and 5".
_TREND_NUMBERS = re.compile(r"\b\d+%|\bWOPR -?\d+|\bweeks? \d+(?:(?:, | and )\d+)*")


def strip_trend_numbers(reason: str) -> str:
    """The trend reason with its share percents and share weeks removed, so a check can find any other number."""
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
                        snapshot=week_snapshot(raw, fixture_history_root, 6, config=CONFIG), config=CONFIG)


def _window(raw, h):
    # The window ends at noon on purpose. It keeps the Tuesday trade as the sixth trade, the only late trade in the fixture.
    return trades_for_week(parse_trades(raw.transactions), h.weeks[5].trades,
                           default_cutoff(date(2026, 9, 9), 6, ET), datetime(2026, 10, 20, 12, 0, tzinfo=ET))


def _trade_bundle(raw_dir, history_root, nfl=None):
    """The week 6 bundle with history and trades. A given nflverse week adds the drop facts."""
    raw = load_raw(raw_dir)
    h = load_history(history_root, raw, week=6)
    return build_bundle(parse_week(raw), news=lambda pid: [], history=h, trades=_window(raw, h), nfl=nfl,
                        snapshot=week_snapshot(raw, history_root, 6, config=CONFIG), config=CONFIG)


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
