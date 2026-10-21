"""
Tests for the loader of the three slow sources.
It reads the cache and the history, so no test needs the network.
"""
import shutil

from cornerstone.nflverse import read_id_map
from cornerstone.slow_sources import load_slow_sources


def _cache(fixture_nflverse_dir, tmp_path):
    cache = tmp_path / "nflverse"
    cache.mkdir()
    for name in ("games.csv", "depth_charts_2026.csv.gz", "db_playerids.csv"):
        shutil.copy(fixture_nflverse_dir / name, cache / name)
    return cache


def test_load_slow_sources_gives_every_source(fixture_nflverse_dir, fixture_history_root, tmp_path):
    sources = load_slow_sources(_cache(fixture_nflverse_dir, tmp_path), 2026, 6, fixture_history_root)
    assert sources.missing == []
    assert sources.schedules["SF"].bye_week == 8
    assert sources.depth_charts["SF"]["RB"][0] == "00-0033280"
    assert sources.points_allowed["NO"]["RB"].rank == 1
    assert sources.id_map == read_id_map(fixture_nflverse_dir / "db_playerids.csv")


def test_load_slow_sources_without_a_cache_names_each_missing_source(tmp_path):
    sources = load_slow_sources(tmp_path / "none", 2026, 6, tmp_path / "no-history")
    assert (sources.schedules, sources.depth_charts, sources.id_map, sources.points_allowed) == (None,) * 4
    assert sources.missing == ["schedules", "depth_charts", "id_map", "points_allowed"]


def test_load_slow_sources_without_the_ffids_file_misses_only_the_id_map(
        fixture_nflverse_dir, fixture_history_root, tmp_path):
    cache = _cache(fixture_nflverse_dir, tmp_path)
    (cache / "db_playerids.csv").unlink()
    sources = load_slow_sources(cache, 2026, 6, fixture_history_root)
    assert sources.id_map is None and sources.missing == ["id_map"]


def test_load_slow_sources_misses_a_source_independently(fixture_nflverse_dir, fixture_history_root, tmp_path):
    cache = _cache(fixture_nflverse_dir, tmp_path)
    (cache / "games.csv").unlink()
    sources = load_slow_sources(cache, 2026, 6, fixture_history_root)
    assert sources.missing == ["schedules"] and sources.depth_charts is not None


def test_load_slow_sources_with_a_broken_file_does_not_raise(fixture_nflverse_dir, fixture_history_root, tmp_path):
    cache = _cache(fixture_nflverse_dir, tmp_path)
    (cache / "games.csv").write_text("not,the,columns\n1,2,3\n")
    (cache / "depth_charts_2026.csv.gz").write_bytes(b"not gzip")
    sources = load_slow_sources(cache, 2026, 6, fixture_history_root)
    assert sources.missing == ["schedules", "depth_charts"]
