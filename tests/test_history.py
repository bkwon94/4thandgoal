"""
Tests for the fetch and cache of past weeks.
One test calls the real Sleeper API and is marked live.
"""
import shutil

import pytest

from cornerstone.history import HISTORY_FILES, fetch_history, history_dir, load_history, player_trend
from cornerstone.parse import parse_moves, parse_week
from cornerstone.sleeper import fetch_past_week, load_raw


def _fill_week_one(root):
    done = history_dir(root, 1)
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
    (history_dir(root, 1) / "stats.json").unlink()
    fetched = fetch_history("L", 2026, 1, root, fetch=lambda lid, s, w, d: None)
    assert fetched == [1]


def test_fetch_history_refetches_a_week_with_empty_stats(tmp_path):
    root = tmp_path / "history"
    _fill_week_one(root)
    (history_dir(root, 1) / "stats.json").write_text("[]")
    fetched = fetch_history("L", 2026, 1, root, fetch=lambda lid, s, w, d: None)
    assert fetched == [1]


def test_load_history_has_six_weeks(fixture_history_root, fixture_raw_dir):
    h = load_history(fixture_history_root, load_raw(fixture_raw_dir), week=6)
    assert sorted(h.weeks) == [1, 2, 3, 4, 5, 6] and h.complete()
    assert h.weeks[1].scores[6] == 153.54
    assert h.weeks[6].scores[7] == 46.08
    assert (6, 10) in h.weeks[6].pairs
    assert h.weeks[5].points["12501"] == 17.3


def test_missing_week_is_incomplete(tmp_path, fixture_history_root, fixture_raw_dir):
    shutil.copytree(fixture_history_root, tmp_path / "h")
    shutil.rmtree(tmp_path / "h" / "week-03")
    h = load_history(tmp_path / "h", load_raw(fixture_raw_dir), week=6)
    assert sorted(h.weeks) == [1, 2, 4, 5, 6] and not h.complete()


def test_parse_moves_matches_parse_week(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    assert parse_moves(raw["transactions"]) == parse_week(raw).moves


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
