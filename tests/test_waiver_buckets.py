"""
Tests for the sneaky and stash buckets of the waiver board.
They feed hand-set usage, depth charts, injuries, and return weeks at the engine seam and read the buckets.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from cornerstone.config import cornerstone_config
from cornerstone.models import NflverseWeek, UsageWeek
from cornerstone.nflverse import TeamSchedule
from cornerstone.sheet import NUMBER_TOKEN
from cornerstone.provider.sleeper import load_raw
from cornerstone.slow_sources import SlowSources
from cornerstone.waiver import waiver_board
from cornerstone.waiver_buckets import return_week

CONFIG = cornerstone_config()

BUILT = datetime(2026, 10, 20, 21, 0, tzinfo=ZoneInfo("America/New_York"))


def _player(position, name, team="KC", injury=None, status="Active"):
    """A pool player. _raw gives him a gsis_id of his Sleeper ID with a G in front, so a depth chart can name him."""
    return {"position": position, "team": team, "status": status, "active": True, "full_name": name,
            "injury_status": injury}


def _raw(fixture_raw_dir, players, per_week):
    """The week 6 raw with `players` added and a flat projection per week, weeks 7 to 17, for each ID in `per_week`."""
    raw = load_raw(fixture_raw_dir)
    raw.players = {**raw.players, **{pid: {**e, "gsis_id": f"G{pid}"} for pid, e in players.items()}}
    raw.projections_ahead = [{"week": w, "projections": dict(per_week)} for w in range(7, 18)]
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
    board = waiver_board(_raw(fixture_raw_dir, players, per_week), 6, BUILT, _nfl(usage), config=CONFIG)
    assert "80001" not in _ids(board.buckets["best_adds"])
    sneaky = board.buckets["sneaky"]
    assert _ids(sneaky) == ["80001"]
    assert sneaky[0].reason == "usage_rise"


def _depth(charts, injuries=None, schedules=None):
    """The slow sources with `charts`, team to position to Sleeper IDs, written as the gsis_ids of _raw."""
    return SlowSources(depth_charts={team: {pos: [f"G{pid}" for pid in ids] for pos, ids in by_pos.items()}
                                     for team, by_pos in charts.items()},
                       id_map={}, injuries=injuries, schedules=schedules)


def _top_backs():
    """Three RBs of another team who project the most of the pool, so they fill the RB places of best adds."""
    return {f"8090{i}": _player("RB", f"Top Back {name}", team="BUF") for i, name in enumerate("ABC")}


def test_a_player_one_slot_below_an_injured_starter_lands_in_sneaky_with_the_story_fact(fixture_raw_dir):
    # The starter is rostered by no one here, but his status comes from the players file all the same.
    players = {"80001": _player("RB", "Michael Pittman", injury="Out"), "80002": _player("RB", "Jake Bernard"),
               "80003": _player("RB", "Third Guy")} | _top_backs()
    per_week = {"80001": 12.0, "80002": 6.0, "80003": 3.0} | dict.fromkeys(_top_backs(), 30.0)
    raw = _raw(fixture_raw_dir, players, per_week)
    board = waiver_board(raw, 6, BUILT, slow=_depth({"KC": {"RB": ["80001", "80002", "80003"]}}), config=CONFIG)
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
    stashes = waiver_board(raw, 6, BUILT, returns={"80001": 9}, config=CONFIG).buckets["stashes"]
    assert _ids(stashes) == ["80001"]
    assert stashes[0].reason == "return"


def test_a_player_out_with_no_return_week_or_one_past_the_season_stays_out_of_stashes(fixture_raw_dir):
    players = {"80001": _player("WR", "No Date", injury="Out"), "80002": _player("WR", "Late Date", injury="IR"),
               "80003": _player("WR", "Low Guy")}
    raw = _raw(fixture_raw_dir, players, {"80001": 15.0, "80002": 14.0, "80003": 4.0})
    # The injury report lists the first player as out in week 6 only, so it gives no return week.
    slow = SlowSources(depth_charts=None, id_map={}, injuries={"G80001": {6: "Out"}})
    assert waiver_board(raw, 6, BUILT, slow=slow, returns={"80002": 18}, config=CONFIG).buckets["stashes"] == []


def test_the_return_week_reads_the_returns_file_first_and_the_injury_report_second():
    injuries = {"G1": {6: "Out", 7: "Out", 8: "Questionable"}}
    assert return_week("1", "G1", 6, {"1": 10}, injuries) == 10
    assert return_week("1", "G1", 6, {}, injuries) == 8
    assert return_week("1", "G1", 6, {}, None) is None


# A rostered RB of the fixture with no injury.
ROSTERED_RB = "11584"


def _every_rb(raw, points):
    """A flat projection for every RB with a team in the players file, rostered or not."""
    return {pid: points for pid, e in raw.players.items() if e.get("position") == "RB" and e.get("team")}


def _handcuff_raw(fixture_raw_dir, players, per_week):
    """The raw of a handcuff test: every RB projects 5 a week, then `per_week` sets the players of the test."""
    raw = _raw(fixture_raw_dir, players, {})
    raw.projections_ahead = [{"week": w, "projections": _every_rb(raw, 5.0) | per_week} for w in range(7, 18)]
    raw.players[ROSTERED_RB] = {**raw.players[ROSTERED_RB], "gsis_id": f"G{ROSTERED_RB}"}
    return raw


def test_an_rb_backup_behind_a_top_half_starter_lands_in_stashes_as_a_handcuff(fixture_raw_dir):
    # The rostered starter projects the most of all RBs. The backup projects the least of the pool RBs.
    raw = _handcuff_raw(fixture_raw_dir, {"80001": _player("RB", "Good Cuff")}, {ROSTERED_RB: 20.0, "80001": 1.0})
    board = waiver_board(raw, 6, BUILT, slow=_depth({"KC": {"RB": [ROSTERED_RB, "80001"]}}), config=CONFIG)
    stashes = board.buckets["stashes"]
    assert _ids(stashes) == ["80001"]
    assert stashes[0].reason == "handcuff"


def test_an_rb_backup_behind_a_bottom_half_starter_is_not_a_handcuff(fixture_raw_dir):
    # Every other RB of the league, rostered too, projects more than the starter.
    players = {"80001": _player("RB", "Weak Starter"), "80002": _player("RB", "Weak Cuff")}
    raw = _handcuff_raw(fixture_raw_dir, players, {"80001": 2.0, "80002": 1.0})
    board = waiver_board(raw, 6, BUILT, slow=_depth({"KC": {"RB": ["80001", "80002"]}}), config=CONFIG)
    assert board.buckets["stashes"] == []


def test_a_qb_backup_behind_a_top_half_starter_is_not_a_handcuff(fixture_raw_dir):
    players = {"80001": _player("QB", "Healthy QB"), "80002": _player("QB", "Backup QB")}
    raw = _raw(fixture_raw_dir, players, {"80001": 20.0, "80002": 1.0})
    board = waiver_board(raw, 6, BUILT, slow=_depth({"KC": {"QB": ["80001", "80002"]}}), config=CONFIG)
    assert board.buckets["stashes"] == []


def test_each_entry_carries_its_reason_and_a_price_and_every_fact_digit_is_in_its_numbers(fixture_raw_dir):
    # One fixture fills every bucket: a riser, a back behind an IR starter, a stash with a return, and a handcuff.
    risers = ["80001", "80002", "80003", "80004"]
    players = {pid: _player("WR", f"Riser {name}") for pid, name in zip(risers, "ABCD")}
    players |= {"80011": _player("RB", "Hurt Starter", injury="IR"), "80012": _player("RB", "Next Up"),
                "80021": _player("TE", "Hurt Star", injury="Out", team="BUF"), "80022": _player("TE", "Low End"),
                "80031": _player("RB", "Healthy Back", team="NYJ"), "80032": _player("RB", "Backup Back", team="NYJ")}
    players |= _top_backs()
    per_week = {"80001": 2.0, "80002": 30.0, "80003": 31.0, "80004": 32.0, "80011": 14.0, "80012": 5.0,
                "80021": 12.0, "80022": 3.0, "80031": 20.0, "80032": 1.0} | dict.fromkeys(_top_backs(), 30.0)
    usage = {pid: [_usage(5, 30, 2), _usage(6, 75, 7)] for pid in risers}
    slow = _depth({"KC": {"RB": ["80011", "80012"]}, "NYJ": {"RB": ["80031", "80032"]}})
    board = waiver_board(_raw(fixture_raw_dir, players, per_week), 6, BUILT, _nfl(usage), slow=slow,
                         returns={"80021": 10}, config=CONFIG)
    reasons = {key: {p.player_id: p.reason for p in board.buckets[key]} for key in ("sneaky", "stashes")}
    assert reasons == {"sneaky": {"80001": "usage_rise", "80012": "behind_injury"},
                       "stashes": {"80021": "return", "80032": "handcuff"}}
    assert {p.reason for p in board.buckets["best_adds"]} == {"board_score"}
    entries = [p for bucket in board.buckets.values() for p in bucket]
    assert all(p.price is not None for p in entries)
    story = next(f for f in board.buckets["sneaky"][1].facts if f.id.startswith("WV.story."))
    assert story.text == "Hurt Starter is on IR, and Next Up is next on the depth chart."
    for f in (f for p in entries for f in [*p.facts, p.price.fact]):
        assert set(NUMBER_TOKEN.findall(f.text)) <= set(f.numbers), f.text


def test_an_ir_player_with_a_return_week_joins_the_pool_and_lands_in_stashes(fixture_raw_dir):
    # Sleeper gives an IR player the status Inactive. He joins the pool for stashes only.
    players = {"80001": _player("WR", "IR Star", injury="IR", status="Inactive"), "80002": _player("WR", "Low Guy")}
    board = waiver_board(_raw(fixture_raw_dir, players, {"80001": 15.0, "80002": 4.0}), 6, BUILT,
                         returns={"80001": 12}, config=CONFIG)
    assert _ids(board.buckets["stashes"]) == ["80001"]
    assert _ids(board.buckets["best_adds"]) == ["80002"]


def test_a_player_who_is_out_stays_out_of_best_adds_trending_and_sneaky(fixture_raw_dir):
    # The PUP back sits behind an injured starter and is trending, and he still lands in none of the three.
    players = {"80001": _player("RB", "Hurt Starter", injury="Out"), "80002": _player("RB", "PUP Back", injury="PUP")}
    raw = _raw(fixture_raw_dir, players, {"80001": 12.0, "80002": 30.0})
    raw.trending = [{"player_id": "80002", "count": 900}]
    board = waiver_board(raw, 6, BUILT, slow=_depth({"KC": {"RB": ["80001", "80002"]}}), config=CONFIG)
    for key in ("best_adds", "trending", "sneaky"):
        assert board.buckets[key] == [], key


def test_a_stash_needs_a_rest_of_season_projection_above_0(fixture_raw_dir):
    # Every pool player projects 0, so each ties at the top of his position, and the tie does not score.
    players = {"80001": _player("WR", "Zero Star", injury="Out"), "80002": _player("WR", "Zero Guy")}
    raw = _raw(fixture_raw_dir, players, {})
    assert waiver_board(raw, 6, BUILT, returns={"80001": 9}, config=CONFIG).buckets["stashes"] == []


def test_every_player_carries_his_bye_his_injury_status_and_his_return_week(fixture_raw_dir):
    players = {"80001": _player("WR", "Hurt Star", injury="Out"), "80002": _player("WR", "Healthy Guy", team="BUF")}
    raw = _raw(fixture_raw_dir, players, {"80001": 15.0, "80002": 4.0})
    raw.trending = [{"player_id": "80002", "count": 12}]
    schedules = {"KC": TeamSchedule(bye_week=10, playoff_opponents={})}
    board = waiver_board(raw, 6, BUILT, slow=_depth({}, schedules=schedules), returns={"80001": 9}, config=CONFIG)
    star = board.buckets["stashes"][0]
    assert (star.bye, star.injury_status, star.return_week) == (10, "Out", 9)
    healthy = board.buckets["trending"][0]
    assert (healthy.bye, healthy.injury_status, healthy.return_week, healthy.reason) == (None, None, None, "trending")
