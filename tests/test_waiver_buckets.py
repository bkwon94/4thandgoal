"""
Tests for the sneaky and stash buckets of the waiver board.
They feed hand-set usage, depth charts, injuries, and return weeks at the engine seam and read the buckets.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from cornerstone.models import NflverseWeek, UsageWeek
from cornerstone.sleeper import load_raw
from cornerstone.waiver import waiver_board

BUILT = datetime(2026, 10, 20, 21, 0, tzinfo=ZoneInfo("America/New_York"))


def _player(position, name, team="KC", injury=None):
    """A pool player with a gsis_id of his Sleeper ID with a G in front, so a depth chart can name him."""
    return {"position": position, "team": team, "status": "Active", "active": True, "full_name": name,
            "injury_status": injury}


def _raw(fixture_raw_dir, players, per_week):
    """The week 6 raw with `players` added and a flat projection per week, weeks 7 to 17, for each ID in `per_week`."""
    raw = load_raw(fixture_raw_dir)
    raw["players"] = {**raw["players"], **{pid: {**e, "gsis_id": f"G{pid}"} for pid, e in players.items()}}
    raw["projections_ahead"] = [{"week": w, "projections": dict(per_week)} for w in range(7, 18)]
    return raw


def _usage(week, snap_share, targets):
    return UsageWeek(week=week, team="KC", snaps=snap_share, snap_share=snap_share, targets=targets,
                     target_share=4 * targets, carries=0, carry_share=0, red_zone_touches=0)


def _nfl(usage):
    return NflverseWeek(sources={}, gsis={}, drops=None, injuries=None, usage=usage, environment={})


def _ids(bucket):
    return [p.player_id for p in bucket]


def test_a_rising_snap_share_with_a_flat_projection_lands_in_sneaky_and_not_in_best_adds(fixture_raw_dir):
    # Four WRs rise by the same amount, so each has a usage score of 1. Three project the most of the pool and
    # take the three WR places of best adds. The fourth projects the least, so his projection is flat.
    risers = ["80001", "80002", "80003", "80004"]
    players = {pid: _player("WR", f"Riser {pid}") for pid in risers}
    players |= {f"8010{i}": _player("WR", f"Steady {i}") for i in range(4)}
    per_week = {"80001": 2.0, "80002": 30.0, "80003": 31.0, "80004": 32.0} | {f"8010{i}": 10.0 + i for i in range(4)}
    usage = {pid: [_usage(5, 30, 2), _usage(6, 75, 7)] for pid in risers}
    board = waiver_board(_raw(fixture_raw_dir, players, per_week), 6, BUILT, _nfl(usage))
    assert "80001" not in _ids(board.buckets["best_adds"])
    sneaky = board.buckets["sneaky"]
    assert _ids(sneaky) == ["80001"]
    assert sneaky[0].reason == "usage_rise"
