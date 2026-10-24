"""
Tests for the sneaky and stash buckets of the waiver board.
They feed hand-set usage, depth charts, injuries, and return weeks at the engine seam and read the buckets.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from cornerstone.models import NflverseWeek, UsageWeek
from cornerstone.sleeper import load_raw
from cornerstone.slow_sources import SlowSources
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


def _depth(charts, injuries=None):
    """The slow sources with `charts`, team to position to Sleeper IDs, written as the gsis_ids of _raw."""
    return SlowSources(depth_charts={team: {pos: [f"G{pid}" for pid in ids] for pos, ids in by_pos.items()}
                                     for team, by_pos in charts.items()},
                       id_map={}, injuries=injuries)


def _top_backs():
    """Three RBs of another team who project the most of the pool, so they fill the RB places of best adds."""
    return {f"8090{i}": _player("RB", f"Top Back {i}", team="BUF") for i in range(3)}


def test_a_player_one_slot_below_an_injured_starter_lands_in_sneaky_with_the_story_fact(fixture_raw_dir):
    # The starter is rostered by no one here, but his status comes from the players file all the same.
    players = {"80001": _player("RB", "Michael Pittman", injury="Out"), "80002": _player("RB", "Jake Bernard"),
               "80003": _player("RB", "Third Guy")} | _top_backs()
    raw = _raw(fixture_raw_dir, players, {"80001": 12.0, "80002": 6.0, "80003": 3.0} | dict.fromkeys(_top_backs(), 30.0))
    board = waiver_board(raw, 6, BUILT, slow=_depth({"KC": {"RB": ["80001", "80002", "80003"]}}))
    sneaky = board.buckets["sneaky"]
    assert _ids(sneaky) == ["80002"]
    assert sneaky[0].reason == "behind_injury"
    story = sneaky[0].facts[-1]
    assert story.text == "Michael Pittman is out, and Jake Bernard is next on the depth chart."
    assert "Michael Pittman" in story.players


def test_a_player_out_with_a_return_week_and_a_top_half_projection_lands_in_stashes(fixture_raw_dir):
    players = {"80001": _player("WR", "Hurt Star", injury="Out"), "80002": _player("WR", "Low Guy"),
               "80003": _player("WR", "Mid Guy")}
    raw = _raw(fixture_raw_dir, players, {"80001": 15.0, "80002": 4.0, "80003": 8.0})
    stashes = waiver_board(raw, 6, BUILT, returns={"80001": 9}).buckets["stashes"]
    assert _ids(stashes) == ["80001"]
    assert stashes[0].reason == "return"
