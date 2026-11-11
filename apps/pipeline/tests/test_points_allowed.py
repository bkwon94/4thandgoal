"""
Tests for the points allowed per position per defense.
They read the weekly stats of the history fixture.
"""
import json
import shutil

from league.points_allowed import most_points_text, points_allowed, rank_word


def test_points_allowed_ranks_a_defense_at_a_position(fixture_history_root):
    allowed = points_allowed(fixture_history_root, 5)
    # Worked by hand from the stat lines of weeks 1 to 5: SF gave up 90.1 half-PPR points to running backs
    # in 5 games, and NO gave up 139.1.
    assert (allowed["SF"]["RB"].points, allowed["SF"]["RB"].rank) == (18.02, 15)
    assert (allowed["NO"]["RB"].points, allowed["NO"]["RB"].rank) == (27.82, 1)
    assert allowed["SF"]["QB"].rank == 31


def test_points_allowed_counts_only_the_weeks_through_the_given_one(fixture_history_root):
    assert points_allowed(fixture_history_root, 4)["NO"]["RB"].games == 4


def test_points_allowed_counts_the_games_each_defense_played(fixture_history_root):
    allowed = points_allowed(fixture_history_root, 5)
    assert (allowed["SF"]["RB"].games, allowed["KC"]["RB"].games) == (5, 4)


def test_points_allowed_ranks_by_the_game_so_a_bye_does_not_help(tmp_path):
    def write(week, lines):
        path = tmp_path / f"week-{week:02d}"
        path.mkdir()
        (path / "stats.json").write_text(json.dumps(
            [{"player": {"position": "RB"}, "opponent": team, "stats": {"pts_half_ppr": points}}
             for team, points in lines]))

    # AAA gives up 20 in two games and BBB gives up 12 in one game and has its bye in week 2.
    write(1, [("AAA", 10), ("BBB", 12)])
    write(2, [("AAA", 10)])
    allowed = points_allowed(tmp_path, 2)
    assert (allowed["AAA"]["RB"].points, allowed["AAA"]["RB"].games, allowed["AAA"]["RB"].rank) == (10.0, 2, 2)
    assert (allowed["BBB"]["RB"].points, allowed["BBB"]["RB"].games, allowed["BBB"]["RB"].rank) == (12.0, 1, 1)


def test_points_allowed_with_a_missing_week_is_none(fixture_history_root, tmp_path):
    shutil.copytree(fixture_history_root, tmp_path / "history")
    (tmp_path / "history" / "week-03" / "stats.json").unlink()
    assert points_allowed(tmp_path / "history", 5) is None


def test_points_allowed_with_an_outage_week_is_none(fixture_history_root, tmp_path):
    shutil.copytree(fixture_history_root, tmp_path / "history")
    (tmp_path / "history" / "week-03" / "stats.json").write_text(json.dumps([]))
    assert points_allowed(tmp_path / "history", 5) is None


def test_rank_1_reads_the_most_points_and_a_rank_in_the_top_half_reads_its_ordinal():
    assert most_points_text(1, "WR", 32) == "the most points to WRs"
    assert most_points_text(3, "WR", 32) == "3rd most points to WRs"
    assert most_points_text(16, "WR", 32) == "16th most points to WRs"


def test_a_rank_in_the_bottom_half_reads_fewest_points_counted_from_the_other_end():
    # A high ordinal of "most points" reads like a soft defense, so the bottom half names the fewest.
    assert most_points_text(17, "RB", 32) == "16th fewest points to RBs"
    assert most_points_text(29, "RB", 32) == "4th fewest points to RBs"
    assert most_points_text(32, "RB", 32) == "the fewest points to RBs"


def test_the_middle_rank_of_an_odd_count_reads_most_points():
    assert most_points_text(16, "TE", 31) == "16th most points to TEs"
    assert most_points_text(17, "TE", 31) == "15th fewest points to TEs"


def test_the_rank_word_is_the_text_without_the_position():
    assert rank_word(1, 32) == "the most"
    assert rank_word(7, 32) == "7th most"
    assert rank_word(28, 32) == "5th fewest"
    assert rank_word(32, 32) == "the fewest"
