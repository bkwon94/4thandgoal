"""
Tests for the league config, the owner flag it drives in the parse, and the playoff cut it drives in the standings.
A second config literal stands in for another league, so the owner and the sizes are parameters and not constants.
"""
from pathlib import Path

import pytest
from pydantic import ValidationError

from cornerstone.config import LeagueConfig, cornerstone_config
from cornerstone.parse import parse_week
from cornerstone.provider.sleeper import load_raw
from cornerstone.sheet.base import RANKINGS_CHAPTER, sentence_range
from cornerstone.standings_table import standings

# Another league with the same raw data, owned by the manager of roster 12. Its sizes are those of Cornerstone.
OTHER = cornerstone_config().model_copy(update=dict(
    slug="other", display_name="Other League", provider="sleeper", league_ids=((2026, "1"),),
    owner_username="pdurkim", timezone="America/Chicago", prompts_dir=Path("prompts"),
))


def _owners(raw: dict, config: LeagueConfig) -> list[int]:
    return [t.roster_id for t in parse_week(raw, config.owner_username).teams.values() if t.is_owner]


def test_the_owner_flag_follows_the_owner_username_of_the_config(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    assert _owners(raw, cornerstone_config()) == [6]
    assert _owners(raw, OTHER) == [12]


def test_a_parse_with_no_owner_flags_no_team(fixture_raw_dir):
    assert not any(t.is_owner for t in parse_week(load_raw(fixture_raw_dir)).teams.values())


def test_the_published_team_keeps_the_is_brian_field_name(fixture_raw_dir):
    # The site schema reads is_brian, so the rename stops at the Python name.
    team = parse_week(load_raw(fixture_raw_dir), cornerstone_config().owner_username).teams[6]
    assert team.model_dump()["is_brian"] is True
    assert "is_brian" in team.model_dump_json()
    assert type(team).model_validate_json(team.model_dump_json()).is_owner


def test_the_league_id_comes_from_the_season():
    assert OTHER.league_id(2026) == "1"
    with pytest.raises(ValueError, match="2031"):
        OTHER.league_id(2031)


def test_the_config_is_frozen():
    with pytest.raises(ValidationError):
        OTHER.owner_username = "someone"


def test_the_standings_cut_follows_the_playoff_spots_of_the_config(fixture_raw_dir):
    # A league with four playoff spots puts four teams in, not the six of Cornerstone.
    week = parse_week(load_raw(fixture_raw_dir))
    config = cornerstone_config()
    four = config.model_copy(update={"playoff_spots": 4})
    assert [s.in_playoffs for s in standings(week, config=config)].count(True) == config.playoff_spots
    assert [s.in_playoffs for s in standings(week, config=four)].count(True) == 4


def test_a_ten_team_league_changes_the_grade_spare_rank_and_the_rankings_range():
    # The spare rank and the rankings range follow the team count, so a smaller league asks for fewer of each.
    config = cornerstone_config()
    ten = config.model_copy(update={"team_count": 10})
    assert ten.grade_spare_rank != config.grade_spare_rank
    assert ten.grade_spare_rank == {"QB": 10, "RB": 20, "WR": 20, "TE": 10}
    assert sentence_range(RANKINGS_CHAPTER, ten) != sentence_range(RANKINGS_CHAPTER, config)
    assert sentence_range(RANKINGS_CHAPTER, ten) == (10, 30)


def test_a_ten_team_league_rounds_the_grade_quarter_down_and_keeps_the_shootout_top():
    # A quarter of ten teams rounds down to two, so ranks 1 and 2 read strong and ranks 9 and 10 read soft.
    config = cornerstone_config()
    ten = config.model_copy(update={"team_count": 10})
    assert (ten.grade_strong_rank, ten.grade_soft_rank) == (2, 9)
    # The shootout top is its own field, so the team count leaves it as it is.
    assert ten.shootout_top == config.shootout_top


def test_the_parse_stops_on_a_team_count_that_does_not_match_the_config(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    with pytest.raises(ValueError, match="10"):
        parse_week(raw, team_count=10)
    assert len(parse_week(raw, team_count=cornerstone_config().team_count).teams) == cornerstone_config().team_count
