"""
Tests for the reader of the nflverse weekly player file and the switch of the usage targets to it.
They read a cut of the real 2026 file: the week 6 fixture players over the season and the targeted
players of six team weeks.
"""
import csv
import gzip
import shutil
from pathlib import Path

import httpx

from cornerstone.models import UsageWeek
from cornerstone.nflverse import STATS_PLAYER_URL, nflverse_week
from cornerstone.nflverse_players import PlayerWeek, read_player_weeks, with_player_weeks
from cornerstone.sleeper import load_raw

FIXTURES = Path(__file__).parent / "fixtures" / "nflverse"
STATS_PLAYER = FIXTURES / "stats_player_week_2026.csv.gz"
GOLDEN_GSIS, GOLDEN = "00-0040667", "12501"


def _file_row(gsis: str, week: int) -> dict[str, str]:
    with gzip.open(STATS_PLAYER, "rt", encoding="utf-8", newline="") as f:
        return next(r for r in csv.DictReader(f) if r["player_id"] == gsis and r["week"] == str(week))


def test_the_reader_gives_the_file_row_of_a_player_in_percent():
    # Hand-read row: Matthew Golden, GB, week 6. 13 targets, target share 0.325, air yards share 0.5245, WOPR 0.8547.
    row = _file_row(GOLDEN_GSIS, 6)
    share, air, wopr = (float(row[c]) for c in ("target_share", "air_yards_share", "wopr"))
    assert (row["targets"], share, round(air, 4), round(wopr, 4)) == ("13", 0.325, 0.5245, 0.8547)
    assert abs(wopr - (1.5 * share + 0.7 * air)) < 1e-9
    weeks = read_player_weeks(STATS_PLAYER, 6, 6, {GOLDEN_GSIS: GOLDEN})
    assert weeks == {(GOLDEN, 6): PlayerWeek(targets=13, target_share=33, air_yards_share=52, wopr=85)}


def test_the_reader_keeps_the_window_the_skill_positions_and_the_mapped_players():
    # 00-0040718 is a JAX cornerback with 4 targets in week 6. Kyren Williams has no Sleeper ID in this map.
    weeks = read_player_weeks(STATS_PLAYER, 3, 6, {GOLDEN_GSIS: GOLDEN, "00-0040718": "999"})
    assert sorted(weeks) == [(GOLDEN, 3), (GOLDEN, 4), (GOLDEN, 5), (GOLDEN, 6)]


def test_a_file_with_no_row_for_the_week_gives_none():
    # The cut holds weeks 1 to 6, so week 8 has no row.
    assert read_player_weeks(STATS_PLAYER, 5, 8, {GOLDEN_GSIS: GOLDEN}) is None


def _usage(week: int, targets: int, share: int) -> UsageWeek:
    return UsageWeek(week=week, team="GB", snaps=None, snap_share=None, targets=targets, target_share=share,
                     carries=0, carry_share=0, red_zone_touches=1)


def test_the_file_row_replaces_our_targets_and_a_week_with_no_row_keeps_our_count():
    usage = {GOLDEN: [_usage(5, 2, 10), _usage(6, 4, 100)]}
    file_weeks = {(GOLDEN, 6): PlayerWeek(targets=13, target_share=33, air_yards_share=52, wopr=85)}
    week5, week6 = with_player_weeks(usage, file_weeks)[GOLDEN]
    assert (week5.targets, week5.target_share, week5.air_yards_share, week5.wopr) == (2, 10, None, None)
    assert (week6.targets, week6.target_share, week6.air_yards_share, week6.wopr) == (13, 33, 52, 85)
    assert week6.red_zone_touches == 1


def test_the_week_extract_takes_the_targets_from_the_file(nfl_week6):
    # Our count on the hand cut play by play gives Golden 4 of 4 Packers targets. The file gives 13 at 33%.
    golden = {u.week: u for u in nfl_week6.usage[GOLDEN]}[6]
    assert (golden.targets, golden.target_share, golden.air_yards_share, golden.wopr) == (13, 33, 52, 85)
    assert nfl_week6.sources["nflverse_stats_player"] is True


def _cache_without_the_file(tmp_path: Path) -> Path:
    for f in FIXTURES.iterdir():
        if f.name != STATS_PLAYER.name:
            shutil.copy(f, tmp_path / f.name)
    return tmp_path


def _boom(url):
    raise httpx.ConnectError("down")


def test_with_the_file_gone_the_usage_keeps_our_count_and_the_flag_is_false(tmp_path, fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    nfl = nflverse_week(2026, 6, [], raw.players, _cache_without_the_file(tmp_path), fetch=_boom)
    golden = nfl.usage[GOLDEN][0]
    assert (golden.targets, golden.target_share, golden.air_yards_share, golden.wopr) == (4, 100, None, None)
    assert nfl.sources["nflverse_stats_player"] is False
    assert nfl.sources["nflverse_pbp"] is True


def test_a_player_with_no_gsis_id_keeps_our_count_and_has_no_air_yards_share_or_wopr():
    # The map has no gsis id for Golden, so the file cannot name him and our count stays. In a real build such a
    # player has at most snap-only rows from his PFR ID, and the file leaves them as they are.
    file_weeks = read_player_weeks(STATS_PLAYER, 6, 6, {"00-0036358": "6786"})
    golden = with_player_weeks({GOLDEN: [_usage(6, 4, 100)]}, file_weeks)[GOLDEN][0]
    assert (golden.targets, golden.target_share, golden.air_yards_share, golden.wopr) == (4, 100, None, None)


def test_a_rebuild_reads_the_file_from_the_cache(tmp_path):
    seen = []

    def fetch(url):
        seen.append(url)
        if url == STATS_PLAYER_URL.format(season=2026):
            return STATS_PLAYER.read_bytes()
        raise httpx.ConnectError("down")

    for _ in range(2):
        nfl = nflverse_week(2026, 6, [], {}, tmp_path, fetch=fetch)
        assert nfl.sources["nflverse_stats_player"] is True
    assert seen.count(STATS_PLAYER_URL.format(season=2026)) == 1
