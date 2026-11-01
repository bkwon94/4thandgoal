"""
Tests for the league config and the owner flag it drives in the parse.
A second config literal stands in for another league, so the owner is a parameter and not a constant.
"""
from pathlib import Path

import pytest
from pydantic import ValidationError

from cornerstone.config import LeagueConfig, cornerstone_config
from cornerstone.parse import parse_week
from cornerstone.sleeper import load_raw

# Another league with the same raw data, owned by the manager of roster 12.
OTHER = LeagueConfig(
    slug="other", display_name="Other League", provider="sleeper", league_ids={2026: "1"},
    owner_username="pdurkim", timezone="America/Chicago", prompts_dir=Path("prompts"),
)


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
