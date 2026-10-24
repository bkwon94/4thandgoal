"""
Tests for the expected points reader of the ffopportunity weekly file.
They read a small fixture cut from the real file for the week 6 fixture players, and the real schedules fixture.
"""
import json

import httpx
import pytest

from cornerstone.models import ExpectedGame
from cornerstone.nflverse import nflverse_week
from cornerstone.nflverse_expected import read_expected, window_gap

# The gsis ids of the fixture players that the tests read, with their Sleeper ids.
SLEEPER_OF_GSIS = {"00-0033077": "3294", "00-0033280": "4034", "00-0033873": "4046", "00-0035676": "5859"}


@pytest.fixture
def scoring(fixture_raw_dir):
    return json.loads((fixture_raw_dir / "league.json").read_text())["scoring_settings"]


@pytest.fixture
def ep(fixture_nflverse_dir):
    return fixture_nflverse_dir / "ep_weekly_2026.csv"


@pytest.fixture
def games(fixture_nflverse_dir):
    return fixture_nflverse_dir / "games.csv"


def test_the_rescale_matches_the_league_scoring_on_a_hand_computed_row(ep, games, scoring):
    # Dak Prescott, week 6: total_fantasy_points_exp 25.19, receptions_exp 0, pass_interception_exp 1.16.
    # The league pays -1 per interception where the file pays -2: 25.19 + 1 * 1.16 = 26.35.
    expected = read_expected(ep, games, 2026, 6, scoring, SLEEPER_OF_GSIS)
    assert expected.players["3294"][-1] == ExpectedGame(week=6, game_id="2026_06_DAL_GB", expected=26.35)


def test_the_rescale_takes_the_reception_weight_from_the_league(ep, games, scoring):
    # Christian McCaffrey, week 6: 34.12 - 0.5 * 8.1 receptions_exp = 30.07.
    half = read_expected(ep, games, 2026, 6, scoring, SLEEPER_OF_GSIS).players["4034"][-1]
    assert half.expected == 30.07
    full = read_expected(ep, games, 2026, 6, {**scoring, "rec": 1.0, "pass_int": -2.0},
                         SLEEPER_OF_GSIS).players["4034"][-1]
    # With the file's own weights, the rescale gives the file's number back.
    assert full.expected == 34.12


def test_an_expected_value_on_a_half_cent_rounds_half_up(ep, games, scoring, tmp_path):
    # round() gives 16.8 for 16.805, because the float sits just under the half. The reader rounds half up.
    half = tmp_path / "ep_weekly_2026.csv"
    half.write_text(ep.read_text().replace("2026,6,2026_06_DAL_GB,00-0033077,Dak Prescott,QB,0,1.16,25.19",
                                           "2026,6,2026_06_DAL_GB,00-0033077,Dak Prescott,QB,0,0,16.805"))
    assert read_expected(half, games, 2026, 6, scoring, SLEEPER_OF_GSIS).players["3294"][-1].expected == 16.81


def test_the_monday_night_game_in_the_file_reads_week_n(ep, games, scoring):
    expected = read_expected(ep, games, 2026, 6, scoring, SLEEPER_OF_GSIS)
    assert expected.through_week == 6
    assert expected.players["4034"][-1].week == 6


def test_without_the_monday_night_game_the_file_reads_through_week_n_minus_1(ep, games, scoring, tmp_path):
    lagged = tmp_path / "ep_weekly_2026.csv"
    lines = ep.read_text().splitlines(keepends=True)
    lagged.write_text("".join(line for line in lines if "2026_06_WAS_SF" not in line))
    expected = read_expected(lagged, games, 2026, 6, scoring, SLEEPER_OF_GSIS)
    assert expected.through_week == 5
    assert all(g.week <= 5 for games_ in expected.players.values() for g in games_)


def test_the_games_of_a_later_week_stay_out(ep, games, scoring):
    # The file holds the Thursday game of week 7, but week 7 is not done, so the data reads through week 6.
    expected = read_expected(ep, games, 2026, 7, scoring, SLEEPER_OF_GSIS)
    assert expected.through_week == 6
    assert [g.week for g in expected.players["5859"]] == [1, 6]


def test_the_window_is_the_last_3_games_played_and_a_bye_is_not_a_game(ep, games, scoring):
    # Patrick Mahomes had a bye in week 5, so his last 3 games are weeks 3, 4, and 6. The file lists the
    # games of some players out of week order, so the order comes from the reader.
    expected = read_expected(ep, games, 2026, 6, scoring, SLEEPER_OF_GSIS)
    assert [g.week for g in expected.players["4046"]] == [3, 4, 6]


def test_a_player_with_no_gsis_id_is_skipped(ep, games, scoring):
    # The file has rows with NA for player_id, and the map has no entry for most of the fixture players.
    expected = read_expected(ep, games, 2026, 6, scoring, SLEEPER_OF_GSIS)
    assert set(expected.players) == set(SLEEPER_OF_GSIS.values())


def test_a_schedule_without_week_n_gives_none(ep, games, scoring):
    # With no game of week N in the schedules, the reader cannot tell a lagged file from a full one.
    assert read_expected(ep, games, 2026, 25, scoring, SLEEPER_OF_GSIS) is None


def test_the_window_gap_is_the_mean_of_actual_minus_expected_and_one_game_gives_none():
    def game(week):
        return ExpectedGame(week=week, game_id=f"2026_{week:02d}_X", expected=10.0)

    assert window_gap([], {}) is None
    assert window_gap([game(6)], {6: 14.0}) is None
    assert window_gap([game(5), game(6)], {5: 14.0, 6: 9.0}) == 1.5
    assert window_gap([game(3), game(4), game(6)], {3: 11.0, 4: 12.0, 6: 14.5}) == 2.5


def test_a_game_with_no_actual_points_is_not_in_the_window_gap():
    games_ = [ExpectedGame(week=w, game_id=f"2026_{w:02d}_X", expected=10.0) for w in (4, 5, 6)]
    assert window_gap(games_, {5: 13.0, 6: 9.0}) == 1.0
    assert window_gap(games_, {6: 9.0}) is None


def test_a_window_gap_on_a_half_cent_rounds_half_up():
    # round() gives 5.12 for 5.125, because it rounds half to even. The gap rounds half up.
    games_ = [ExpectedGame(week=w, game_id=f"2026_{w:02d}_X", expected=10.0) for w in (5, 6)]
    assert window_gap(games_, {5: 15.125, 6: 15.125}) == 5.13


def test_the_window_gap_on_the_fixture_takes_the_league_points(ep, games, scoring):
    # Patrick Mahomes, weeks 3, 4, and 6, with hand-set actual points of the league.
    window = read_expected(ep, games, 2026, 6, scoring, SLEEPER_OF_GSIS).players["4046"]
    actual = {g.week: g.expected + 3.0 for g in window}
    assert window_gap(window, actual) == 3.0


def test_the_window_gap_of_a_fixture_player_with_one_game_is_none(ep, games, scoring):
    # A.J. Brown played week 1 and week 6, so through week 1 he has one game.
    expected = read_expected(ep, games, 2026, 1, scoring, SLEEPER_OF_GSIS)
    assert len(expected.players["5859"]) == 1 and window_gap(expected.players["5859"], {1: 20.0}) is None


def test_the_nflverse_week_carries_the_expected_points_by_sleeper_id(nfl_week6):
    assert nfl_week6.sources["ffopportunity"] is True
    assert nfl_week6.expected.through_week == 6
    assert nfl_week6.expected.players["4034"][-1].expected == 30.07


def test_a_missing_file_gives_none_and_a_false_source(tmp_path, scoring):
    def boom(url):
        raise httpx.ConnectError("down")

    nfl = nflverse_week(2026, 6, [], {"4034": {"position": "RB", "gsis_id": "00-0033280"}}, tmp_path,
                        fetch=boom, scoring=scoring)
    assert nfl.expected is None
    assert nfl.sources["ffopportunity"] is False
