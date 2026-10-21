"""
Tests for the grade of a proposed trade: the start letter, consolidation, unlisted, and each adjuster.
They feed a proposed trade and the week 6 snapshot at the grade seam.
"""
import re
import shutil

import pytest

from cornerstone.rubric import ProposedTrade, TradeInputError, TradeSide, grade
from cornerstone.sleeper import load_raw
from cornerstone.slow_sources import load_slow_sources
from cornerstone.snapshot import build_snapshot, load_snapshot

# Week 6 trade values from the fixture: Collins 46.5 and Croskey-Merritt 24.0 on roster 4,
# McCaffrey 64.0 on roster 3, Kincaid 31.5 and Wilson 27.5 on roster 12,
# Harrison 36.0, Brian Robinson 22.0, and Bijan Robinson 20.5 on roster 7.
COLLINS, CROSKEY, MCCAFFREY = "7569", "12533", "4034"
KINCAID, WILSON = "10236", "8146"
HARRISON, B_ROBINSON, BIJAN = "11628", "8154", "9509"


@pytest.fixture
def snap(fixture_raw_dir, fixture_history_root, chart_week6):
    return load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)


@pytest.fixture
def slow_snap(fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    """The week 6 snapshot with the slow sources from the nflverse fixture: the depth chart, the id map, and the injuries."""
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    return load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow)


def _trade(a: int, a_gives: list[str], b: int, b_gives: list[str], asker: int | None = None) -> ProposedTrade:
    return ProposedTrade(season=2026, sides=(TradeSide(roster_id=a, gives=a_gives), TradeSide(roster_id=b, gives=b_gives)),
                         asker=a if asker is None else asker)


def _with_values(snap, values: dict[str, float]):
    chart = snap.chart.model_copy(update={"values": {**snap.chart.values, **values}})
    return snap.model_copy(update={"chart": chart})


def _letters(result) -> list[str]:
    return [side.start_letter for side in result]


# McCaffrey is set to 20, so the ratio for roster 3 is Collins over 20, at each band's lower bound.
@pytest.mark.parametrize("got, letter", [(25.0, "A"), (22.0, "B"), (18.0, "C"), (15.0, "D"), (14.5, "F")])
def test_each_band_starts_at_its_lower_bound(snap, got, letter):
    snap = _with_values(snap, {MCCAFFREY: 20.0, COLLINS: got})
    result = grade(_trade(3, [MCCAFFREY], 4, [COLLINS]), snap)
    assert result[0].roster_id == 3
    assert result[0].start_letter == letter


def test_a_real_one_for_one_gives_each_side_its_own_letter(snap):
    # Roster 4 gets 31.5 for 24.0, a ratio of 1.3125. Roster 12 gets 24.0 for 31.5, a ratio of 0.762.
    result = grade(_trade(4, [CROSKEY], 12, [KINCAID]), snap)
    assert _letters(result) == ["A", "D"]


def test_consolidation_divides_the_depth_side_sum_by_the_margin(snap):
    # Roster 12 gives 31.5 plus 27.5, which is 59.0, and counts as 47.2 against Collins at 46.5.
    # With no discount the letters are A for roster 4 and D for roster 12.
    result = grade(_trade(4, [COLLINS], 12, [KINCAID, WILSON]), snap)
    assert _letters(result) == ["C", "C"]
    assert all("one player for two or more" in side.reason for side in result)


def test_a_three_for_two_gets_no_discount(snap):
    # Roster 7 gives 78.5 and gets 59.0, a ratio of 0.752. Roster 12 gets a ratio of 1.331.
    result = grade(_trade(7, [HARRISON, B_ROBINSON, BIJAN], 12, [KINCAID, WILSON]), snap)
    assert _letters(result) == ["D", "A"]
    assert not any("one player for two or more" in side.reason for side in result)


def test_an_unlisted_player_starts_both_sides_at_c(snap):
    unlisted = next(pid for pid in snap.rosters[1] if pid not in snap.chart.values)
    result = grade(_trade(1, [unlisted], 4, [COLLINS]), snap)
    assert _letters(result) == ["C", "C"]
    name = snap.players[unlisted].name
    assert all(f"{name} has no trade value" in side.reason for side in result)


def test_a_week_with_no_chart_starts_both_sides_at_c(snap):
    result = grade(_trade(4, [CROSKEY], 12, [KINCAID]), snap.model_copy(update={"chart": None}))
    assert _letters(result) == ["C", "C"]


def test_a_given_player_not_on_the_giving_roster_is_an_input_error(snap):
    with pytest.raises(TradeInputError) as error:
        grade(_trade(4, [MCCAFFREY], 12, [KINCAID]), snap)
    assert error.value.player_id == MCCAFFREY
    assert MCCAFFREY in str(error.value)


def test_a_roster_not_in_the_league_is_an_input_error(snap):
    with pytest.raises(TradeInputError):
        grade(_trade(4, [CROSKEY], 99, ["1"]), snap)


def test_a_proposed_trade_needs_two_rosters_players_on_each_side_and_an_asker_in_the_trade():
    with pytest.raises(ValueError):
        _trade(4, [CROSKEY], 4, [KINCAID])
    with pytest.raises(ValueError):
        _trade(4, [], 12, [KINCAID])
    with pytest.raises(ValueError):
        _trade(4, [CROSKEY], 12, [KINCAID], asker=7)


def test_the_breakdown_holds_no_trade_value_sum_ratio_or_chart_name(snap):
    for trade in (_trade(4, [COLLINS], 12, [KINCAID, WILSON]), _trade(4, [CROSKEY], 12, [KINCAID])):
        for side in grade(trade, snap):
            assert set(side.model_dump()) == {"roster_id", "start_letter", "reason", "adjusters"}
            # A digit in a reason could be a trade value or a lineup total, so no reason holds one.
            for reason in [side.reason, *(a.reason for a in side.adjusters)]:
                assert not re.search(r"\d", reason)
                # The trade value chart never shows. The NFL depth chart is a plain source, so its name may.
                assert not re.search(r"ratio|sum|peaked|(?<!depth )chart", reason, re.IGNORECASE)


# Points per game over weeks 2 to 5, the last four completed weeks of the week 6 snapshot.
# Roster 10, in the middle at 4-6: Saquon Barkley 3.83 on the bench, Monangai 12.47 and Judkins 10.32 at RB,
# Egbuka 8.50 and Ferguson 8.03 at flex.
# Roster 5, a contender: James Cook 19.10, Hubbard 17.27, and Javonte Williams 16.20 at RB and flex,
# Denzel Boston 12.03 at the last flex spot, Michael Wilson 10.37, Woody Marks 8.32, and Metcalf 8.03 on the bench.
SAQUON, COOK, HUBBARD, MARKS = "4866", "8138", "7594", "12474"


def _adjuster(breakdown, name: str):
    return next(a for a in breakdown.adjusters if a.name == name)


def test_fit_steps_up_for_a_lineup_gain_and_down_for_a_lineup_loss(snap):
    # Cook takes an RB spot on roster 10 and Judkins moves to flex for Ferguson, a gain of 11.07.
    # Roster 5 loses Cook, and Michael Wilson takes the last flex spot, a loss of 8.73.
    tenth, fifth = grade(_trade(10, [SAQUON], 5, [COOK]), snap)
    assert _adjuster(tenth, "roster fit").step == 1
    assert _adjuster(tenth, "roster fit").reason == "The best lineup gains after the trade."
    assert _adjuster(fifth, "roster fit").step == -1
    assert _adjuster(fifth, "roster fit").reason == "The best lineup loses after the trade."


# Roster 12: Tony Pollard 8.95 sits on the bench, behind Hampton 9.70 at the last flex spot.
POLLARD = "5967"


def test_fit_steps_up_for_the_highest_value_player_in_the_trade_with_no_lineup_loss(snap):
    # Saquon Barkley sits on roster 12's bench after the trade, so its lineup does not change.
    # Pollard takes the last flex spot on roster 10, a gain of 0.93, which is less than the fit threshold.
    snap = _with_values(snap, {SAQUON: 30.0})
    tenth, twelfth = grade(_trade(10, [SAQUON], 12, [POLLARD]), snap)
    assert _adjuster(twelfth, "roster fit").step == 1
    assert _adjuster(twelfth, "roster fit").reason == (
        "It gets the highest-value player in the trade, and the best lineup does not lose.")
    assert _adjuster(tenth, "roster fit").step == 0


def test_an_unlisted_player_makes_points_per_game_pick_the_highest_value_player_in_the_trade(snap):
    # Saquon Barkley has no trade value. Pollard has more points per game, so roster 10 gets the highest-value player.
    tenth, twelfth = grade(_trade(10, [SAQUON], 12, [POLLARD]), snap)
    assert _adjuster(tenth, "roster fit").step == 1
    assert _adjuster(twelfth, "roster fit").step == 0


def test_fit_holds_at_one_step_when_the_gain_is_large_and_the_side_gets_the_highest_value_player(snap):
    # Cook and Hubbard take both RB spots on roster 10, and Monangai and Judkins move to flex, a gain of 19.84.
    # Saquon Barkley has no trade value, so points per game make Cook the highest-value player in the trade.
    tenth, _ = grade(_trade(10, [SAQUON], 5, [COOK, HUBBARD]), snap)
    assert _adjuster(tenth, "roster fit").step == 1


def test_the_side_that_gets_the_depth_steps_up_only_when_every_player_it_gets_starts(snap):
    # Cook starts on roster 10, but Woody Marks at 8.32 sits on the bench, behind Egbuka at 8.50.
    tenth, _ = grade(_trade(10, [SAQUON], 5, [COOK, MARKS]), snap)
    assert _adjuster(tenth, "roster fit").step == 0
    assert _adjuster(tenth, "roster fit").reason == (
        "The best lineup gains after the trade, but not every player it gets starts.")


# Standings through week 5: rosters 3, 6, 5, 1, 2, and 9 hold the six playoff spots, and roster 9 in the sixth has 5 wins.
# Roster 4 has 1 win, four games out, so it is a seller.
# Rosters 7, 8, 10, 11, and 12 have 4 wins, one game out, so they are in the middle.
WICKS, JACOBS, SMITH_NJIGBA = "9486", "5850", "9488"


def test_a_team_in_the_middle_gets_no_standing_step(snap):
    tenth, _ = grade(_trade(10, [SAQUON], 5, [COOK]), snap)
    standing = _adjuster(tenth, "standing")
    assert standing.step == 0
    assert standing.reason == "The team is neither in a playoff spot nor out of the race."


def test_a_contender_steps_up_for_a_lineup_gain_now(snap):
    # Cook takes an RB spot on roster 3, and McCaffrey moves to flex for Dobbins.
    third, _ = grade(_trade(3, [WICKS], 5, [COOK]), snap)
    standing = _adjuster(third, "standing")
    assert standing.step == 1
    assert standing.reason == "The team holds a playoff spot, and the best lineup gains now."


def test_a_contender_steps_up_for_a_player_due_back_by_the_last_regular_season_week(snap):
    # Wicks sits on roster 3's bench and Jacobs has no games in the last four weeks, so the lineup holds.
    # The returns file has Jacobs back in week 7.
    third, _ = grade(_trade(3, [WICKS], 11, [JACOBS]), snap)
    standing = _adjuster(third, "standing")
    assert standing.step == 1
    assert standing.reason == "The team holds a playoff spot, and Josh Jacobs is due back before the playoffs."


def test_a_contender_steps_down_for_a_lineup_loss_now_for_a_player_with_no_return_week(snap):
    # Roster 3 loses McCaffrey at RB. Dobbins moves to RB, and Meyers at 7.17 takes the last flex spot, a loss of 10.45.
    # Saquon Barkley is Out and has no row in the returns file.
    third, _ = grade(_trade(3, [MCCAFFREY], 10, [SAQUON]), snap)
    standing = _adjuster(third, "standing")
    assert standing.step == -1
    assert standing.reason == (
        "The team holds a playoff spot, but the best lineup loses now for Saquon Barkley, "
        "who has no return week on file.")


def test_a_contender_steps_down_for_a_lineup_loss_now_for_a_player_due_back_after_the_playoffs_start(snap):
    snap = snap.model_copy(update={"returns": {SAQUON: 16}})
    third, _ = grade(_trade(3, [MCCAFFREY], 10, [SAQUON]), snap)
    standing = _adjuster(third, "standing")
    assert standing.step == -1
    assert "is not due back before the playoffs" in standing.reason


def test_a_seller_steps_up_when_it_gets_the_highest_value_player_in_the_trade(snap):
    # McCaffrey at 64.0 is worth more than Collins at 46.5.
    fourth, _ = grade(_trade(4, [COLLINS], 3, [MCCAFFREY]), snap)
    standing = _adjuster(fourth, "standing")
    assert standing.step == 1
    assert standing.reason == "The team is out of the playoff race, and it gets the highest-value player in the trade."


def test_a_seller_steps_down_when_it_gives_the_highest_value_player_for_a_lineup_gain_now(snap):
    # Smith-Njigba takes Collins's WR spot on roster 4, a gain of 6.99.
    # At 20.0 he is worth less than Collins at 46.5.
    snap = _with_values(snap, {SMITH_NJIGBA: 20.0})
    fourth, _ = grade(_trade(4, [COLLINS], 3, [SMITH_NJIGBA]), snap)
    standing = _adjuster(fourth, "standing")
    assert standing.step == -1
    assert standing.reason == (
        "The team is out of the playoff race, but it gives the highest-value player in the trade for a lineup gain now.")


def test_the_adjusters_show_in_rubric_order(snap):
    for side in grade(_trade(10, [SAQUON], 5, [COOK]), snap):
        assert [a.name for a in side.adjusters] == ["roster fit", "standing", "trend and usage", "injury", "handcuff"]


# The week 6 Josh Jacobs trade: roster 11 got Jacobs and Devaughn Vele from roster 12
# for Bhayshul Tuten and Garrett Wilson. Jacobs was suspended. The returns file has him back in week 7.
VELE, TUTEN = "11834", "12490"


def _before_the_jacobs_trade(snap):
    """The snapshot with rosters 11 and 12 set back to before the trade. The saved rosters show the league after it."""
    rosters = dict(snap.rosters)
    rosters[11] = [pid for pid in rosters[11] if pid not in (JACOBS, VELE)] + [TUTEN, WILSON]
    rosters[12] = [pid for pid in rosters[12] if pid not in (TUTEN, WILSON)] + [JACOBS, VELE]
    return snap.model_copy(update={"rosters": rosters})


def _as_contender(snap, roster_id: int):
    """The snapshot with the roster moved to the sixth playoff spot, at the record of the team it moves past.

    Each standing gets its rank, its playoff spot, and its games from the cut again, as the standings builder sets them.
    """
    ranked = sorted(snap.standings, key=lambda s: s.rank)
    team = next(s for s in ranked if s.roster_id == roster_id)
    sixth = ranked[5]
    others = [s for s in ranked if s.roster_id != roster_id]
    moved = team.model_copy(update={"wins": sixth.wins, "losses": sixth.losses, "points_for": sixth.points_for + 1})
    order = others[:5] + [moved] + others[5:]
    cut_wins = order[5].wins
    standings = [s.model_copy(update={"rank": i + 1, "in_playoffs": i < 6, "games_from_cut": s.wins - cut_wins})
                 for i, s in enumerate(order)]
    return snap.model_copy(update={"standings": standings})


def test_the_jacobs_trade_as_a_contender_bet_on_jacobs_back_in_week_7_gets_the_standing_step_up(snap):
    # Roster 11 is 4-6 and seventh through week 5, so this case moves it into the sixth playoff spot to test the bet.
    snap = _as_contender(_before_the_jacobs_trade(snap), 11)
    eleventh, _ = grade(_trade(11, [TUTEN, WILSON], 12, [JACOBS, VELE]), snap)
    standing = _adjuster(eleventh, "standing")
    assert standing.step == 1
    assert "Josh Jacobs is due back before the playoffs" in standing.reason


def test_the_jacobs_trade_never_steps_the_side_that_got_jacobs_down_for_standing(snap):
    # With the real standings through week 5, roster 11 is in the middle, one game out of the last spot.
    eleventh, _ = grade(_trade(11, [TUTEN, WILSON], 12, [JACOBS, VELE]), _before_the_jacobs_trade(snap))
    assert _adjuster(eleventh, "standing").step == 0


# The week 6 trade between rosters 6 and 7: roster 7 got Patrick Mahomes and Brian Robinson for Lamar Jackson.
MAHOMES, LAMAR = "4046", "4881"


def test_a_lineup_change_below_the_fit_threshold_is_no_loss_for_the_highest_value_player_step(
        fixture_raw_dir, fixture_history_root, chart_week6):
    # With stats through week 5, the lineup of roster 7 gains 8.48, so the gain alone earns the step.
    # This case grades the trade on the Tuesday after week 6, so points per game cover weeks 3 to 6.
    # Mahomes at 15.14 takes the QB spot from Lamar Jackson at 19.66, and Brian Robinson starts at flex.
    # The best lineup of roster 7 changes by about -0.60, which is less than the fit threshold.
    snap = build_snapshot(load_raw(fixture_raw_dir), fixture_history_root, chart_week6, trade_week=7)
    rosters = dict(snap.rosters)
    rosters[7] = [pid for pid in rosters[7] if pid not in (MAHOMES, B_ROBINSON)] + [LAMAR]
    rosters[6] = [pid for pid in rosters[6] if pid != LAMAR] + [MAHOMES, B_ROBINSON]
    snap = snap.model_copy(update={"rosters": rosters})
    _, seventh = grade(_trade(6, [MAHOMES, B_ROBINSON], 7, [LAMAR]), snap)
    fit = _adjuster(seventh, "roster fit")
    assert fit.step == 1
    assert fit.reason == "It gets the highest-value player in the trade, and the best lineup does not lose."


# Snap and target share directions through week 5, the last two weeks against the two before.
# Rome Odunze on roster 4 is up in both. Christian Watson on roster 1 is down in both.
# Rashee Rice on roster 1 is down in snap share and up in target share.
ODUNZE, WATSON, RICE = "11620", "8167", "10229"


def test_trend_steps_up_for_the_side_that_gets_the_rising_player_and_down_for_the_other(snap):
    first, fourth = grade(_trade(1, [WATSON], 4, [ODUNZE]), snap)
    assert _adjuster(first, "trend and usage").step == 1
    assert _adjuster(first, "trend and usage").reason == (
        "The players it gets gain snap or target share, and the players it gives lose it.")
    assert _adjuster(fourth, "trend and usage").step == -1
    assert _adjuster(fourth, "trend and usage").reason == (
        "The players it gets lose snap or target share, and the players it gives gain it.")


def test_trend_gives_no_step_when_the_shares_point_both_ways(snap):
    # Roster 4 gets Watson, who is down, and Rice, who is down in snap share and up in target share.
    _, fourth = grade(_trade(1, [WATSON, RICE], 4, [ODUNZE]), snap)
    assert _adjuster(fourth, "trend and usage").step == 0
    assert _adjuster(fourth, "trend and usage").reason == "The snap and target shares point both ways."


# Both shares are flat through week 5 for RJ Harvey on roster 1, with 3 red-zone touches,
# and for Alvin Kamara on roster 9, with 5.
HARVEY, KAMARA = "12489", "4035"


def test_red_zone_use_breaks_the_tie_when_every_share_is_flat(snap):
    first, ninth = grade(_trade(1, [HARVEY], 9, [KAMARA]), snap)
    assert _adjuster(first, "trend and usage").step == 1
    assert _adjuster(first, "trend and usage").reason == (
        "The snap and target shares are flat, and the players it gets have more red-zone use.")
    assert _adjuster(ninth, "trend and usage").step == -1


def test_injury_steps_down_for_a_player_out_now_with_no_near_return(snap):
    # Saquon Barkley is Out and has no row in the returns file. Wicks is Questionable, which is not out.
    third, tenth = grade(_trade(3, [WICKS], 10, [SAQUON]), snap)
    assert _adjuster(third, "injury").step == -1
    assert _adjuster(third, "injury").reason == "Saquon Barkley is out with no near return."
    assert _adjuster(tenth, "injury").step == 0


def test_injury_gives_no_step_for_a_player_due_back_within_the_return_window(snap):
    # The trade week is 6, so a return in week 7 is near.
    snap = snap.model_copy(update={"returns": {SAQUON: 7}})
    third, _ = grade(_trade(3, [WICKS], 10, [SAQUON]), snap)
    assert _adjuster(third, "injury").step == 0


@pytest.mark.parametrize("week, step", [(8, 0), (9, -1)])
def test_the_return_window_counts_from_the_trade_week(snap, week, step):
    # The trade week is 6 and stats run through week 5. A return in week 8 is near, and a return in week 9 is not.
    # Roster 7 is in the middle of the standings, so no return bet credit hides the injury step.
    snap = snap.model_copy(update={"returns": {SAQUON: week}})
    seventh, _ = grade(_trade(7, [B_ROBINSON], 10, [SAQUON]), snap)
    assert _adjuster(seventh, "injury").step == step


# Deebo Samuel on roster 10 is Out and has no row in the returns file, as Saquon Barkley.
DEEBO = "5872"


def test_injury_steps_down_once_when_two_players_it_gets_qualify(snap):
    third, _ = grade(_trade(3, [WICKS], 10, [SAQUON, DEEBO]), snap)
    assert _adjuster(third, "injury").step == -1


# Chris Olave on roster 2 is on the injury report in weeks 2 and 6, and in week 5 with no status.
# Jakobi Meyers on roster 3 is never on it.
OLAVE, OLAVE_GSIS, MEYERS = "8144", "00-0037239", "5947"


def _with_report_weeks(snap, gsis: str, weeks: list[int]):
    injuries = {**snap.injuries, gsis: {**snap.injuries[gsis], **{week: "Questionable" for week in weeks}}}
    return snap.model_copy(update={"injuries": injuries})


def test_injury_steps_down_at_the_count_of_report_weeks_and_never_counts_the_trade_week(slow_snap):
    # Weeks 2, 3, and 6 are three weeks, but week 6 is the trade week, so only two count.
    third, _ = grade(_trade(3, [MEYERS], 2, [OLAVE]), _with_report_weeks(slow_snap, OLAVE_GSIS, [3]))
    assert _adjuster(third, "injury").step == 0
    third, _ = grade(_trade(3, [MEYERS], 2, [OLAVE]), _with_report_weeks(slow_snap, OLAVE_GSIS, [3, 4]))
    assert _adjuster(third, "injury").step == -1
    assert _adjuster(third, "injury").reason == "Chris Olave was on the injury report in many weeks this season."


def test_injury_without_the_injury_report_says_no_count_ran(snap):
    third, _ = grade(_trade(3, [MEYERS], 2, [OLAVE]), snap)
    assert _adjuster(third, "injury").step == 0
    assert "The injury report is not available" in _adjuster(third, "injury").reason


def test_injury_never_fires_for_a_player_the_standing_adjuster_credits_as_a_return_bet(snap):
    # Jacobs is suspended and due back in week 10: past the return window, but before the playoffs.
    snap = _before_the_jacobs_trade(snap).model_copy(update={"returns": {JACOBS: 10}})
    trade = _trade(11, [TUTEN, WILSON], 12, [JACOBS, VELE])
    # In the middle of the standings, roster 11 gets no return bet credit, so the injury counts.
    eleventh, _ = grade(trade, snap)
    assert _adjuster(eleventh, "injury").step == -1
    assert _adjuster(eleventh, "injury").reason == "Josh Jacobs is out with no near return."
    # As a contender, the standing step credits Jacobs as a return bet, so the injury does not count.
    eleventh, _ = grade(trade, _as_contender(snap, 11))
    assert _adjuster(eleventh, "standing").step == 1
    assert _adjuster(eleventh, "injury").step == 0


# The LAC depth chart: Omarion Hampton on roster 12 first, then Keaton Mitchell and Kimani Vidal on roster 11.
# The id map fixture lacks them, so the tests join their gsis_ids here.
MITCHELL, HAMPTON, VIDAL = "9511", "12507", "11647"
LAC_IDS = {MITCHELL: "00-0038454", HAMPTON: "00-0040666", VIDAL: "00-0039391"}


def _with_ids(snap, ids: dict[str, str]):
    return snap.model_copy(update={"id_map": {**snap.id_map, **ids}})


def test_a_handcuff_with_a_chart_row_counts_as_zero_in_the_sums(slow_snap):
    # With Mitchell at 10.0 for Pollard at 9.0, roster 12 would start at B and roster 11 at C.
    snap = _with_values(_with_ids(slow_snap, LAC_IDS), {MITCHELL: 10.0})
    twelfth, eleventh = grade(_trade(12, [POLLARD], 11, [MITCHELL]), snap)
    assert _letters([twelfth, eleventh]) == ["F", "A"]
    handcuff = _adjuster(twelfth, "handcuff")
    assert handcuff.step == 0
    assert handcuff.reason == "Keaton Mitchell backs up the team's own starter, so he counts as insurance."
    # The id map fixture lacks Pollard, so the reason of roster 11 also names him.
    assert _adjuster(eleventh, "handcuff").reason.startswith("No player it gets is a handcuff.")


def test_a_handcuff_with_no_chart_row_keeps_the_start_letter(slow_snap):
    # Mitchell has no trade value. As a handcuff he counts as zero, so no side starts at C for him.
    twelfth, eleventh = grade(_trade(12, [POLLARD], 11, [MITCHELL]), _with_ids(slow_snap, LAC_IDS))
    assert _letters([twelfth, eleventh]) == ["F", "A"]
    assert "no trade value" not in twelfth.reason


def test_a_backup_whose_starter_is_on_another_roster_is_no_handcuff(slow_snap):
    # Roster 7 has no LAC starter, so Mitchell is unlisted there and both sides start at C.
    seventh, _ = grade(_trade(7, [B_ROBINSON], 11, [MITCHELL]), _with_ids(slow_snap, LAC_IDS))
    assert seventh.start_letter == "C"
    assert _adjuster(seventh, "handcuff").reason == "No player it gets is a handcuff."


# Amon-Ra St. Brown starts at WR for roster 12. Mitchell sits on its bench after the trade.
ST_BROWN = "7547"


def test_fit_never_steps_down_because_of_a_handcuff(slow_snap):
    twelfth, _ = grade(_trade(12, [ST_BROWN], 11, [MITCHELL]), _with_ids(slow_snap, LAC_IDS))
    fit = _adjuster(twelfth, "roster fit")
    assert fit.step == 0
    assert fit.reason == (
        "The best lineup loses after the trade, but Keaton Mitchell is a handcuff, so the loss does not count.")


# The NE depth chart: Rhamondre Stevenson on roster 7 first, then TreVeyon Henderson on roster 8.
# Henderson's snap share is down through week 5. The Carolina defense has no share direction and no red-zone use.
STEVENSON, HENDERSON, CAR_DEF = "7611", "12529", "CAR"
NE_IDS = {STEVENSON: "00-0036875", HENDERSON: "00-0040734"}


def test_trend_never_steps_down_because_of_a_handcuff(snap, slow_snap):
    trade = _trade(7, [CAR_DEF], 8, [HENDERSON])
    # With no depth chart, Henderson is no handcuff, and his falling share steps roster 7 down.
    seventh, _ = grade(trade, snap)
    assert _adjuster(seventh, "trend and usage").step == -1
    seventh, _ = grade(trade, _with_ids(slow_snap, NE_IDS))
    trend = _adjuster(seventh, "trend and usage")
    assert trend.step == 0
    assert trend.reason.endswith("TreVeyon Henderson is a handcuff, so his use does not count.")


def test_with_no_depth_chart_the_handcuff_check_does_not_run_and_the_breakdown_says_so(slow_snap):
    for snap, source in ((slow_snap.model_copy(update={"depth_charts": None}), "depth chart"),
                         (slow_snap.model_copy(update={"id_map": None}), "id map")):
        twelfth, _ = grade(_trade(12, [POLLARD], 11, [MITCHELL]), snap)
        assert _letters(grade(_trade(12, [POLLARD], 11, [MITCHELL]), snap)) == ["C", "C"]
        handcuff = _adjuster(twelfth, "handcuff")
        assert handcuff.step == 0
        assert handcuff.reason == f"The {source} is not available, so no handcuff check ran."


def test_a_player_not_in_the_id_map_gets_no_report_count_and_no_handcuff_check(slow_snap):
    # The id map fixture lacks Mitchell, so roster 12 gets a player with no gsis_id.
    twelfth, _ = grade(_trade(12, [POLLARD], 11, [MITCHELL]), slow_snap)
    injury, handcuff = _adjuster(twelfth, "injury"), _adjuster(twelfth, "handcuff")
    assert injury.step == 0
    assert injury.reason.endswith("Keaton Mitchell is not in the id map, so no report count ran for him.")
    assert handcuff.step == 0
    assert handcuff.reason.endswith("Keaton Mitchell is not in the id map, so no handcuff check ran for him.")


def test_trend_leaves_out_a_player_who_is_due_back(snap):
    # Jacobs is suspended through week 5 and due back in week 7, so he has no use to compare on either side.
    for side in grade(_trade(11, [TUTEN, WILSON], 12, [JACOBS, VELE]), _before_the_jacobs_trade(snap)):
        assert _adjuster(side, "trend and usage").reason.endswith("Josh Jacobs is due back, so his use does not count.")
