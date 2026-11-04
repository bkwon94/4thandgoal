"""
Tests for the league values the client carries: the league id per season, and the sizes the League settings drive.
A copy of the CPC settings with other sizes stands in for another league, so each size is a parameter, not a constant.
"""
import pytest
from cpc import cpc_client
from pydantic import ValidationError

from facts.chapters import RANKINGS_CHAPTER
from league.parse import parse_week
from league.provider.sleeper import load_raw
from league.standings_table import standings
from week.sheet.base import sentence_range


def test_the_league_id_comes_from_the_season():
    client = cpc_client()
    assert client.league_id(2026) == "1386167364424318976"
    with pytest.raises(ValueError, match="2031"):
        client.league_id(2031)


def test_the_client_is_frozen():
    with pytest.raises(ValidationError):
        cpc_client().slug = "other"


def test_the_published_team_has_no_owner_flag(fixture_raw_dir):
    team = parse_week(load_raw(fixture_raw_dir)).teams[6]
    assert "is_brian" not in team.model_dump()
    assert "is_brian" not in team.model_dump_json()


def test_the_standings_cut_follows_the_playoff_spots_of_the_settings(fixture_raw_dir):
    # A league with four playoff spots puts four teams in, not the six of CPC.
    week = parse_week(load_raw(fixture_raw_dir))
    client = cpc_client()
    four = cpc_client(playoff_spots=4)
    assert [s.in_playoffs for s in standings(week, client=client)].count(True) == client.settings.playoff_spots
    assert [s.in_playoffs for s in standings(week, client=four)].count(True) == 4


def test_a_ten_team_league_changes_the_grade_spare_rank_and_the_rankings_range():
    # The spare rank and the rankings range follow the team count, so a smaller league asks for fewer of each.
    client = cpc_client()
    ten = cpc_client(team_count=10)
    assert ten.settings.grade_spare_rank == {"QB": 10, "RB": 20, "WR": 20, "TE": 10}
    assert sentence_range(RANKINGS_CHAPTER, ten) != sentence_range(RANKINGS_CHAPTER, client)
    assert sentence_range(RANKINGS_CHAPTER, ten) == (10, 30)


def test_the_parse_stops_on_a_team_count_that_does_not_match_the_settings(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    with pytest.raises(ValueError, match="10"):
        parse_week(raw, team_count=10)
    assert len(parse_week(raw, team_count=cpc_client().settings.team_count).teams) == 12
