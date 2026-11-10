"""
Tests for the past-season splits of the Advisor sheet and for the cache of the past season files.
They read a real slice of the nflverse files of 2023 to 2025: the rows of Derrick Henry and Nico Collins.
"""
import csv
import gzip
import os
import shutil
import time
from pathlib import Path

import pytest
from cpc import cpc_client, four_week
from fakes import FakeJev, no_news

from analyzer.advisor import advisor_sheet
from analyzer.trade import ProposedTrade, TradeSide
from analyzer.trade_news import NewsFeed
from analyzer.trade_splits import Split, season_splits, trade_split_facts
from league.past_seasons import fetch_past_seasons
from league.paths import nflverse_cache_dir
from league.slow_sources import load_slow_sources
from league.snapshot import load_snapshot

PAST = Path(__file__).parent / "fixtures" / "nflverse_past"
HENRY_GSIS, COLLINS_GSIS = "00-0032764", "00-0036554"
COLLINS, KINCAID, WILSON = "7569", "10236", "8146"


@pytest.fixture
def cache(tmp_path):
    folder = tmp_path / "nflverse"
    shutil.copytree(PAST, folder)
    return folder


def test_a_veteran_has_a_split_for_each_of_the_last_three_seasons(cache):
    splits = season_splits(cache, 2026, HENRY_GSIS)
    assert [s.season for s in splits] == [2023, 2024, 2025]
    assert splits[2].early == Split(points_per_game=12.84, games=7)
    assert splits[2].late == Split(points_per_game=18.83, games=9)
    assert splits[2].cold == Split(points_per_game=21.58, games=5)
    # One cold game in 2023, and its week 1 to 8 count skips the bye week.
    assert splits[0].cold == Split(points_per_game=17.7, games=1)
    assert splits[0].early.games == 7
    # He moved from TEN to BAL after 2023.
    assert [s.team for s in splits] == ["TEN", "BAL", "BAL"]


def _big_past_file(cache: Path, season: int, copies: int) -> None:
    """The past season file of `season` with its rows, plus `copies` copies of them under other gsis ids.

    A real past season file holds about 19,000 rows, so a file of this size shows the time of a full read.
    """
    path = cache / f"stats_player_week_{season}.csv.gz"
    with gzip.open(path, "rt", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields, rows = reader.fieldnames, list(reader)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        for copy in range(copies):
            writer.writerows({**row, "player_id": f"{row['player_id']}-{copy}"} for row in rows)


@pytest.mark.serial
def test_the_splits_of_many_players_read_each_past_season_file_once(cache):
    # The Finder pick builds a sheet for each shortlist offer, so a full read of each past season file per player
    # costs seconds. The splits of 20 players must take well under a second after the first read.
    for season in (2023, 2024, 2025):
        _big_past_file(cache, season, copies=200)
    first = season_splits(cache, 2026, HENRY_GSIS)
    started = time.monotonic()
    for _ in range(20):
        assert season_splits(cache, 2026, HENRY_GSIS) == first
    assert time.monotonic() - started < 0.5


def test_a_past_season_file_that_changes_on_disk_is_read_again(cache):
    before = season_splits(cache, 2026, HENRY_GSIS)
    path = cache / "stats_player_week_2023.csv.gz"
    with gzip.open(path, "rt", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = [row for row in reader if row["player_id"] != HENRY_GSIS]
    with gzip.open(path, "wt", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    os.utime(path, ns=(time.time_ns(), time.time_ns() + 10**9))
    assert [s.season for s in season_splits(cache, 2026, HENRY_GSIS)] == [2024, 2025] != [s.season for s in before]


@pytest.fixture
def snap(fixture_raw_dir, fixture_history_root, chart_week6, tmp_path):
    """The week 6 snapshot, with the cache of the client holding the past season slice. Collins has his gsis id."""
    client = cpc_client(at=tmp_path)
    folder = nflverse_cache_dir(client.nfl_dir)
    shutil.copytree(PAST, folder)
    slow = load_slow_sources(folder, 2026, 6, fixture_history_root)
    snapshot = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow, client=client)
    return four_week(snapshot).model_copy(update={"id_map": {COLLINS: COLLINS_GSIS}})


@pytest.fixture
def trade():
    return ProposedTrade(season=2026, asker=4, sides=(
        TradeSide(roster_id=4, gives=[{"player_id": COLLINS, "to": 12}]),
        TradeSide(roster_id=12, gives=[{"player_id": KINCAID, "to": 4}, {"player_id": WILSON, "to": 4}])))


def test_the_sheet_holds_one_history_fact_with_each_season_and_its_game_count(snap, trade):
    facts = trade_split_facts(trade, snap)
    fact = facts[f"{COLLINS}.history"]
    assert "Nico Collins" in fact.players
    for season in ("2023", "2024", "2025"):
        assert season in fact.numbers
    assert "weeks 1 to 8" in fact.text
    assert "cold" in fact.text
    assert "played for HOU" in fact.text
    assert "no cold game" in fact.text, "Collins played no cold game in 2023"


def test_a_player_with_no_past_season_has_no_history_fact(snap, trade):
    # Garrett Wilson has no row in the slice, as a rookie has none in a real file. Dalton Kincaid has no gsis id.
    facts = trade_split_facts(trade, snap)
    assert f"{WILSON}.history" not in facts
    assert f"{KINCAID}.history" not in facts


def test_the_sheet_of_the_advisor_carries_the_history_fact(snap, trade):
    sheet = advisor_sheet(trade, snap, FakeJev(), NewsFeed(fetch=no_news))
    assert f"{COLLINS}.history" in sheet


def _serve_from_slice(asked):
    """A download that answers from the real slice and keeps each URL it was asked for."""
    def fetch(url):
        asked.append(url)
        return (PAST / url.rsplit("/", 1)[-1]).read_bytes()
    return fetch


def test_a_second_press_downloads_no_past_season_file(tmp_path):
    cache = tmp_path / "nflverse"
    asked = []
    assert fetch_past_seasons(cache, 2026, _serve_from_slice(asked)) == [2023, 2024, 2025]
    assert [url.rsplit("/", 1)[-1] for url in asked] == [
        "stats_player_week_2023.csv.gz", "stats_player_week_2024.csv.gz", "stats_player_week_2025.csv.gz"]
    # A file a year old is still final, so it never downloads again.
    for path in cache.iterdir():
        os.utime(path, (time.time() - 400 * 24 * 3600,) * 2)
    asked.clear()
    assert fetch_past_seasons(cache, 2026, _serve_from_slice(asked)) == []
    assert asked == []
