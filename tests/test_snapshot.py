"""
Tests for the snapshot the trade analyzer grades from.
They build it from the recorded week 6 data and the week 6 trade values, with no network.
"""
import shutil
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from cornerstone.sleeper import load_raw
from cornerstone.slow_sources import SlowSources, load_slow_sources
from cornerstone.snapshot import KnownGames, build_snapshot, load_snapshot


def test_week_6_snapshot_holds_rosters_teams_standings_and_slots(fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    assert snap.season == 2026
    assert sorted(snap.rosters) == list(range(1, 13))
    assert "7569" in snap.rosters[4]
    assert "4034" in snap.rosters[3]
    assert snap.players["7569"].name == "Nico Collins"
    assert snap.players["7569"].position == "WR"
    assert len(snap.teams) == 12
    assert [s.rank for s in snap.standings] == list(range(1, 13))
    assert snap.roster_positions[:3] == ["QB", "RB", "RB"]


def test_week_6_snapshot_is_the_trade_week_and_its_inputs_end_at_week_5(
        fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    assert snap.week == 6
    assert snap.chart == chart_week6
    assert snap.as_of.chart_week == 6
    assert snap.as_of.stats_through == 5
    assert snap.as_of.completed_through == 5
    # A saved week grades from the saved history only, so the raw week 6 games stay out of it.
    assert sorted(snap.stats.weeks) == [1, 2, 3, 4, 5]
    assert snap.as_of.known_games is None
    assert snap.stale == []


def test_week_6_standings_count_the_games_of_weeks_1_to_5(fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    # Each week is two games for each of the 12 rosters: the head-to-head game and the median game.
    games = sum(s.wins + s.losses for s in snap.standings)
    assert games == 5 * 2 * 12


def test_a_history_without_week_5_stamps_the_last_week_it_holds_and_notes_it(
        fixture_raw_dir, fixture_history_root, chart_week6, tmp_path):
    root = tmp_path / "history"
    shutil.copytree(fixture_history_root, root)
    shutil.rmtree(root / "week-05")
    snap = load_snapshot(fixture_raw_dir, root, chart_week6)
    assert snap.week == 6
    assert snap.as_of.stats_through == 4
    assert snap.as_of.completed_through == 4
    assert sorted(snap.stats.weeks) == [1, 2, 3, 4]
    assert snap.stale == ["history"]


def test_slow_sources_are_empty_and_named_as_missing(fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    assert snap.injuries is None
    assert snap.schedules is None
    assert snap.depth_charts is None
    assert snap.points_allowed is None
    assert snap.id_map is None
    assert snap.expected is None and snap.wopr is None
    assert snap.missing == ["schedules", "depth_charts", "id_map", "points_allowed", "injuries", "expected_points",
                            "player_weeks"]


def test_slow_sources_fill_the_snapshot_and_only_the_files_not_in_the_cache_stay_missing(
        fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    cache = tmp_path / "nflverse"
    cache.mkdir()
    for name in ("games.csv", "depth_charts_2026.csv.gz", "db_playerids.csv", "injuries_2026.csv.gz"):
        shutil.copy(fixture_nflverse_dir / name, cache / name)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow)
    assert snap.schedules == slow.schedules and snap.schedules
    assert snap.depth_charts == slow.depth_charts and snap.depth_charts
    assert snap.id_map == slow.id_map and snap.id_map
    assert snap.points_allowed == slow.points_allowed and snap.points_allowed
    assert snap.injuries == slow.injuries and snap.injuries
    # The cache holds neither the expected points file nor the weekly player file, so only those two are missing.
    assert snap.missing == ["expected_points", "player_weeks"]


def test_a_week_with_no_chart_has_no_chart_week(fixture_raw_dir, fixture_history_root):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, None)
    assert snap.chart is None
    assert snap.as_of.chart_week is None
    assert "chart" in snap.missing


def test_the_returns_file_gives_the_return_week_and_sleeper_gives_the_injury_status(
        fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    # Brian keeps the returns file by hand. Josh Jacobs, suspended in week 6, is back in week 7.
    assert snap.returns == {"5850": 7}
    assert snap.players["5850"].injury_status == "NA"
    assert snap.players["7569"].injury_status is None
    assert "returns" not in snap.missing


def test_a_season_with_no_returns_file_has_no_return_weeks_and_names_it_as_missing(
        fixture_raw_dir, fixture_history_root, chart_week6, tmp_path):
    # The returns file sits beside the history, so a history root with no sibling file has none.
    history_root = tmp_path / "2026" / "history"
    shutil.copytree(fixture_history_root, history_root)
    snap = load_snapshot(fixture_raw_dir, history_root, chart_week6)
    assert snap.returns == {}
    assert snap.missing[-1] == "returns"


def test_the_snapshot_carries_the_wopr_by_player_and_week(fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, SlowSources(wopr={"12501": {5: 58}}))
    assert snap.wopr == {"12501": {5: 58}}
    assert load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6).wopr is None


def test_the_snapshot_carries_the_projections_ahead_by_player_and_week(
        fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    # Josh Jacobs has his bye in week 11, so that week has no row.
    assert snap.projections_ahead["5850"] == {7: 10.81, 8: 14.19, 9: 12.41, 10: 11.0, 12: 11.39, 13: 13.25, 14: 12.4}


def test_the_projections_ahead_start_at_the_raw_week(fixture_raw_dir, fixture_history_root, chart_week6):
    # A player due back in the raw week counts for that week too, so its half-PPR projection joins the weeks ahead.
    # Nico Collins has his bye in week 8, so that week has no row.
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    assert snap.projections_ahead["7569"] == {
        6: 15.52, 7: 15.29, 9: 15.25, 10: 14.48, 11: 15.16, 12: 14.88, 13: 15.43, 14: 16.6}


def test_a_week_with_no_projections_ahead_file_has_none(fixture_raw_dir, fixture_history_root, chart_week6, tmp_path):
    raw_dir = tmp_path / "raw"
    shutil.copytree(fixture_raw_dir, raw_dir)
    (raw_dir / "projections_ahead.json").unlink()
    snap = load_snapshot(raw_dir, fixture_history_root, chart_week6)
    assert snap.projections_ahead is None
    # The missing list stays as it is. The fit reason says the projections are not available when a player is due back.
    assert "projections_ahead" not in snap.missing and "projections" not in snap.missing


# The game of the Bills and the Dolphins in week 6. A raw without its stat lines holds 13 games of 26 teams.
BUF_MIA = "202610602"


def _known_games_raw(fixture_raw_dir, drop_game=None):
    """The week 6 raw as a fetch on a game day of week 6 gives it, with the stat lines of `drop_game` left out."""
    raw = load_raw(fixture_raw_dir)
    raw["stats"] = [row for row in raw["stats"] if row.get("game_id") != drop_game]
    return raw


def test_a_trade_week_with_stat_lines_reads_its_known_games_and_keeps_the_standings_at_the_week_before(
        fixture_raw_dir, fixture_history_root, chart_week6):
    raw = _known_games_raw(fixture_raw_dir, drop_game=BUF_MIA)
    snap = build_snapshot(raw, fixture_history_root, chart_week6, trade_week=6)
    assert snap.week == 6
    assert snap.as_of.stats_through == 6
    assert snap.as_of.completed_through == 5
    assert sorted(snap.stats.weeks) == [1, 2, 3, 4, 5, 6]
    assert len({row["team"] for row in raw["stats"]}) == 26
    assert snap.as_of.known_games == KnownGames(week=6, games=13, in_progress=0, pending={})
    assert snap.stale == []


def test_the_standings_of_a_known_games_week_count_the_games_of_weeks_1_to_5_only(
        fixture_raw_dir, fixture_history_root, chart_week6):
    saved = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    known = build_snapshot(_known_games_raw(fixture_raw_dir), fixture_history_root, chart_week6, trade_week=6)
    assert sum(s.wins + s.losses for s in known.standings) == 5 * 2 * 12
    # The week 6 scores would move the records and the points for, so the same standings show week 6 is left out.
    assert known.standings == saved.standings


def test_a_trade_week_with_no_stat_lines_keeps_the_bound_at_the_week_before_and_reads_zero_games(
        fixture_raw_dir, fixture_history_root, chart_week6):
    # A good fetch before the first week 6 game gives an empty list. Nothing failed, so nothing is stale.
    raw = load_raw(fixture_raw_dir)
    raw["stats"] = []
    snap = build_snapshot(raw, fixture_history_root, chart_week6, trade_week=6)
    assert snap.as_of.stats_through == 5
    assert snap.as_of.completed_through == 5
    assert sorted(snap.stats.weeks) == [1, 2, 3, 4, 5]
    assert snap.as_of.known_games == KnownGames(week=6, games=0)
    assert snap.stale == []


def test_a_trade_week_with_only_lines_of_active_players_keeps_the_bound_at_the_week_before(
        fixture_raw_dir, fixture_history_root, chart_week6):
    # Before a kickoff Sleeper posts a line with only gms_active for each active player, and no game is played.
    raw = load_raw(fixture_raw_dir)
    for row in raw["stats"]:
        row["stats"] = {"gms_active": 1.0}
    snap = build_snapshot(raw, fixture_history_root, chart_week6, trade_week=6)
    assert snap.as_of.stats_through == 5
    assert sorted(snap.stats.weeks) == [1, 2, 3, 4, 5]
    assert snap.as_of.known_games == KnownGames(week=6, games=0)
    assert snap.stale == []


def test_a_failed_stats_fetch_keeps_the_bound_at_the_week_before_and_names_the_stats_stale(
        fixture_raw_dir, fixture_history_root, chart_week6):
    # The fetch gives no stats when the call fails, and a raw can also lack the key.
    failed = load_raw(fixture_raw_dir)
    failed["stats"] = None
    absent = load_raw(fixture_raw_dir)
    del absent["stats"]
    for raw in (failed, absent):
        snap = build_snapshot(raw, fixture_history_root, chart_week6, trade_week=6)
        assert snap.as_of.stats_through == 5
        assert sorted(snap.stats.weeks) == [1, 2, 3, 4, 5]
        assert snap.as_of.known_games is None
        assert snap.stale == ["stats"]


# The game of the Bears at the Falcons in week 6 kicks off at 1 pm Eastern on Sunday 2026-10-18.
EASTERN = ZoneInfo("America/New_York")
CHI_ATL_KICKOFF = datetime(2026, 10, 18, 13, 0, tzinfo=EASTERN)
CHI_ATL = SlowSources(kickoffs={"CHI": CHI_ATL_KICKOFF, "ATL": CHI_ATL_KICKOFF})


def test_a_game_2_hours_after_its_kickoff_is_in_progress_and_the_block_counts_it(
        fixture_raw_dir, fixture_history_root, chart_week6):
    snap = build_snapshot(load_raw(fixture_raw_dir), fixture_history_root, chart_week6, CHI_ATL, trade_week=6,
                          now=CHI_ATL_KICKOFF + timedelta(hours=2))
    assert snap.as_of.known_games == KnownGames(week=6, games=14, in_progress=1)
    assert snap.in_progress_teams == {"CHI", "ATL"}


def test_a_game_5_hours_after_its_kickoff_is_final_and_the_block_counts_zero_in_progress(
        fixture_raw_dir, fixture_history_root, chart_week6):
    snap = build_snapshot(load_raw(fixture_raw_dir), fixture_history_root, chart_week6, CHI_ATL, trade_week=6,
                          now=CHI_ATL_KICKOFF + timedelta(hours=5))
    assert snap.as_of.known_games == KnownGames(week=6, games=14, in_progress=0)
    assert snap.in_progress_teams == set()


def test_a_game_with_no_schedule_row_is_final(fixture_raw_dir, fixture_history_root, chart_week6):
    # The schedules hold only the Bears and the Falcons, so the 1 pm game of the Ravens and the Browns has no row.
    # At 3 pm both 1 pm games are on, but only the game with a row counts as in progress.
    snap = build_snapshot(load_raw(fixture_raw_dir), fixture_history_root, chart_week6, CHI_ATL, trade_week=6,
                          now=CHI_ATL_KICKOFF + timedelta(hours=2))
    assert snap.as_of.known_games.in_progress == 1
    assert "BAL" not in snap.in_progress_teams and "CLE" not in snap.in_progress_teams


def test_a_saved_week_has_no_game_in_progress(fixture_raw_dir, fixture_history_root, chart_week6):
    snap = build_snapshot(load_raw(fixture_raw_dir), fixture_history_root, chart_week6, CHI_ATL,
                          now=CHI_ATL_KICKOFF + timedelta(hours=2))
    assert snap.as_of.known_games is None
    assert snap.in_progress_teams == set()


def test_on_the_tuesday_roll_the_raw_week_joins_the_history_and_the_new_trade_week_has_no_known_games(
        fixture_raw_dir, fixture_history_root, chart_week6):
    snap = build_snapshot(load_raw(fixture_raw_dir), fixture_history_root, chart_week6, trade_week=7)
    assert snap.week == 7
    assert snap.as_of.stats_through == 6
    assert snap.as_of.completed_through == 6
    assert sum(s.wins + s.losses for s in snap.standings) == 6 * 2 * 12
    assert snap.as_of.known_games is None
    assert snap.stale == []


# The game of the Packers in week 6.
GB_GAME = "202610612"


def _without_snaps(raw, game_ids):
    """The raw with no snap count on the lines of `game_ids`, as Sleeper posts a Sunday game on Sunday night."""
    for row in raw["stats"]:
        if row.get("game_id") in game_ids:
            row["stats"] = {key: value for key, value in row["stats"].items() if key not in ("off_snp", "tm_off_snp")}
    return raw


def test_a_known_game_with_no_snap_count_is_pending_for_snaps(fixture_raw_dir, fixture_history_root, chart_week6):
    raw = _without_snaps(load_raw(fixture_raw_dir), {BUF_MIA, GB_GAME})
    snap = build_snapshot(raw, fixture_history_root, chart_week6, trade_week=6)
    assert snap.as_of.stats_through == 6
    assert snap.as_of.known_games == KnownGames(week=6, games=14, pending={"snaps": 2})


def test_a_known_game_with_snap_counts_is_pending_for_nothing(fixture_raw_dir, fixture_history_root, chart_week6):
    # A final week has lines of players with no offense snap, because Sleeper leaves out a 0. They are no pending game.
    snap = build_snapshot(load_raw(fixture_raw_dir), fixture_history_root, chart_week6, trade_week=6)
    assert snap.as_of.known_games == KnownGames(week=6, games=14, pending={})


def test_a_player_file_with_no_row_of_the_trade_week_names_usage_pending_for_each_game_it_lacks(
        fixture_raw_dir, fixture_history_root, chart_week6):
    # Watson of the Packers has a week 6 row, so only the Packers game has its WOPR.
    # The usage of the other 13 games is pending.
    wopr = {"8167": {5: 50, 6: 60}, "11620": {5: 70}}
    snap = build_snapshot(load_raw(fixture_raw_dir), fixture_history_root, chart_week6, trade_week=6,
                          slow=SlowSources(wopr=wopr))
    assert snap.as_of.known_games.pending == {"usage": 13}
    no_week_6 = {"8167": {5: 50}, "11620": {5: 70}}
    snap = build_snapshot(load_raw(fixture_raw_dir), fixture_history_root, chart_week6, trade_week=6,
                          slow=SlowSources(wopr=no_week_6))
    assert snap.as_of.known_games.pending == {"usage": 14}


def test_a_missing_player_file_is_a_missing_source_and_not_a_pending_count(
        fixture_raw_dir, fixture_history_root, chart_week6):
    snap = build_snapshot(load_raw(fixture_raw_dir), fixture_history_root, chart_week6, trade_week=6,
                          slow=SlowSources(missing=["player_weeks"]))
    assert snap.as_of.known_games.pending == {}
    assert "player_weeks" in snap.missing


# The week 6 rank pool reads the saved weeks 1 to 5. Lineup value reads weeks 2 to 5, LINEUP_WEEKS of them.
# The ranks below come from a hand count of the RB lines in the saved history, not from the code.
TUTEN, JACOBS, FREE_AGENT_RB = "12490", "5850", "9226"
NO_GAME_RBS = ("12476", "8205")


def test_week_6_ranks_tuten_rb15_by_lineup_value(fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    # Tuten scored about 12.48 points per game in 4 games of weeks 2 to 5. 14 backs have more.
    # The 14, by points per game of weeks 2 to 5. "ahead" marks a back out now who counts for his projection ahead.
    # Jahmyr Gibbs 27.28, Kenneth Walker 23.83, Bijan Robinson 21.22, Kyren Williams 20.45, James Cook 19.10, Jaylen
    # Warren 18.92, Derrick Henry 18.25, Christian McCaffrey 17.62, Chuba Hubbard 17.27, Jonathan Taylor 16.82, Javonte
    # Williams 16.20, Bucky Irving 13.60, Aaron Jones 13.30, Saquon Barkley 12.64 ahead.
    assert snap.position_rank(TUTEN) == 15


def test_a_player_with_no_game_in_the_window_ranks_after_every_player_with_a_game(
        fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    # 77 backs have a stat line in weeks 1 to 5 or a roster spot. The two with no game in weeks 2 to 5 are last.
    assert sorted(snap.position_rank(pid) for pid in NO_GAME_RBS) == [76, 77]


def test_a_rostered_player_due_back_ranks_by_his_projection_ahead(fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    # Jacobs has no game in weeks 2 to 5, so his recent points would rank him last. The returns file has him
    # back in week 7, and his projections of weeks 7 to 14 give 12.21 per game.
    assert snap.returns[JACOBS] == 7
    assert snap.position_rank(JACOBS) == 16


def test_a_free_agent_with_a_stat_line_ranks_in_the_pool(fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    # The back is on no roster. He scored 12.5 points in 2 games, 6.25 per game, so 45 backs rank above him.
    assert all(FREE_AGENT_RB not in players for players in snap.rosters.values())
    assert snap.position_rank(FREE_AGENT_RB) == 46


def test_k_def_and_a_player_with_no_stat_line_and_no_roster_spot_have_no_rank(
        fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    defense = next(pid for players in snap.rosters.values() for pid in players
                   if snap.players[pid].position == "DEF")
    assert snap.position_rank(defense) is None
    assert snap.position_rank("no-such-player") is None


def test_a_copy_of_the_snapshot_ranks_from_its_own_data(fixture_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)
    assert snap.position_rank(JACOBS) == 16
    # With no projections file every player keeps his recent points. 6 backs then have no game in weeks 2 to 5,
    # so they hold ranks 72 to 77 in player id order. Jacobs is the third of them.
    assert snap.model_copy(update={"projections_ahead": None}).position_rank(JACOBS) == 74


ACHANE, RODRIGUEZ, BIGSBY, PERINE, GAINWELL, NO_LINE_BACK = "9226", "10219", "9225", "4147", "7567", "80001"


def test_the_week_6_snapshot_lists_the_free_agents_the_waiver_pool_reads_at_rb(
        free_agent_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(free_agent_raw_dir, fixture_history_root, chart_week6)
    # Bigsby is Active, Perine is Inactive and out as a stash, and the back with no stat line is Active too.
    # The list is in player id order.
    assert [p.player_id for p in snap.free_agents["RB"]] == [PERINE, NO_LINE_BACK, BIGSBY]
    assert snap.free_agents["RB"][2].name == "Tank Bigsby"
    assert [p.player_id for p in snap.free_agents["TE"]] == ["2505"]
    # A free agent is not a rostered player, so the readers of the rosters never see him.
    assert BIGSBY not in snap.players


def test_a_named_inactive_free_agent_is_not_in_the_free_agents(free_agent_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(free_agent_raw_dir, fixture_history_root, chart_week6)
    # Achane is Inactive with no out tag. He still has a position rank, because his stat line is in the rank pool.
    assert ACHANE not in {p.player_id for p in snap.free_agents["RB"]}
    assert snap.position_rank(ACHANE) == 46


def test_a_free_agent_on_injured_reserve_with_no_out_tag_and_one_with_no_team_are_not_in_the_free_agents(
        free_agent_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(free_agent_raw_dir, fixture_history_root, chart_week6)
    assert {RODRIGUEZ, GAINWELL}.isdisjoint(p.player_id for p in snap.free_agents["RB"])


def test_the_best_free_agent_is_the_one_with_the_best_position_rank(
        free_agent_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(free_agent_raw_dir, fixture_history_root, chart_week6)
    # Bigsby scored 15.3 points in 3 games of weeks 2 to 5, 5.10 a game. Perine scored 20.1 in 4, 5.03 a game.
    # 50 backs have more lineup value than Bigsby, so he is RB51. The back with no stat line has no rank.
    player, rank = snap.best_free_agent(["RB"])
    assert (player.name, rank) == ("Tank Bigsby", 51)
    assert snap.position_rank(PERINE) == 53
    assert snap.position_rank(NO_LINE_BACK) is None


def test_a_position_with_no_free_agent_with_a_rank_has_no_best_free_agent(
        free_agent_raw_dir, fixture_history_root, chart_week6):
    snap = load_snapshot(free_agent_raw_dir, fixture_history_root, chart_week6)
    assert snap.best_free_agent(["QB"]) is None
    only_no_line = snap.model_copy(update={"free_agents": {"RB": snap.free_agents["RB"][1:2]}})
    assert only_no_line.best_free_agent(["RB"]) is None
