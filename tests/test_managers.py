"""
Tests for the managers module, the entries of the managers file.
They run on the fixture history, as the power rankings tests do.
"""
from cornerstone.history import load_history
from cornerstone.managers import managers
from cornerstone.parse import parse_week, player_name
from cornerstone.season_inputs import SeasonInputs
from cornerstone.provider.sleeper import load_raw
from cornerstone.standings_table import season_records


def _inputs(raw_dir, root):
    raw = load_raw(raw_dir)
    return load_history(root, raw, week=6), parse_week(raw).teams


def test_twelve_entries_in_roster_id_order(fixture_raw_dir, fixture_history_root):
    history, teams = _inputs(fixture_raw_dir, fixture_history_root)
    entries = managers(SeasonInputs(history=history), teams)
    assert [e.roster_id for e in entries] == list(range(1, 13))


def test_each_entry_carries_the_team(fixture_raw_dir, fixture_history_root):
    history, teams = _inputs(fixture_raw_dir, fixture_history_root)
    for entry in managers(SeasonInputs(history=history), teams):
        team = teams[entry.roster_id]
        assert (entry.team.name, entry.team.owner, entry.team.avatar_url) == (team.name, team.owner, team.avatar_url)


def test_the_record_counts_both_games_of_every_week(fixture_raw_dir, fixture_history_root):
    history, teams = _inputs(fixture_raw_dir, fixture_history_root)
    records = season_records(history, 6)
    for entry in managers(SeasonInputs(history=history), teams):
        assert (entry.wins, entry.losses, entry.points_for) == records[entry.roster_id]
        # Six weeks of two games each, so a record with no tie sums to twelve.
        assert entry.wins + entry.losses <= 12


def test_each_entry_carries_named_best_adds_and_top_performers(fixture_raw_dir, fixture_history_root):
    history, teams = _inputs(fixture_raw_dir, fixture_history_root)
    players = load_raw(fixture_raw_dir).players
    entries = managers(SeasonInputs(history=history), teams, players)
    assert any(e.best_adds for e in entries)
    for entry in entries:
        assert len(entry.best_adds) <= 3
        assert len(entry.top_performers) == 5
        points = [p.points for p in entry.top_performers]
        assert points == sorted(points, reverse=True)
        for performer in entry.top_performers:
            assert performer.name == player_name(performer.player_id, players.get(performer.player_id))
