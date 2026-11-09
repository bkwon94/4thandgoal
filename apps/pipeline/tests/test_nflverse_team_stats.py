"""
Tests for the reader of the nflverse team stats file: the offense of each NFL team by expected points per play.
The fixture is the real 2026 file of nflverse cut to the columns the reader uses.
"""
from league.nflverse_team_stats import read_team_stats


def test_each_team_gets_its_games_its_expected_points_per_play_and_its_rank_through_the_week(fixture_nflverse_dir):
    teams = read_team_stats(fixture_nflverse_dir / "stats_team_week_2026.csv.gz", 5)
    assert len(teams) == 32
    # BUF scores the most expected points per play in weeks 1 to 5, and LAC the fewest.
    assert (teams["BUF"].rank, teams["BUF"].games, round(teams["BUF"].epa_per_play, 3)) == (1, 5, 0.213)
    assert (teams["LAC"].rank, teams["LAC"].games, round(teams["LAC"].epa_per_play, 3)) == (32, 5, -0.188)
    # KC has its bye in week 5, so it has four games.
    assert teams["KC"].games == 4


def test_the_rams_go_by_their_sleeper_code(fixture_nflverse_dir):
    teams = read_team_stats(fixture_nflverse_dir / "stats_team_week_2026.csv.gz", 5)
    assert "LAR" in teams and "LA" not in teams


def test_a_file_with_no_row_through_the_week_gives_none(fixture_nflverse_dir):
    assert read_team_stats(fixture_nflverse_dir / "stats_team_week_2026.csv.gz", 0) is None
