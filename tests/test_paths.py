"""Checks that each function of paths builds the directory or label the repo layout uses on disk.
The expected strings are literal, so a change to the layout fails here first.
"""
from pathlib import Path

from cornerstone.paths import (
    chart_image, chart_read, charts_dir, history_dir, history_raw_dir, history_root, history_week_dir,
    nflverse_cache_dir, players_cache, raw_dir, results_cache_dir, returns_path, season_dir, site_week_dir, week_dir,
    week_from_label, week_label,
)

REPO = Path("/repo")
SITE = Path("/repo/site")


def test_week_label_pads_to_two_digits():
    assert week_label(7) == "week-07"
    assert week_label(12) == "week-12"


def test_week_from_label_reads_a_label_and_a_stem():
    assert week_from_label("week-07") == 7
    assert week_from_label(Path("week-12.png").stem) == 12


def test_week_dir_is_under_the_season_data():
    assert week_dir(REPO, 2026, 6) == Path("/repo/data/2026/week-06")


def test_raw_dir_is_inside_the_week_dir():
    assert raw_dir(REPO, 2026, 6) == Path("/repo/data/2026/week-06/raw")


def test_history_root_is_under_the_season_data():
    assert history_root(REPO, 2026) == Path("/repo/data/2026/history")


def test_history_dir_is_a_week_under_the_history_root():
    assert history_dir(REPO, 2026, 6) == Path("/repo/data/2026/history/week-06")


def test_returns_path_is_beside_the_history():
    assert returns_path(REPO, 2026) == Path("/repo/data/2026/returns.json")


def test_site_week_dir_is_a_week_under_the_season_dir():
    assert site_week_dir(SITE, 2026, 6) == Path("/repo/site/2026/week-06")


def test_season_dir_is_under_the_site():
    assert season_dir(SITE, 2026) == Path("/repo/site/2026")


def test_players_cache_is_one_file_in_the_cache():
    assert players_cache(REPO) == Path("/repo/data/cache/players.json")


def test_nflverse_cache_dir_is_in_the_cache():
    assert nflverse_cache_dir(REPO) == Path("/repo/data/cache/nflverse")


def test_charts_dir_is_in_the_cache():
    assert charts_dir(REPO) == Path("/repo/data/cache/charts")


def test_chart_image_is_a_png_named_for_the_week():
    assert chart_image(REPO, 6) == Path("/repo/data/cache/charts/week-06.png")


def test_chart_read_is_a_json_named_for_the_week():
    assert chart_read(REPO, 6) == Path("/repo/data/cache/charts/week-06.json")


def test_results_cache_dir_is_in_the_cache():
    assert results_cache_dir(REPO) == Path("/repo/data/cache/results")


def test_history_week_dir_is_a_week_under_a_given_root():
    assert history_week_dir(Path("/h"), 6) == Path("/h/week-06")


def test_history_raw_dir_sits_beside_the_history_root():
    assert history_raw_dir(Path("/repo/data/2026/history"), 7) == Path("/repo/data/2026/week-07/raw")
