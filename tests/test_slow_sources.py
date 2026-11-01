"""
Tests for the loader of the slow sources.
It reads the cache and the history, so no test needs the network.
"""
import shutil

from cornerstone.nflverse import read_id_map
from cornerstone.sleeper import load_raw
from cornerstone.slow_sources import load_slow_sources


def _cache(fixture_nflverse_dir, tmp_path):
    cache = tmp_path / "nflverse"
    cache.mkdir()
    for name in ("games.csv", "depth_charts_2026.csv.gz", "db_playerids.csv", "injuries_2026.csv.gz"):
        shutil.copy(fixture_nflverse_dir / name, cache / name)
    return cache


# The two sources that `_cache` leaves out. Each test that needs one copies it in.
NOT_IN_CACHE = ["expected_points", "player_weeks"]


def test_load_slow_sources_gives_every_source_in_the_cache(fixture_nflverse_dir, fixture_history_root, tmp_path):
    sources = load_slow_sources(_cache(fixture_nflverse_dir, tmp_path), 2026, 6, fixture_history_root)
    assert sources.missing == NOT_IN_CACHE
    assert sources.schedules["SF"].bye_week == 8
    assert sources.depth_charts["SF"]["RB"][0] == "00-0033280"
    assert sources.points_allowed["NO"]["RB"].rank == 1
    assert sources.id_map == read_id_map(fixture_nflverse_dir / "db_playerids.csv")
    # Terry McLaurin is Questionable in weeks 4 and 5 and has no status in week 6.
    assert sources.injuries["00-0035659"] == {4: "Questionable", 5: "Questionable"}


def test_load_slow_sources_without_a_cache_names_each_missing_source(tmp_path):
    sources = load_slow_sources(tmp_path / "none", 2026, 6, tmp_path / "no-history")
    assert (sources.schedules, sources.depth_charts, sources.id_map, sources.points_allowed, sources.injuries) == (
        None,) * 5
    assert sources.missing == ["schedules", "depth_charts", "id_map", "points_allowed", "injuries", *NOT_IN_CACHE]


def test_load_slow_sources_without_the_ffids_file_misses_only_the_id_map(
        fixture_nflverse_dir, fixture_history_root, tmp_path):
    cache = _cache(fixture_nflverse_dir, tmp_path)
    (cache / "db_playerids.csv").unlink()
    sources = load_slow_sources(cache, 2026, 6, fixture_history_root)
    assert sources.id_map is None and sources.missing == ["id_map", *NOT_IN_CACHE]


def test_load_slow_sources_misses_a_source_independently(fixture_nflverse_dir, fixture_history_root, tmp_path):
    cache = _cache(fixture_nflverse_dir, tmp_path)
    (cache / "games.csv").unlink()
    sources = load_slow_sources(cache, 2026, 6, fixture_history_root)
    assert sources.missing == ["schedules", *NOT_IN_CACHE] and sources.depth_charts is not None


def test_load_slow_sources_with_a_broken_file_does_not_raise(fixture_nflverse_dir, fixture_history_root, tmp_path):
    cache = _cache(fixture_nflverse_dir, tmp_path)
    (cache / "games.csv").write_text("not,the,columns\n1,2,3\n")
    (cache / "depth_charts_2026.csv.gz").write_bytes(b"not gzip")
    sources = load_slow_sources(cache, 2026, 6, fixture_history_root)
    assert sources.missing == ["schedules", "depth_charts", *NOT_IN_CACHE]


def test_load_slow_sources_without_the_injuries_file_misses_only_the_injuries(
        fixture_nflverse_dir, fixture_history_root, tmp_path):
    cache = _cache(fixture_nflverse_dir, tmp_path)
    (cache / "injuries_2026.csv.gz").unlink()
    sources = load_slow_sources(cache, 2026, 6, fixture_history_root)
    assert sources.injuries is None and sources.missing == ["injuries", *NOT_IN_CACHE]


def test_load_slow_sources_with_the_league_scoring_gives_the_expected_points(
        fixture_nflverse_dir, fixture_history_root, fixture_raw_dir, tmp_path):
    cache = _cache(fixture_nflverse_dir, tmp_path)
    shutil.copy(fixture_nflverse_dir / "ep_weekly_2026.csv", cache / "ep_weekly_2026.csv")
    scoring = load_raw(fixture_raw_dir).league.scoring_settings
    sources = load_slow_sources(cache, 2026, 6, fixture_history_root, scoring)
    # The trade week is 6, so the expected window ends at week 5, as every other grade input does.
    assert sources.expected.through_week == 5
    assert sources.expected.players and all(game.week <= 5 for games in sources.expected.players.values()
                                            for game in games)
    assert sources.missing == ["player_weeks"]


def test_load_slow_sources_without_the_expected_points_file_gives_none_and_names_it_as_missing(
        fixture_nflverse_dir, fixture_history_root, fixture_raw_dir, tmp_path):
    scoring = load_raw(fixture_raw_dir).league.scoring_settings
    sources = load_slow_sources(_cache(fixture_nflverse_dir, tmp_path), 2026, 6, fixture_history_root, scoring)
    assert sources.expected is None and sources.missing == NOT_IN_CACHE


def test_load_slow_sources_gives_the_wopr_of_the_weekly_player_file_through_the_trade_week_when_it_has_it(
        fixture_nflverse_dir, fixture_history_root, tmp_path):
    cache = _cache(fixture_nflverse_dir, tmp_path)
    shutil.copy(fixture_nflverse_dir / "stats_player_week_2026.csv.gz", cache / "stats_player_week_2026.csv.gz")
    sources = load_slow_sources(cache, 2026, 6, fixture_history_root)
    # Matthew Golden's WOPR by week. The trade week is 6 and the file has week 6, so the known games read it.
    assert sources.wopr["12501"] == {1: 65, 2: 57, 3: 71, 4: 64, 5: 58, 6: 85}
    assert sources.missing == ["expected_points"]


def test_load_slow_sources_gives_the_wopr_through_the_week_before_when_the_file_lacks_the_trade_week(
        fixture_nflverse_dir, fixture_history_root, tmp_path):
    cache = _cache(fixture_nflverse_dir, tmp_path)
    shutil.copy(fixture_nflverse_dir / "stats_player_week_2026.csv.gz", cache / "stats_player_week_2026.csv.gz")
    # The file ends at week 6. A trade week of 7 reads weeks 1 to 6.
    assert load_slow_sources(cache, 2026, 7, fixture_history_root).wopr["12501"] == {
        1: 65, 2: 57, 3: 71, 4: 64, 5: 58, 6: 85}
    # A trade week of 8 needs week 7, so the file counts as missing.
    late = load_slow_sources(cache, 2026, 8, fixture_history_root)
    assert late.wopr is None and "player_weeks" in late.missing


def test_load_slow_sources_without_the_weekly_player_file_or_the_id_map_gives_no_wopr_and_names_it_as_missing(
        fixture_nflverse_dir, fixture_history_root, tmp_path):
    cache = _cache(fixture_nflverse_dir, tmp_path)
    sources = load_slow_sources(cache, 2026, 6, fixture_history_root)
    assert sources.wopr is None and sources.missing == NOT_IN_CACHE
    shutil.copy(fixture_nflverse_dir / "stats_player_week_2026.csv.gz", cache / "stats_player_week_2026.csv.gz")
    (cache / "db_playerids.csv").unlink()
    without_id_map = load_slow_sources(cache, 2026, 6, fixture_history_root)
    assert without_id_map.wopr is None and without_id_map.missing == ["id_map", *NOT_IN_CACHE]
