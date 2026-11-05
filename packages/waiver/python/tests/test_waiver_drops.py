"""
Tests for the drops bucket of the waiver board.
They feed the week 6 raw with hand-set usage and projections at the engine seam and the drops seam.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from cpc import cpc_client

from league.models import BoardScores, NflverseWeek, UsageWeek, WaiverPlayer
from league.provider.sleeper import load_raw
from league.tunables import DROP_WEEKS, USAGE_SAVED_WEEKS
from waiver.board import _rostered, waiver_board
from waiver.drops import drop_candidates

CLIENT = cpc_client()

BUILT = datetime(2026, 10, 20, 21, 0, tzinfo=ZoneInfo("America/New_York"))
# Rostered players of the week 6 fixture. Lil Fridge is roster 3, and all three are on it.
DOBBINS, HENRY, MEYERS = "6806", "3198", "5947"


def _player(position, team="KC", name="Free Agent"):
    return {"position": position, "team": team, "status": "Active", "active": True, "full_name": name}


def _raw(fixture_raw_dir, players, per_week):
    """The week 6 raw with `players` added and a flat projection per week, weeks 7 to 17, for each ID in `per_week`."""
    raw = load_raw(fixture_raw_dir)
    raw.players = {**raw.players, **players}
    raw.projections_ahead = [{"week": w, "projections": dict(per_week)} for w in range(7, 18)]
    return raw


def _usage(week, share):
    return UsageWeek(week=week, team="DEN", snaps=share, snap_share=share, targets=0, target_share=0, carries=0,
                     carry_share=0, red_zone_touches=0)


def _shares(*shares):
    """The usage weeks that end at week 6, one per snap share, oldest first."""
    first = 7 - len(shares)
    return [_usage(first + i, s) for i, s in enumerate(shares)]


def _nfl(usage):
    return NflverseWeek(sources={}, gsis={}, drops=None, injuries=None, usage=usage, environment={})


def _drops(raw, usage):
    return waiver_board(raw, 6, BUILT, _nfl(usage), client=CLIENT).buckets["drops"]


def test_a_rostered_player_with_three_falls_and_a_better_pool_player_lands_in_drops_with_his_roster(fixture_raw_dir):
    raw = _raw(fixture_raw_dir, {"80001": _player("RB", name="Audric Estime")}, {"80001": 9.0, DOBBINS: 6.9})
    drops = _drops(raw, {DOBBINS: _shares(70, 61, 52, 40)})
    assert [d.player_id for d in drops] == [DOBBINS]
    candidate = drops[0]
    assert candidate.drop.model_dump() == {"roster_id": 3, "holder": "Lil Fridge", "reason": "three_falls",
                                           "beaten_by": "80001", "beaten_by_name": "Audric Estime", "margin": 2.1}
    assert candidate.price is None
    assert [f.text for f in candidate.facts] == [
        "Lil Fridge holds J.K. Dobbins, and Audric Estime projects 2.1 points a week higher."]
    assert candidate.facts[0].numbers == ["2.1"]


def test_a_whole_margin_prints_with_no_decimal(fixture_raw_dir):
    # 99 minus 66 over 11 weeks is a margin of 3.0, and the page form writes it as 3.
    raw = _raw(fixture_raw_dir, {"80001": _player("RB", name="Audric Estime")}, {"80001": 9.0, DOBBINS: 6.0})
    candidate = _drops(raw, {DOBBINS: _shares(70, 61, 52, 40)})[0]
    assert candidate.facts[0].text == (
        "Lil Fridge holds J.K. Dobbins, and Audric Estime projects 3 points a week higher.")
    assert candidate.facts[0].numbers == ["3"]


def test_a_bye_inside_the_window_gives_no_drop_candidate(fixture_raw_dir):
    raw = _raw(fixture_raw_dir, {"80001": _player("RB")}, {"80001": 9.0, DOBBINS: 6.9})
    # Weeks 3, 4, and 6 fall, and week 5 is the bye, so the run of falls has a hole.
    drops = _drops(raw, {DOBBINS: [_usage(3, 70), _usage(4, 61), _usage(6, 40)]})
    assert drops == []


def test_two_drop_candidates_at_one_position_on_one_roster_both_show(fixture_raw_dir):
    raw = _raw(fixture_raw_dir, {"80001": _player("RB")}, {"80001": 9.0, DOBBINS: 6.9, HENRY: 5.0})
    drops = _drops(raw, {DOBBINS: _shares(70, 61, 52, 40), HENRY: _shares(70, 61, 52, 40)})
    assert [(d.player_id, d.drop.roster_id) for d in drops] == [(HENRY, 3), (DOBBINS, 3)]


def test_the_usage_extract_saves_the_weeks_of_the_drops_window():
    # DROP_WEEKS falls in a row take one more week than the falls.
    assert USAGE_SAVED_WEEKS == DROP_WEEKS + 1


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


def _rostered_at(raw, position, count):
    """The first `count` rostered players at `position` by player ID."""
    return [pid for pid in sorted(_rostered(raw)) if raw.players[pid].get("position") == position][:count]


def test_the_drops_bucket_sorts_by_the_margin_and_holds_at_most_8(fixture_raw_dir):
    # Three rostered players at each of four positions fall three weeks in a row. Each pool player projects 20
    # a week. Rostered player i of the position at offset o projects o + i, so his margin is 20 - o - i.
    fixture = load_raw(fixture_raw_dir)
    offsets = {"QB": 0.0, "RB": 4.0, "WR": 8.0, "TE": 12.0}
    pool = {f"8000{i}": _player(position) for i, position in enumerate(offsets, 1)}
    per_week = dict.fromkeys(pool, 20.0)
    falling = []
    for position, offset in offsets.items():
        for i, pid in enumerate(_rostered_at(fixture, position, 3)):
            per_week[pid] = offset + i
            falling.append(pid)
    assert len(falling) == 12
    drops = _drops(_raw(fixture_raw_dir, pool, per_week), {pid: _shares(70, 61, 52, 40) for pid in falling})
    # The margins are QB 20 to 18, RB 16 to 14, WR 12 to 10, and TE 8 to 6. The eight largest stay.
    assert [d.drop.margin for d in drops] == [20.0, 19.0, 18.0, 16.0, 15.0, 14.0, 12.0, 11.0]


def test_five_rb_drop_candidates_all_show_when_they_rank_in_the_top_8(fixture_raw_dir):
    # Five rostered RBs have the five largest margins, and three WRs follow. No cap per position applies.
    fixture = load_raw(fixture_raw_dir)
    rbs, wrs = _rostered_at(fixture, "RB", 5), _rostered_at(fixture, "WR", 3)
    per_week = {"80001": 20.0, "80002": 20.0} | {pid: 1.0 + i for i, pid in enumerate(rbs)}
    per_week |= {pid: 10.0 + i for i, pid in enumerate(wrs)}
    raw = _raw(fixture_raw_dir, {"80001": _player("RB"), "80002": _player("WR")}, per_week)
    drops = _drops(raw, {pid: _shares(70, 61, 52, 40) for pid in rbs + wrs})
    assert [d.position for d in drops] == ["RB"] * 5 + ["WR"] * 3


def test_a_drop_candidate_keeps_its_roster_through_the_saved_board(fixture_raw_dir):
    raw = _raw(fixture_raw_dir, {"80001": _player("RB")}, {"80001": 9.0, DOBBINS: 6.9})
    board = waiver_board(raw, 6, BUILT, _nfl({DOBBINS: _shares(70, 61, 52, 40)}), client=CLIENT)
    saved = type(board).model_validate_json(board.model_dump_json())
    assert saved == board
    assert saved.buckets["drops"][0].drop.holder == "Lil Fridge"


def _pool_player(pid, position, ros, name):
    return WaiverPlayer(player_id=pid, name=name, position=position, team="KC", week_projection=0.0,
                        ros_projection=ros, scores=BoardScores(), board_score=0.0)


def test_the_pool_player_who_beats_a_drop_candidate_is_the_best_at_his_position(fixture_raw_dir):
    # A WR projects the most of the pool, but Dobbins is an RB, so the best RB beats him.
    raw = _raw(fixture_raw_dir, {}, {DOBBINS: 5.0})
    pool = [_pool_player("80001", "WR", 300.0, "Top Wideout"), _pool_player("80002", "RB", 77.0, "Second Back"),
            _pool_player("80003", "RB", 88.0, "Top Back")]
    drops = drop_candidates(raw, 6, {DOBBINS: _shares(70, 61, 52, 40)}, pool, client=CLIENT)
    # 88 minus 55 over 11 weeks is 3 a week.
    assert [(d.player_id, d.drop.beaten_by_name, d.drop.margin) for d in drops] == [(DOBBINS, "Top Back", 3.0)]
