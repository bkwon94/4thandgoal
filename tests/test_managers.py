"""
Tests for the managers module, the entries of the managers file.
They run on the fixture history, as the power rankings tests do.
"""
from cornerstone.facts_league import season_records
from cornerstone.history import load_history
from cornerstone.managers import managers
from cornerstone.parse import parse_week
from cornerstone.sleeper import load_raw


def _inputs(raw_dir, root):
    raw = load_raw(raw_dir)
    return load_history(root, raw, week=6), parse_week(raw).teams


def test_twelve_entries_in_roster_id_order(fixture_raw_dir, fixture_history_root):
    history, teams = _inputs(fixture_raw_dir, fixture_history_root)
    entries = managers(history, teams)
    assert [e.roster_id for e in entries] == list(range(1, 13))


def test_each_entry_carries_the_team(fixture_raw_dir, fixture_history_root):
    history, teams = _inputs(fixture_raw_dir, fixture_history_root)
    for entry in managers(history, teams):
        team = teams[entry.roster_id]
        assert (entry.team.name, entry.team.owner, entry.team.avatar_url) == (team.name, team.owner, team.avatar_url)


def test_the_record_counts_both_games_of_every_week(fixture_raw_dir, fixture_history_root):
    history, teams = _inputs(fixture_raw_dir, fixture_history_root)
    records = season_records(history, 6)
    for entry in managers(history, teams):
        assert (entry.wins, entry.losses, entry.points_for) == records[entry.roster_id]
        # Six weeks of two games each, so a record with no tie sums to twelve.
        assert entry.wins + entry.losses <= 12
