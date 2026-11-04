"""
Tests for the League settings: the Sleeper adapter maps a season into them, and the sizes derive from them.
Each derived CPC value must equal the value of the old League config at commit 003c70c on main (AT-2).
"""
import json
from pathlib import Path

import pytest

from league.league_settings import LeagueSettings
from league.provider.raw import RawLeague
from league.provider.sleeper import SleeperProvider, league_settings

CPC_LEAGUE = Path(__file__).parents[3] / "clients" / "cpc" / "data" / "2026" / "league.json"


def _raw(**changes) -> RawLeague:
    data = json.loads(CPC_LEAGUE.read_text(encoding="utf-8"))
    for key, value in changes.items():
        if key == "roster_positions":
            data[key] = value
        elif key == "rec":
            data["scoring_settings"]["rec"] = value
        else:
            data["settings"][key] = value
    return RawLeague.model_validate(data)


@pytest.fixture
def cpc() -> LeagueSettings:
    return league_settings(_raw())


def test_the_cpc_sizes_equal_the_old_league_config(cpc):
    # The values of cornerstone_config() before the League config went away.
    assert cpc.team_count == 12
    assert cpc.playoff_spots == 6
    assert cpc.bye_count == 2
    assert cpc.last_regular_week == 14
    assert cpc.return_by_week == 14
    assert cpc.last_season_week == 17
    assert cpc.lines == {"QB": 24, "RB": 36, "WR": 36, "TE": 24}
    assert cpc.strength_rank == 24
    assert cpc.star_rank_by_position == {"QB": 6, "RB": 12, "WR": 12, "TE": 6}
    assert cpc.grade_spare_rank == {"QB": 12, "RB": 24, "WR": 24, "TE": 12}
    assert (cpc.grade_strong_rank, cpc.grade_soft_rank) == (3, 10)


def test_the_cpc_settings_carry_the_reception_points_and_the_median_game(cpc):
    assert cpc.reception_points == 0.5
    assert cpc.points_key == "pts_half_ppr"
    assert cpc.median_game is True
    assert cpc.roster_slots == ("QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "FLEX", "DEF")


@pytest.mark.parametrize(("rec", "key"), [(0, "pts_std"), (0.5, "pts_half_ppr"), (1, "pts_ppr")])
def test_the_reception_points_choose_the_points_key(rec, key):
    assert league_settings(_raw(rec=rec)).points_key == key


def test_another_reception_value_fails_with_a_plain_message():
    with pytest.raises(ValueError, match="0.75"):
        league_settings(_raw(rec=0.75))


def test_a_league_with_no_median_game_says_so():
    assert league_settings(_raw(league_average_match=0)).median_game is False


def test_a_ten_team_league_with_three_flex_slots_derives_its_own_sizes():
    settings = league_settings(_raw(num_teams=10, playoff_teams=4, roster_positions=[
        "QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "FLEX", "FLEX", "BN", "BN"]))
    assert settings.team_count == 10
    assert settings.bye_count == 0
    assert settings.last_season_week == 16
    assert settings.lines == {"QB": 20, "RB": 35, "WR": 35, "TE": 20}
    assert settings.strength_rank == 20
    assert settings.star_rank_by_position == {"QB": 5, "RB": 10, "WR": 10, "TE": 5}
    assert (settings.grade_strong_rank, settings.grade_soft_rank) == (2, 9)


def test_an_unknown_flex_slot_fails_with_its_name():
    with pytest.raises(ValueError, match="SUPER_FLEX"):
        league_settings(_raw(roster_positions=["QB", "SUPER_FLEX", "RB", "WR", "TE", "BN"]))


def test_the_sleeper_adapter_reads_the_cached_league_file_with_no_fetch(tmp_path):
    cache = tmp_path / "league.json"
    cache.write_text(CPC_LEAGUE.read_text(encoding="utf-8"), encoding="utf-8")
    assert SleeperProvider(tmp_path).fetch_settings("1386167364424318976", cache).team_count == 12


def test_the_cpc_roster_slots_start_no_kicker(cpc):
    # CPC has a DEF slot and no K slot, so K leaves the pool and the leaders.
    assert cpc.positions == ("QB", "RB", "WR", "TE", "DEF")


def test_a_flex_slot_starts_each_position_it_takes():
    # A league with no TE slot still starts a TE through its FLEX slots.
    settings = league_settings(_raw(roster_positions=["QB", "RB", "RB", "WR", "WR", "FLEX", "K", "BN"]))
    assert settings.positions == ("QB", "RB", "WR", "TE", "K")


def test_a_league_with_no_def_slot_starts_no_def():
    settings = league_settings(_raw(roster_positions=["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "BN"]))
    assert "DEF" not in settings.positions
