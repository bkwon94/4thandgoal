"""
Tests for the drops bucket of the waiver board.
They feed the week 6 raw with hand-set usage and projections at the engine seam and the drops seam.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from cornerstone.models import BoardScores, NflverseWeek, UsageWeek, WaiverPlayer
from cornerstone.sleeper import load_raw
from cornerstone.waiver import waiver_board
from cornerstone.waiver_drops import drop_candidates

BUILT = datetime(2026, 10, 20, 21, 0, tzinfo=ZoneInfo("America/New_York"))
# Rostered players of the week 6 fixture. Lil Fridge is roster 3.
DOBBINS, HENRY, MEYERS = "6806", "3198", "5947"


def _player(position, team="KC", name="Free Agent"):
    return {"position": position, "team": team, "status": "Active", "active": True, "full_name": name}


def _raw(fixture_raw_dir, players, per_week):
    """The week 6 raw with `players` added and a flat projection per week, weeks 7 to 17, for each ID in `per_week`."""
    raw = load_raw(fixture_raw_dir)
    raw["players"] = {**raw["players"], **players}
    raw["projections_ahead"] = [{"week": w, "projections": dict(per_week)} for w in range(7, 18)]
    return raw


def _shares(*shares):
    """The usage weeks that end at week 6, one per snap share, oldest first."""
    first = 7 - len(shares)
    return [UsageWeek(week=first + i, team="DEN", snaps=s, snap_share=s, targets=0, target_share=0, carries=0,
                      carry_share=0, red_zone_touches=0) for i, s in enumerate(shares)]


def _nfl(usage):
    return NflverseWeek(sources={}, gsis={}, drops=None, injuries=None, usage=usage, environment={})


def _drops(raw, usage):
    return waiver_board(raw, 6, BUILT, _nfl(usage)).buckets["drops"]


def test_a_rostered_player_with_three_falls_and_a_better_pool_player_lands_in_drops_with_his_roster(fixture_raw_dir):
    raw = _raw(fixture_raw_dir, {"80001": _player("RB", name="Audric Estime")}, {"80001": 9.0, DOBBINS: 6.9})
    drops = _drops(raw, {DOBBINS: _shares(70, 61, 52, 40)})
    assert [d.player_id for d in drops] == [DOBBINS]
    drop = drops[0]
    assert (drop.roster_id, drop.holder) == (3, "Lil Fridge")
    assert (drop.beaten_by, drop.beaten_by_name, drop.gap) == ("80001", "Audric Estime", 2.1)
    assert drop.reason == "three_falls"
    assert drop.price is None
    assert [f.text for f in drop.facts] == [
        "Lil Fridge holds J.K. Dobbins, and Audric Estime projects 2.1 points a week higher."]
    assert drop.facts[0].numbers == ["2.1"]


def test_a_rostered_player_with_two_falls_stays_out_of_drops(fixture_raw_dir):
    raw = _raw(fixture_raw_dir, {"80001": _player("RB")}, {"80001": 9.0, DOBBINS: 6.9, HENRY: 6.9})
    # Dobbins rose in week 4 before two falls. Henry has only three weeks of usage, so two falls.
    drops = _drops(raw, {DOBBINS: _shares(50, 61, 52, 40), HENRY: _shares(61, 52, 40)})
    assert drops == []


def test_a_rostered_player_with_three_falls_and_no_better_pool_player_stays_out_of_drops(fixture_raw_dir):
    # The best pool RB projects the same as Dobbins, and the pool has no WR, so Meyers has no one to beat him.
    raw = _raw(fixture_raw_dir, {"80001": _player("RB")}, {"80001": 6.9, DOBBINS: 6.9, MEYERS: 1.0})
    drops = _drops(raw, {DOBBINS: _shares(70, 61, 52, 40), MEYERS: _shares(70, 61, 52, 40)})
    assert drops == []


def _rostered(raw, position, count):
    """The first `count` rostered players at `position` by player ID."""
    rostered = {pid for r in raw["rosters"] for pid in r["players"] or []}
    return [pid for pid in sorted(rostered) if raw["players"][pid].get("position") == position][:count]


def test_the_drops_bucket_sorts_by_the_gap_and_holds_at_most_8(fixture_raw_dir):
    # Three rostered players at each of four positions fall three weeks in a row. Each pool player projects 20
    # a week. Rostered player i of the position at offset o projects o + i, so his gap is 20 - o - i.
    fixture = load_raw(fixture_raw_dir)
    offsets = {"QB": 0.0, "RB": 4.0, "WR": 8.0, "TE": 12.0}
    pool = {f"8000{i}": _player(position) for i, position in enumerate(offsets, 1)}
    per_week = dict.fromkeys(pool, 20.0)
    falling = []
    for position, offset in offsets.items():
        for i, pid in enumerate(_rostered(fixture, position, 3)):
            per_week[pid] = offset + i
            falling.append(pid)
    assert len(falling) == 12
    drops = _drops(_raw(fixture_raw_dir, pool, per_week), {pid: _shares(70, 61, 52, 40) for pid in falling})
    # The gaps are QB 20 to 18, RB 16 to 14, WR 12 to 10, and TE 8 to 6. The eight largest stay.
    assert [d.gap for d in drops] == [20.0, 19.0, 18.0, 16.0, 15.0, 14.0, 12.0, 11.0]


def test_a_drop_keeps_its_roster_through_the_saved_board(fixture_raw_dir):
    raw = _raw(fixture_raw_dir, {"80001": _player("RB")}, {"80001": 9.0, DOBBINS: 6.9})
    board = waiver_board(raw, 6, BUILT, _nfl({DOBBINS: _shares(70, 61, 52, 40)}))
    saved = type(board).model_validate_json(board.model_dump_json())
    assert saved == board
    assert saved.buckets["drops"][0].holder == "Lil Fridge"


def _pool_player(pid, position, ros, name):
    return WaiverPlayer(player_id=pid, name=name, position=position, team="KC", week_projection=0.0,
                        ros_projection=ros, scores=BoardScores(), board_score=0.0)


def test_the_pool_player_who_beats_a_drop_is_the_best_at_his_position(fixture_raw_dir):
    # A WR projects the most of the pool, but Dobbins is an RB, so the best RB beats him.
    raw = _raw(fixture_raw_dir, {}, {DOBBINS: 5.0})
    pool = [_pool_player("80001", "WR", 300.0, "Top Wideout"), _pool_player("80002", "RB", 77.0, "Second Back"),
            _pool_player("80003", "RB", 88.0, "Top Back")]
    drops = drop_candidates(raw, 6, {DOBBINS: _shares(70, 61, 52, 40)}, pool)
    # 88 minus 55 over 11 weeks is 3 a week.
    assert [(d.player_id, d.beaten_by_name, d.gap) for d in drops] == [(DOBBINS, "Top Back", 3.0)]
