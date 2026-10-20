"""
Tests for the fetch and cache of past weeks.
One test calls the real Sleeper API and is marked live.
"""
import pytest

from cornerstone.history import HISTORY_FILES, fetch_history, history_dir
from cornerstone.sleeper import fetch_past_week


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


@pytest.mark.live
def test_fetch_past_week_writes_four_files(tmp_path):
    fetch_past_week("1386167364424318976", 2026, 5, tmp_path)
    assert {p.stem for p in tmp_path.glob("*.json")} == set(HISTORY_FILES)
