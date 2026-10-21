"""
Shared pytest fixtures for the Cornerstone Weekly tests.
They give tests the path to the recorded Sleeper data.
"""
import shutil
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from cornerstone.history import load_history
from cornerstone.models import ChartValues, NflverseWeek, Trade
from cornerstone.nflverse import nflverse_week
from cornerstone.parse import parse_trades, parse_week
from cornerstone.sheet import build_bundle
from cornerstone.sleeper import load_raw
from cornerstone.trades import default_cutoff, trades_for_week

ET = ZoneInfo("America/New_York")


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
                        history=load_history(fixture_history_root, raw, week=6))


def _trade_bundle(raw_dir, history_root, nfl=None, chart=None):
    """The week 6 bundle with history and trades. A given nflverse week adds the drop facts.

    Chart values, when given, add the trade value facts.
    """
    raw = load_raw(raw_dir)
    h = load_history(history_root, raw, week=6)
    trades = trades_for_week(parse_trades(raw["transactions"]), h.weeks[5].trades,
                             default_cutoff(date(2026, 9, 9), 6), datetime(2026, 10, 20, 12, 0, tzinfo=ET))
    return build_bundle(parse_week(raw), news=lambda pid: [], history=h, trades=trades, nfl=nfl, chart=chart)


def _decisive_trade(week):
    """A one-way trade in which a loser gives the winner a starter who scored more than the margin.

    It returns the trade, the winner, and the loser. The week 6 data has no decisive swing of its own.
    """
    for m in week.matchups:
        winner, loser = (m.a, m.b) if m.a.points > m.b.points else (m.b, m.a)
        big = max((l for l in winner.lines if l.started), key=lambda l: l.points)
        if big.points > winner.points - loser.points:
            trade = Trade(transaction_id="decisive", created=datetime(2026, 10, 14, tzinfo=ET),
                          roster_ids=[loser.roster_id, winner.roster_id],
                          adds={big.player_id: winner.roster_id}, drops={big.player_id: loser.roster_id},
                          draft_picks=[])
            return trade, winner.roster_id, loser.roster_id
    raise AssertionError("no matchup has a starter who scored more than the margin")


@pytest.fixture
def tbundle(fixture_raw_dir, fixture_history_root):
    return _trade_bundle(fixture_raw_dir, fixture_history_root)


@pytest.fixture
def chart_week6() -> ChartValues:
    path = Path(__file__).parent / "fixtures" / "charts" / "week-06.json"
    return ChartValues.model_validate_json(path.read_text(encoding="utf-8"))


@pytest.fixture
def vbundle(fixture_raw_dir, fixture_history_root, chart_week6):
    return _trade_bundle(fixture_raw_dir, fixture_history_root, chart=chart_week6)


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
    starters = sorted({p for entry in raw["matchups"] for p in entry["starters"] if p != "0"})
    return nflverse_week(2026, 6, starters, raw["players"], cache, fetch=no_network)
