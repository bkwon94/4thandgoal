"""
Tests for the fetch and cache of past weeks.
They also test the pre-trade player profile helpers.
One test calls the real Sleeper API and is marked live.
"""
import json
import shutil

import pytest

from league.history import (
    HISTORY_FILES,
    fetch_history,
    load_history,
    load_saved_weeks,
    player_trend,
    points_per_game,
    red_zone,
    season_rank,
    share_direction,
    snap_share,
    target_share,
)
from league.models import UsageShare
from league.parse import parse_moves, parse_week
from league.paths import history_week_dir
from league.provider.sleeper import fetch_past_week, load_raw


def _fill_week_one(root):
    done = history_week_dir(root, 1)
    done.mkdir(parents=True)
    for name in HISTORY_FILES:
        (done / f"{name}.json").write_text('[{"player_id": "1"}]')


def test_fetch_history_skips_weeks_on_disk(tmp_path):
    root = tmp_path / "history"
    _fill_week_one(root)
    seen = []
    fetched = fetch_history("L", 2026, 2, root, fetch=lambda lid, s, w, d: seen.append(w))
    assert fetched == [2] and seen == [2]


def test_fetch_history_force_refetches(tmp_path):
    root = tmp_path / "history"
    _fill_week_one(root)
    seen = []
    fetched = fetch_history("L", 2026, 2, root, force=True, fetch=lambda lid, s, w, d: seen.append(w))
    assert fetched == [1, 2] and seen == [1, 2]


def test_fetch_history_refetches_a_week_with_a_missing_file(tmp_path):
    root = tmp_path / "history"
    _fill_week_one(root)
    (history_week_dir(root, 1) / "stats.json").unlink()
    fetched = fetch_history("L", 2026, 1, root, fetch=lambda lid, s, w, d: None)
    assert fetched == [1]


def test_fetch_history_refetches_a_week_with_empty_stats(tmp_path):
    root = tmp_path / "history"
    _fill_week_one(root)
    (history_week_dir(root, 1) / "stats.json").write_text("[]")
    fetched = fetch_history("L", 2026, 1, root, fetch=lambda lid, s, w, d: None)
    assert fetched == [1]


def test_load_history_has_six_weeks(fixture_history_root, fixture_raw_dir):
    h = load_history(fixture_history_root, load_raw(fixture_raw_dir), week=6)
    assert sorted(h.weeks) == [1, 2, 3, 4, 5, 6] and h.complete()
    assert h.weeks[1].scores[6] == 153.54
    assert h.weeks[6].scores[7] == 46.08
    assert (6, 10) in h.weeks[6].pairs
    assert h.weeks[5].points["12501"] == 17.3


def test_a_saved_week_keeps_the_starters_of_each_roster(fixture_history_root, fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    raw.matchups[0].starters[1] = "0"
    h = load_history(fixture_history_root, raw, week=6)
    assert h.weeks[3].starters[1] == ['8183', '13286', '9226', '2216', '8167', '11604', '3198', '7543', 'SF']
    # The empty slot "0" is not a starter.
    assert "0" not in h.weeks[6].starters[raw.matchups[0].roster_id]
    assert len(h.weeks[6].starters[raw.matchups[0].roster_id]) == 8


def test_a_saved_week_keeps_every_player_of_each_roster_with_his_points(fixture_history_root, fixture_raw_dir):
    h = load_history(fixture_history_root, load_raw(fixture_raw_dir), week=6)
    week = h.weeks[3]
    assert week.rosters[1] == [
        '11604', '12489', '13281', '13286', '2216', '2449', '3198', '5001',
        '6797', '7543', '8167', '8183', '9225', '9226', 'SF',
    ]
    bench = [pid for pid in week.rosters[1] if pid not in week.starters[1]]
    assert {pid: week.points[pid] for pid in bench} == {
        '12489': 7.7, '13281': 0.0, '2449': 5.3, '5001': 4.5, '6797': 13.74, '9225': -1.0,
    }
    assert all(pid in week.points for players in week.rosters.values() for pid in players)


def test_a_roster_with_an_empty_slot_keeps_every_player(fixture_history_root, fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    roster_id = raw.matchups[0].roster_id
    benched = raw.matchups[0].starters[1]
    raw.matchups[0].starters[1] = "0"
    h = load_history(fixture_history_root, raw, week=6)
    # The player out of the empty slot stays on the roster with his points.
    assert benched in h.weeks[6].rosters[roster_id]
    assert h.weeks[6].points[benched] == 5.9
    assert "0" not in h.weeks[6].rosters[roster_id]
    assert len(h.weeks[6].rosters[roster_id]) == 15


def test_missing_week_is_incomplete(tmp_path, fixture_history_root, fixture_raw_dir):
    shutil.copytree(fixture_history_root, tmp_path / "h")
    shutil.rmtree(tmp_path / "h" / "week-03")
    h = load_history(tmp_path / "h", load_raw(fixture_raw_dir), week=6)
    assert sorted(h.weeks) == [1, 2, 4, 5, 6] and not h.complete()


def _add(player_id, roster_id):
    return {"status": "complete", "type": "free_agent", "leg": 1, "adds": {player_id: roster_id},
            "drops": None, "settings": None, "transaction_id": f"{player_id}-{roster_id}", "created": 0,
            "roster_ids": [roster_id]}


def test_a_saved_week_reads_the_fresh_transactions_of_the_next_week(tmp_path, fixture_history_root):
    root = tmp_path / "2026" / "history"
    shutil.copytree(fixture_history_root / "week-01", history_week_dir(root, 1))
    (history_week_dir(root, 1) / "transactions.json").write_text(json.dumps([_add("SF", 1)]))
    raw = tmp_path / "2026" / "week-02" / "raw"
    raw.mkdir(parents=True)
    (raw / "transactions_prev.json").write_text(json.dumps([_add("SF", 1), _add("HOU", 6)]))
    moves = load_saved_weeks(root, 1)[1].moves
    assert [(m.player_id, m.roster_id) for m in moves] == [("SF", 1), ("HOU", 6)]


def test_a_saved_week_with_no_fresh_transactions_reads_the_saved_copy(tmp_path, fixture_history_root):
    root = tmp_path / "2026" / "history"
    shutil.copytree(fixture_history_root / "week-01", history_week_dir(root, 1))
    (history_week_dir(root, 1) / "transactions.json").write_text(json.dumps([_add("SF", 1)]))
    moves = load_saved_weeks(root, 1)[1].moves
    assert [(m.player_id, m.roster_id) for m in moves] == [("SF", 1)]


def test_parse_moves_matches_parse_week(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    assert parse_moves(raw.transactions) == parse_week(raw).moves


@pytest.mark.live
def test_fetch_past_week_writes_four_files(tmp_path):
    fetch_past_week("1386167364424318976", 2026, 5, tmp_path)
    assert {p.stem for p in tmp_path.glob("*.json")} == set(HISTORY_FILES)


def test_player_trend(fixture_history_root, fixture_raw_dir):
    h = load_history(fixture_history_root, load_raw(fixture_raw_dir), week=6)
    assert player_trend(h, "12501") == 3   # Matthew Golden
    assert player_trend(h, "9509") == 1    # Bijan Robinson


def test_player_trend_needs_points_and_projection_in_all_three_weeks(fixture_history_root, fixture_raw_dir):
    h = load_history(fixture_history_root, load_raw(fixture_raw_dir), week=6)
    assert player_trend(h, "no-such-player") is None
    del h.weeks[5].projections["12501"]
    assert player_trend(h, "12501") is None


def _h(fixture_history_root, fixture_raw_dir):
    return load_history(fixture_history_root, load_raw(fixture_raw_dir), week=6)


def test_past_week_keeps_position_and_nfl_team(fixture_history_root, fixture_raw_dir):
    h = _h(fixture_history_root, fixture_raw_dir)
    assert h.weeks[5].positions["12501"] == "WR" and h.weeks[5].nfl_teams["12501"] == "GB"


def test_golden_profile_through_week_5(fixture_history_root, fixture_raw_dir):
    # Week 5: 47 of 61 snaps, 7 targets, 3 red-zone targets, 17.3 points.
    h = _h(fixture_history_root, fixture_raw_dir)
    assert points_per_game(h, "12501", 5) == (13.3, 5)
    assert season_rank(h, "12501", 5) == (11, 90)
    assert snap_share(h, "12501", 5) == UsageShare(percent=83, weeks=2, direction="flat", weeks_used=[4, 5])
    assert target_share(h, "12501", 5) == UsageShare(percent=32, weeks=2, direction="flat", weeks_used=[4, 5])
    assert red_zone(h, "12501", 5) == (7, 0)
    assert player_trend(h, "12501", through=5) == 3


def test_points_per_game_counts_a_game_with_no_points_stat_as_zero(fixture_history_root, fixture_raw_dir):
    # Higbee played in a week with no pts_half_ppr key, because Sleeper leaves out a zero stat.
    h = _h(fixture_history_root, fixture_raw_dir)
    result = points_per_game(h, "3271", 5)
    assert isinstance(result, tuple) and result[1] > 0


def test_tuten_profile_ignores_week_6(fixture_history_root, fixture_raw_dir):
    # He scored 22.7 in week 6. Through week 5 the total is 59.2 over 5 games, 11.8 a game.
    h = _h(fixture_history_root, fixture_raw_dir)
    assert points_per_game(h, "12490", 5) == (11.8, 5)
    assert season_rank(h, "12490", 5) == (16, 77)
    assert snap_share(h, "12490", 5) == UsageShare(percent=64, weeks=2, direction="up", weeks_used=[4, 5])
    assert target_share(h, "12490", 5) == UsageShare(percent=11, weeks=2, direction="flat", weeks_used=[4, 5])
    assert red_zone(h, "12490", 5) == (1, 12)
    assert player_trend(h, "12490", through=5) == 1


def test_fewer_than_4_weeks_has_no_direction(fixture_history_root, fixture_raw_dir):
    h = _h(fixture_history_root, fixture_raw_dir)
    assert points_per_game(h, "7569", 5) == (17.7, 3)
    assert snap_share(h, "7569", 5) == UsageShare(percent=71, weeks=3, direction=None, weeks_used=[1, 4, 5])


def test_no_scored_game(fixture_history_root, fixture_raw_dir):
    h = _h(fixture_history_root, fixture_raw_dir)
    assert points_per_game(h, "5850", 5) == (0.0, 0)
    assert snap_share(h, "5850", 5) is None and red_zone(h, "5850", 5) is None


def test_ppg_rounds_half_up(fixture_history_root, fixture_raw_dir):
    # Patrick Mahomes: 85.58 over 4 games is 21.395.
    assert points_per_game(_h(fixture_history_root, fixture_raw_dir), "4046", 5) == (21.4, 4)


def test_stats_outage_removes_the_profile(fixture_history_root, fixture_raw_dir):
    h = _h(fixture_history_root, fixture_raw_dir)
    h.weeks[2].stats = {}
    assert points_per_game(h, "12490", 5) is None
    assert season_rank(h, "12490", 5) is None
    assert snap_share(h, "12490", 5) is None and target_share(h, "12490", 5) is None


def test_share_direction():
    assert share_direction(55, 50) == "up"
    assert share_direction(50, 55) == "down"
    assert share_direction(54.9, 50) == "flat"
