"""
Tests for the grade of a proposed trade: the start letter, each adjuster, the clamp, the final letter, and the verdict.
They feed a proposed trade and the week 6 snapshot at the grade seam.
"""
import re
import shutil
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from conftest import strip_trend_numbers, with_carries, with_free_agents

from cornerstone import rubric, tunables
from cornerstone.analysis import _allowed, _breakdown_text, _letter_failures, _prose_failures
from cornerstone.adjusters import (
    TREND, _byes_left, _return_bet, _wopr, best_lineup, due_back_week, lineup_value,
    rubric_adjusters,
)
from cornerstone.history import carry_share, points_per_game, red_zone, snap_share, target_share
from cornerstone.models import ExpectedGame, ExpectedPoints
from cornerstone.ranks import recent_points_per_game
from cornerstone.rubric import (
    Adjuster, Breakdown, ProposedTrade, TradeInputError, TradeSide, Verdict, fairness, grade, verdict,
)
from cornerstone.sleeper import load_raw
from cornerstone.slow_sources import SlowSources, load_slow_sources
from cornerstone.snapshot import build_snapshot, load_returns, load_snapshot
from cornerstone.trade_facts import trade_fact_sheet
from cornerstone.writer import load_prompt

# Week 6 trade values from the fixture: Collins 46.5 and Croskey-Merritt 24.0 on roster 4,
# McCaffrey 64.0 on roster 3, Kincaid 31.5 and Wilson 27.5 on roster 12,
# Harrison 36.0, Brian Robinson 22.0, and Bijan Robinson 20.5 on roster 7.
COLLINS, CROSKEY, MCCAFFREY = "7569", "12533", "4034"
KINCAID, WILSON = "10236", "8146"
HARRISON, B_ROBINSON, BIJAN = "11628", "8154", "9509"


@pytest.fixture
def snap(fixture_raw_dir, fixture_history_root, chart_week6):
    return load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)


def _known_games_snap(raw_dir, history_root, chart, edit=None, slow=None, now=None):
    """The week 6 snapshot of a game day in week 6, so the week 6 stat lines are the known games.

    `edit` changes the raw data first, as a test needs. `slow` and `now` give the kickoffs and the clock.
    """
    raw = load_raw(raw_dir)
    if edit is not None:
        edit(raw)
    return build_snapshot(raw, history_root, chart, slow, trade_week=6,
                          returns=load_returns(history_root.parent / "returns.json"), now=now)


@pytest.fixture
def known_snap(fixture_raw_dir, fixture_history_root, chart_week6):
    return _known_games_snap(fixture_raw_dir, fixture_history_root, chart_week6)


@pytest.fixture
def slow_snap(fixture_raw_dir, fixture_history_root, chart_week6, fixture_nflverse_dir, tmp_path):
    """The week 6 snapshot with the slow sources from the nflverse fixture: the depth chart, the id map,
    and the injuries."""
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    return load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6, slow)


def _trade(a: int, a_gives: list[str], b: int, b_gives: list[str], asker: int | None = None) -> ProposedTrade:
    return ProposedTrade(season=2026,
                         sides=(TradeSide(roster_id=a, gives=a_gives), TradeSide(roster_id=b, gives=b_gives)),
                         asker=a if asker is None else asker)


def _with_values(snap, values: dict[str, float]):
    chart = snap.chart.model_copy(update={"values": {**snap.chart.values, **values}})
    return snap.model_copy(update={"chart": chart})


def _with_status(snap, player: str, status: str | None):
    """The snapshot with the player's injury status set to `status`."""
    players = {**snap.players, player: snap.players[player].model_copy(update={"injury_status": status})}
    return snap.model_copy(update={"players": players})


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
    name = snap.players[MCCAFFREY].name
    assert str(error.value) == f"{name} is no longer on {snap.teams[4].name}."


def test_a_given_player_the_snapshot_does_not_know_is_named_by_id(snap):
    with pytest.raises(TradeInputError) as error:
        grade(_trade(4, ["999999"], 12, [KINCAID]), snap)
    assert error.value.player_id == "999999"
    assert str(error.value) == f"999999 is no longer on {snap.teams[4].name}."


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
    # Croskey-Merritt is on IR with no return week. The note for a player due back gives his projection, so this case
    # makes him healthy to keep every reason free of a digit.
    snap = _with_status(snap, CROSKEY, None)
    for trade in (_trade(4, [COLLINS], 12, [KINCAID, WILSON]), _trade(4, [CROSKEY], 12, [KINCAID])):
        for side in grade(trade, snap):
            assert set(side.model_dump()) == {"roster_id", "start_letter", "reason", "adjusters", "final_letter"}
            # A digit in a reason could be a trade value or a lineup total, so no reason holds one.
            # The trend reason may give share percents and the weeks behind them. Any other number in it fails.
            for reason in [side.reason, *(strip_trend_numbers(a.reason) if a.name == TREND else a.reason
                                          for a in side.adjusters)]:
                assert not re.search(r"\d", reason)
                # The trade value chart never shows. The NFL depth chart is a plain source, so its name may.
                assert not re.search(r"ratio|sum|peaked|(?<!depth )chart", reason, re.IGNORECASE)


# Lineup values in the week 6 snapshot: points per game over the last completed weeks, or the projection ahead from
# week 14 for a player out with no return week.
# Roster 10, in the middle at 4-6: Saquon Barkley 12.64 and Judkins 8.94 at RB, Monangai 8.44 and Deebo Samuel 8.32
# at flex, Ferguson 8.03 on the bench. All four are Out with no return week.
# Roster 5, a contender: James Cook 19.10, Hubbard 17.27, and Javonte Williams 16.20 at RB and flex,
# Denzel Boston 12.03 at the last flex spot, Michael Wilson 10.37, Woody Marks 8.32, and Metcalf 8.03 on the bench.
SAQUON, COOK, HUBBARD, MARKS = "4866", "8138", "7594", "12474"
# Saquon Barkley is Out with no return week, so he counts as back in week 14 at his fixture projection ahead.
SAQUON_NOTE = ("Saquon Barkley has no return week on file, so he counts as back in week 14 "
               "for his projection ahead of 12.6 a game.")
# The `snap` fixture has no schedule map, so no bye hole reads and each fit reason on it says so after the step.
NO_SCHEDULES = " The schedule sources are not available."


def _adjuster(breakdown, name: str):
    return next(a for a in breakdown.adjusters if a.name == name)


def test_fit_steps_up_for_a_lineup_gain_and_down_for_a_lineup_loss(snap):
    # Cook takes the RB spot of Saquon Barkley on roster 10, a gain of 6.46.
    # Roster 5 loses Cook, and Saquon Barkley takes his RB spot, a loss of 6.46.
    # Saquon Barkley is Out with no return week, so both sides name the projection he counts for.
    tenth, fifth = grade(_trade(10, [SAQUON], 5, [COOK]), snap)
    assert _adjuster(tenth, "roster fit").step == 1
    assert _adjuster(tenth, "roster fit").reason == (
        "The best lineup gains after the trade." + NO_SCHEDULES + " " + SAQUON_NOTE)
    assert _adjuster(fifth, "roster fit").step == -1
    # Saquon Barkley takes FLEX1 on roster 5. He counts as back in week 14, past the bye window, so his slot is a hole.
    assert _adjuster(fifth, "roster fit").reason == (
        "FLEX1 is a hole after the trade: Saquon Barkley is out with no return week on file." + NO_SCHEDULES + " "
        + SAQUON_NOTE)


# Roster 12: Tony Pollard 8.95 sits on the bench, behind Hampton 9.70. DJ Moore, Out with no return week, holds the
# last flex spot at 12.20.
POLLARD = "5967"


def _saquon_back_in_week_7(snap):
    """The snapshot with Saquon Barkley due back in week 7, inside the bye window.

    Out with no return week, he counts as back in week 14, and a slot he takes is a hole. The highest-value tests
    are about another rule, so they give him a return week. A bench back on roster 12 covers him.
    """
    return snap.model_copy(update={"returns": {**snap.returns, SAQUON: 7}})


def test_fit_steps_up_for_the_highest_value_player_in_the_trade_with_no_lineup_loss(snap):
    # Saquon Barkley is due back in week 7 at 12.7 a game. Roster 12's lineup does not lose with him.
    # Roster 10 loses his 12.7 for Pollard at 8.95, a loss of 3.75, past the fit threshold.
    snap = _with_values(_saquon_back_in_week_7(snap), {SAQUON: 30.0})
    tenth, twelfth = grade(_trade(10, [SAQUON], 12, [POLLARD]), snap)
    assert _adjuster(twelfth, "roster fit").step == 1
    assert _adjuster(twelfth, "roster fit").reason == (
        "It gets the highest-value player in the trade, and the best lineup does not lose." + NO_SCHEDULES
        + " Saquon Barkley is due back in week 7, so he counts for his projection ahead of 12.7 a game.")
    assert _adjuster(tenth, "roster fit").step == -1


def test_an_unlisted_player_makes_points_per_game_pick_the_highest_value_player_in_the_trade(snap):
    # Saquon Barkley has no trade value. He counts for 12.7 a game, more than Pollard at 8.95, so roster 12 gets the
    # highest-value player. Roster 10 loses his 12.7 in its lineup.
    tenth, twelfth = grade(_trade(10, [SAQUON], 12, [POLLARD]), _saquon_back_in_week_7(snap))
    assert _adjuster(tenth, "roster fit").step == -1
    assert _adjuster(twelfth, "roster fit").step == 1


def test_fit_holds_at_one_step_when_the_gain_is_large_and_the_side_gets_the_highest_value_player(snap):
    # Cook and Hubbard take both RB spots on roster 10, Judkins and Monangai move to flex, and Deebo Samuel moves to
    # the bench, a gain of 15.41.
    # Saquon Barkley has no trade value, so points per game make Cook the highest-value player in the trade.
    tenth, _ = grade(_trade(10, [SAQUON], 5, [COOK, HUBBARD]), snap)
    assert _adjuster(tenth, "roster fit").step == 1


def test_the_side_that_gets_the_depth_steps_up_only_when_every_player_it_gets_starts(snap):
    # Cook starts on roster 10, but Woody Marks at 8.32 sits on the bench, behind Egbuka at 8.50.
    # Roster 10 holds players out with no return week, and their projections ahead would change its lineup.
    # With no projections file, every player keeps his recent points. Saquon Barkley is healthy here, so no note shows.
    # Judkins is healthy here too. Out with no return week, he would take a flex spot as a hole, and this test is
    # about the one-for-two rule.
    snap = _with_status(_with_status(_with_projections(snap, None), SAQUON, None), JUDKINS, None)
    tenth, _ = grade(_trade(10, [SAQUON], 5, [COOK, MARKS]), snap)
    assert _adjuster(tenth, "roster fit").step == 0
    assert _adjuster(tenth, "roster fit").reason == (
        "The best lineup gains after the trade, but not every player it gets starts." + NO_SCHEDULES)


# Position ranks by lineup value on the week 6 fixture. The line is RB36 and WR36, QB24 and TE24.
# Roster 2 starts Aaron Jones RB13 and Ashton Jeanty RB21, with Zach Charbonnet RB27 at flex.
# Its bench backs are Kendre Miller RB55 at 4.27 and Jeremiyah Love RB75 at 0.
# Roster 12 starts Amon-Ra St. Brown WR11 and Garrett Wilson WR12, each at 15.00.
JONES, JEANTY, CHARBONNET, MILLER = "4199", "12527", "9753", "9757"


def test_a_side_that_gives_two_backs_for_two_receivers_and_opens_an_rb2_hole_steps_down(snap):
    # Roster 2 after: Charbonnet moves up to RB1 and Miller at RB55 takes RB2. St. Brown and Wilson take both flex
    # spots, so the best lineup changes by 0.35, about the same. The new holes alone step it down.
    # Charbonnet is Out with no return week, so he counts as back in week 14 and RB1 is a hole too. His flex slot
    # was a hole before, and that FLEX hole closes.
    second, _ = grade(_trade(2, [JONES, JEANTY], 12, [ST_BROWN, WILSON]), snap)
    fit = _adjuster(second, "roster fit")
    assert fit.step == -1
    assert fit.reason == ("RB1 is a hole after the trade: Zach Charbonnet is out with no return week on file. "
                          "RB2 is a hole after the trade: Kendre Miller is RB55." + NO_SCHEDULES)


def _prompt_section(heading: str) -> str:
    """One section of the rubric prompt, from its heading to the next, with the line breaks joined."""
    text = load_prompt("rubric.md")
    section = text.split(f"## {heading}\n", 1)[1].split("\n## ", 1)[0]
    return " ".join(section.split())


# The words GLOSSARY.md bans for the line and a hole.
FIT_BANNED = re.compile(r"\b(replacements?|tiers?|floors?|gaps?)\b", re.IGNORECASE)


def test_the_rubric_prompt_states_the_step_rule_and_the_narrowed_handcuff_block():
    fit, handcuff = _prompt_section("Roster fit"), _prompt_section("Handcuff")
    assert "`LINE_RB_WR` at RB and WR, and `LINE_QB_TE` at QB and TE" in fit
    assert "A hole is a starting slot that holds a player below the line, or holds no player." in fit
    assert "A new hole with no lineup gain is one step down." in fit
    assert "A gain that opens a new hole is no step, because the two cancel." in fit
    assert "A new hole blocks this step too, and the step is none." in fit
    assert "The block covers a lineup loss only. A new hole still steps down." in handcuff
    assert "broad" not in handcuff
    assert tunables.LINE_RB_WR == 36 and tunables.LINE_QB_TE == 24


def test_the_rubric_prompt_states_the_no_cover_hole():
    fit = _prompt_section("Roster fit")
    assert "A starter who misses a week with no cover is a hole too." in fit
    assert "The bye window is `BYE_WINDOW` weeks from the trade week." in fit
    assert "A starter due back after the window is a hole, whatever his rank." in fit
    assert "it names the week of his bye or his return." in fit
    assert tunables.BYE_WINDOW == 3


def test_the_rubric_prompt_states_that_depth_and_strength_are_facts_and_never_move_the_step():
    fit = _prompt_section("Roster fit")
    assert "Strength is how many of the side's RB1, RB2, WR1, and WR2 starters hold a position rank of " \
           "`STRENGTH_RANK` or better." in fit
    assert "Depth and strength are facts for the analysis. They never move the step." in fit


def test_no_roster_fit_reason_or_prompt_section_uses_replacement_tier_floor_or_gap(snap):
    assert not FIT_BANNED.search(_prompt_section("Roster fit"))
    assert not FIT_BANNED.search(_prompt_section("Handcuff"))
    trades = [_trade(2, [JONES, JEANTY], 12, [ST_BROWN, WILSON]), _trade(1, [ADAMS], 2, [ADDISON]),
              _trade(2, [JONES, JEANTY, CHARBONNET, LOVE, MILLER], 12, ["6801"]), _trade(10, [SAQUON], 5, [COOK])]
    for trade in trades:
        for breakdown in grade(trade, snap):
            assert not FIT_BANNED.search(_adjuster(breakdown, "roster fit").reason)


# Jordan Addison sits on the bench of roster 2 at WR53. He is Out with no return week, so a note names him.
ADDISON = "9756"


def test_a_side_that_gets_a_back_who_fills_a_hole_at_rb2_and_gains_in_the_lineup_steps_up(snap):
    # With Jones and Jeanty off roster 2, Charbonnet RB27 is RB1 and Miller RB55 holds RB2, a hole.
    # Hampton RB26 at 9.70 takes RB1 and Charbonnet moves to RB2, a gain of 5.43. Addison was on the bench.
    rosters = {**snap.rosters, 2: [pid for pid in snap.rosters[2] if pid not in (JONES, JEANTY)]}
    second, _ = grade(_trade(2, [ADDISON], 12, [HAMPTON]), snap.model_copy(update={"rosters": rosters}))
    fit = _adjuster(second, "roster fit")
    assert fit.step == 1
    assert fit.reason.startswith("The best lineup gains after the trade.")
    assert "hole" not in fit.reason


# Roster 10 starts Emeka Egbuka WR37 at WR2, a hole, and Deebo Samuel WR41 at FLEX2. Keenan Allen sits on its bench.
KEENAN_ALLEN = "1479"


def test_a_side_with_the_same_hole_before_and_after_gets_no_step_for_it(snap):
    # Tuten RB15 takes RB2, Judkins and Monangai take the flex spots, and Deebo Samuel sits, a gain of 4.16.
    # Egbuka holds WR2 before and after, so his hole is not new and the gain steps up.
    tenth, _ = grade(_trade(10, [KEENAN_ALLEN], 12, [TUTEN]), snap)
    fit = _adjuster(tenth, "roster fit")
    assert fit.step == 1
    assert fit.reason == "The best lineup gains after the trade." + NO_SCHEDULES


def test_a_side_that_gets_the_highest_value_player_and_opens_a_new_hole_gets_no_step_up(snap):
    # St. Brown at 90.0 is the highest-value player, and roster 2 gets him. Its RB2 slot opens a hole at Miller RB55.
    # Jones and Jeanty get chart rows, so trade value picks St. Brown. The hole blocks the step up, and the two
    # cancel to no step.
    snap = _with_values(snap, {ST_BROWN: 90.0, JONES: 10.0, JEANTY: 10.0})
    second, _ = grade(_trade(2, [JONES, JEANTY], 12, [ST_BROWN, WILSON]), snap)
    fit = _adjuster(second, "roster fit")
    assert fit.step == 0
    assert fit.reason == ("It gets the highest-value player in the trade, and the best lineup does not lose. "
                          "RB1 is a hole after the trade: Zach Charbonnet is out with no return week on file. "
                          "RB2 is a hole after the trade: Kendre Miller is RB55." + NO_SCHEDULES)


def test_a_lineup_gain_that_opens_a_new_hole_gets_no_step_and_names_both(slow_snap):
    # Hand-worked trade 3: roster 4 gives McConkey and Stevenson for Skattebo and Collins, a gain of 4.75.
    # Stevenson RB23 held FLEX2, and Worthy WR45 takes it. The gain and the hole cancel.
    # McConkey is Out with no return week, so his FLEX1 slot is a hole before the trade, and Worthy's would not be
    # new. The test is about a new hole, so McConkey is back in week 6 here.
    snap = _before_real_trade(slow_snap, 3)
    snap = snap.model_copy(update={"returns": {**snap.returns, "11635": 6}})
    fourth, _ = grade(_trade(4, ["11635", "7611"], 7, ["12481", COLLINS], asker=7), snap)
    fit = _adjuster(fourth, "roster fit")
    assert fit.step == 0
    assert fit.reason.startswith(
        "The best lineup gains after the trade. FLEX2 is a hole after the trade: Xavier Worthy is WR45.")


def test_a_side_that_gives_its_starter_for_his_handcuff_and_opens_a_hole_steps_down(slow_snap):
    # Roster 12 gives Tuten, Emanuel Wilson, and Pollard for Mitchell, who backs up Hampton at LAC.
    # Hampton RB26 moves up to RB1 and Mitchell RB39 takes RB2. The handcuff blocks the loss, never the hole.
    # Hampton and Mitchell of LAC share the bye in week 7, so Mitchell cannot cover Hampton. Hampton covered the bye
    # of Tee Higgins in week 6 from the bench before, and now he starts, so two bye holes open too.
    twelfth, _ = grade(_trade(12, [TUTEN, E_WILSON, POLLARD], 11, [MITCHELL]), _lac_snap(slow_snap))
    assert _adjuster(twelfth, "handcuff").reason == (
        "Keaton Mitchell backs up the team's own starter, so he counts as insurance.")
    fit = _adjuster(twelfth, "roster fit")
    assert fit.step == -1
    assert fit.reason == ("RB1 is a hole after the trade: Omarion Hampton has his bye in week 7, and no bench player "
                          "covers him. RB2 is a hole after the trade: Keaton Mitchell is RB39. "
                          "FLEX1 is a hole after the trade: Tee Higgins has his bye in week 6, and no bench player "
                          "covers him.")


# Roster 1 starts Davante Adams WR20 at FLEX2, with Jordyn Tyson WR44 at 7.76 next on its bench.
# Roster 6 starts Pat Freiermuth TE10 at FLEX2, with Malik Washington WR38 and Blake Corum RB42 on its bench.
# Hunter Henry sits on the bench of roster 4 at TE20.
E_WILSON, ADAMS, FREIERMUTH, CORUM, HUNTER_HENRY = "11435", "2133", "7600", "11586", "3214"
RICE, JUDKINS = "10229", "12512"


def test_a_flex_slot_with_a_wr_below_36_is_a_hole(snap):
    # Tyson takes FLEX2, a loss of 3.98. With a loss and a new hole, the step is one down and the reason names the hole.
    # Adams and Rashee Rice are back in week 6 here. Out with no return week, each holds a flex slot as a hole before
    # the trade, so the hole at Tyson would not be new.
    snap = snap.model_copy(update={"returns": {**snap.returns, ADAMS: 6, RICE: 6}})
    first, _ = grade(_trade(1, [ADAMS], 2, [ADDISON]), snap)
    fit = _adjuster(first, "roster fit")
    assert fit.step == -1
    assert fit.reason.startswith("FLEX2 is a hole after the trade: Jordyn Tyson is WR44.")
    assert "The best lineup loses" not in fit.reason


def test_a_flex_slot_with_a_te_at_20_is_not_a_hole(snap):
    # Henry takes FLEX2 at 6.78, a change of -2.65, about the same. TE20 is above the line at TE, so he is no hole.
    sixth, _ = grade(_trade(6, [FREIERMUTH, M_WASHINGTON, CORUM], 4, [HUNTER_HENRY]), snap)
    fit = _adjuster(sixth, "roster fit")
    assert fit.step == 0
    assert fit.reason == "The best lineup stays about the same." + NO_SCHEDULES


def test_a_def_slot_never_makes_a_hole(snap):
    # Roster 1 gives its only defense, so the DEF slot is empty, a loss of 5.36. The loss steps down, not a hole.
    # Roster 2 has no defense before or after, and its DEF slot makes no hole either.
    first, second = grade(_trade(1, ["TB"], 2, [ADDISON]), snap)
    assert _adjuster(first, "roster fit").step == -1
    assert _adjuster(first, "roster fit").reason.startswith("The best lineup loses after the trade.")
    assert "hole" not in _adjuster(second, "roster fit").reason


def test_a_starting_slot_with_no_player_is_a_hole_and_each_new_hole_is_named(snap):
    # Roster 2 gives all five of its backs, so no player can fill RB1 or RB2.
    second, _ = grade(_trade(2, [JONES, JEANTY, CHARBONNET, LOVE, MILLER], 12, ["6801"]), snap)
    fit = _adjuster(second, "roster fit")
    assert fit.step == -1
    assert fit.reason.startswith("RB1 is a hole after the trade: no player fills it. "
                                 "RB2 is a hole after the trade: no player fills it.")


# Bye weeks from the nflverse fixture. The trade week is 6, so the bye window is weeks 6 to 8.
# Roster 5 has no hole before a trade. Each of its starters with a bye in the window has a bench cover: Stafford QB6
# covers Daniels, Woody Marks RB34 covers Cook, and Gesicki TE17 covers Kittle. Michael Wilson WR25, bye week 14,
# sits on its bench free to cover a receiver.
# Roster 6 starts Parker Washington WR18 of JAX, bye week 7, and roster 5 starts Denzel Boston WR23 of CLE, bye week 11.
P_WASHINGTON, BOSTON, MICHAEL_WILSON, DEVONTA_SMITH = "9487", "13346", "10232", "7525"


def _without(snap, roster_id: int, player: str):
    return snap.model_copy(update={"rosters": {**snap.rosters, roster_id: [
        pid for pid in snap.rosters[roster_id] if pid != player]}})


def _with_bye(snap, team: str, week: int):
    schedules = {**snap.schedules, team: snap.schedules[team].model_copy(update={"bye_week": week})}
    return snap.model_copy(update={"schedules": schedules})


def _washington_for_boston(snap):
    # Boston gets the higher trade value, so roster 5 does not get the highest-value player and a new hole steps down.
    fifth, _ = grade(_trade(5, [BOSTON], 6, [P_WASHINGTON]), _with_values(snap, {BOSTON: 30.0, P_WASHINGTON: 20.0}))
    return _adjuster(fifth, "roster fit")


def test_a_starter_with_his_bye_in_week_n_plus_1_and_a_bench_cover_above_the_line_is_no_hole(slow_snap):
    # Parker Washington takes a flex spot on roster 5, and Michael Wilson WR25 covers his bye in week 7.
    fit = _washington_for_boston(slow_snap)
    assert "hole" not in fit.reason


def test_a_starter_with_his_bye_in_week_n_plus_1_and_no_bench_cover_is_a_hole_that_names_the_week(slow_snap):
    # With Michael Wilson gone, no bench receiver above the line covers Parker Washington in week 7.
    fit = _washington_for_boston(_without(slow_snap, 5, MICHAEL_WILSON))
    assert fit.step == -1
    assert fit.reason == ("FLEX2 is a hole after the trade: Parker Washington has his bye in week 7, and no bench "
                          "player covers him.")


def test_a_starter_with_his_bye_in_week_n_plus_3_is_no_hole(slow_snap):
    # JAX moves its bye to week 9, past the window, so Parker Washington needs no cover.
    fit = _washington_for_boston(_with_bye(_without(slow_snap, 5, MICHAEL_WILSON), "JAX", 9))
    assert "hole" not in fit.reason


def test_two_starters_with_byes_in_the_window_and_one_bench_cover_give_one_hole(slow_snap):
    # PHI moves its bye to week 7, so DeVonta Smith at WR1 and Parker Washington both miss week 7.
    # Michael Wilson covers one slot only. WR1 fills first, so he covers Smith, and Washington's slot is the hole.
    fit = _washington_for_boston(_with_bye(slow_snap, "PHI", 7))
    assert fit.step == -1
    assert fit.reason == ("FLEX2 is a hole after the trade: Parker Washington has his bye in week 7, and no bench "
                          "player covers him.")


def test_a_starter_due_back_in_week_n_plus_2_reads_as_a_bye_and_needs_cover(slow_snap):
    # The returns file has Parker Washington back in week 8. JAX moves its bye to week 9, so only his return reads.
    snap = _with_bye(_without(slow_snap, 5, MICHAEL_WILSON), "JAX", 9)
    fit = _washington_for_boston(snap.model_copy(update={"returns": {**snap.returns, P_WASHINGTON: 8}}))
    assert fit.reason.startswith(
        "FLEX2 is a hole after the trade: Parker Washington is due back in week 8, and no bench player covers him.")
    covered = _washington_for_boston(_with_bye(slow_snap, "JAX", 9).model_copy(
        update={"returns": {**slow_snap.returns, P_WASHINGTON: 8}}))
    assert "hole" not in covered.reason


def test_a_starter_due_back_in_week_n_plus_6_is_a_hole(slow_snap):
    # Back in week 12 is past the window, so his slot is a hole even with Michael Wilson on the bench to cover.
    snap = slow_snap.model_copy(update={"returns": {**slow_snap.returns, P_WASHINGTON: 12}})
    fit = _washington_for_boston(snap)
    assert fit.reason.startswith("FLEX2 is a hole after the trade: Parker Washington is due back in week 12.")


# Roster 12 starts Bhayshul Tuten RB15 of JAX, bye week 7. Its bench backs are Omarion Hampton RB26 of LAC, bye week 7
# too, Tony Pollard RB30 of TEN, bye week 9, and Tyjae Spears RB61. Pollard is the only back who can cover Tuten.
# Josh Downs WR46 sits on the bench of roster 11.
DOWNS = "9500"


def test_a_trade_that_gives_away_the_only_bench_cover_for_a_bye_opens_a_new_hole_and_steps_down(slow_snap):
    # The best lineup of roster 12 does not change, so the new hole alone steps it down.
    twelfth, _ = grade(_trade(12, [POLLARD], 11, [DOWNS]), slow_snap)
    fit = _adjuster(twelfth, "roster fit")
    assert fit.step == -1
    assert fit.reason == ("RB1 is a hole after the trade: Bhayshul Tuten has his bye in week 7, and no bench player "
                          "covers him.")


def test_with_no_schedule_map_no_bye_hole_reads_and_the_reason_names_the_missing_schedules(slow_snap):
    twelfth, _ = grade(_trade(12, [POLLARD], 11, [DOWNS]), slow_snap.model_copy(update={"schedules": None}))
    fit = _adjuster(twelfth, "roster fit")
    assert fit.step == 0
    assert fit.reason == "The best lineup stays about the same. The schedule sources are not available."


# Roster 2 starts Ja'Marr Chase WR8 at WR1, Chris Olave WR14 at WR2, and Tre Tucker WR31 at FLEX1. Its DEF slot is
# empty. St. Brown WR11 and Garrett Wilson WR12 score 15.00 each, so St. Brown takes WR2 by the player ID tie rule.
def test_the_fact_sheet_names_the_slot_each_player_takes_and_the_player_he_pushes_out(snap):
    sheet = trade_fact_sheet(_trade(2, [JONES, JEANTY], 12, [ST_BROWN, WILSON]), snap)
    assert sheet[f"{ST_BROWN}.slot"].text == "Amon-Ra St. Brown takes WR2, and Chris Olave moves to FLEX2."
    assert sheet[f"{WILSON}.slot"].text == "Garrett Wilson takes FLEX1 and pushes Tre Tucker to the bench."
    # The slot names carry digits, so the checker accepts "WR2" and "FLEX1" in the prose.
    assert set(sheet[f"{ST_BROWN}.slot"].numbers) >= {"2"}
    assert set(sheet[f"{WILSON}.slot"].numbers) >= {"1"}


def test_the_slot_fact_names_the_player_who_held_the_slot_and_leaves_in_the_trade(snap):
    # Hampton RB26 at 9.70 takes RB2 on roster 2 over Charbonnet at 9.58. Jeanty held RB2 and goes to roster 12.
    sheet = trade_fact_sheet(_trade(2, [JEANTY], 12, [HAMPTON]), snap)
    assert sheet[f"{HAMPTON}.slot"].text == "Omarion Hampton takes RB2, which Ashton Jeanty held before the trade."


def test_a_player_the_side_gets_who_starts_in_no_slot_sits_on_the_bench(snap):
    # Jeanty at 10.98 is behind Tee Higgins at 13.60 and DJ Moore at 12.20 for the flex spots of roster 12.
    sheet = trade_fact_sheet(_trade(2, [JEANTY], 12, [HAMPTON]), snap)
    assert sheet[f"{JEANTY}.slot"].text == "Ashton Jeanty sits on the bench."


def test_a_player_who_takes_an_empty_slot_says_the_slot_was_empty(snap):
    sheet = trade_fact_sheet(_trade(2, [LOVE], 12, ["NE"]), snap)
    assert sheet["NE.slot"].text == "New England Patriots takes DEF, which was empty before the trade."


# Roster 2 holds Jones RB13, Jeanty RB21, and Charbonnet RB27 above the line at RB, with Miller RB55 and Love RB75
# below it. At WR it holds Chase WR8, Olave WR14, Tucker WR31, and Wan'Dale Robinson WR36, with Addison WR53 below.
# Roster 12 holds Tuten RB15, Emanuel Wilson RB17, Hampton RB26, and Pollard RB30 above the line at RB, and
# Higgins WR15, DJ Moore WR22, and Luther Burden WR32 at WR beside St. Brown and Wilson.
def test_a_trade_that_drops_a_sides_rb_depth_from_three_to_one_gives_a_depth_fact_with_both_counts(snap):
    sheet = trade_fact_sheet(_trade(2, [JONES, JEANTY], 12, [ST_BROWN, WILSON]), snap)
    assert sheet["2.depth.rb"].text == "For All You Need Is Love, RB depth above the line goes from 3 to 1."
    assert sheet["2.depth.rb"].numbers == ["3", "1"]
    assert sheet["2.depth.wr"].text == "For All You Need Is Love, WR depth above the line goes from 4 to 6."
    assert sheet["12.depth.rb"].text == "For Amon-Ra Dawg Your Team, RB depth above the line goes from 4 to 6."
    assert sheet["12.depth.wr"].text == "For Amon-Ra Dawg Your Team, WR depth above the line goes from 5 to 3."


def test_a_position_whose_depth_count_does_not_change_gets_no_depth_fact(snap):
    # Hampton RB26 for Jeanty RB21 keeps 3 backs above the line on roster 2 and 4 on roster 12.
    sheet = trade_fact_sheet(_trade(2, [JEANTY], 12, [HAMPTON]), snap)
    assert not [fid for fid in sheet if ".depth." in fid]
    # QB and TE do not change in the trade of backs for receivers, so they get no depth fact either.
    sheet = trade_fact_sheet(_trade(2, [JONES, JEANTY], 12, [ST_BROWN, WILSON]), snap)
    assert sorted(fid for fid in sheet if ".depth." in fid) == [
        "12.depth.rb", "12.depth.wr", "2.depth.rb", "2.depth.wr"]


def test_a_trade_that_drops_the_top_24_starter_count_from_four_to_three_gives_a_strength_fact_with_both_counts(snap):
    # Roster 2 starts Jones RB13, Jeanty RB21, Chase WR8, and Olave WR14, all four in the top 24. Hampton RB26 takes
    # RB2 for Jeanty, so three are in the top 24 after. Roster 12 starts Tuten RB15 and Emanuel Wilson RB17 at RB
    # before and after, so its count of 4 does not change and it gets no strength fact.
    sheet = trade_fact_sheet(_trade(2, [JEANTY], 12, [HAMPTON]), snap)
    assert sheet["2.strength"].text == ("For All You Need Is Love, the starters at RB1, RB2, WR1, and WR2 with a "
                                        "position rank of 24 or better go from 4 to 3.")
    assert {"24", "4", "3"} <= set(sheet["2.strength"].numbers)
    assert "12.strength" not in sheet
    assert tunables.STRENGTH_RANK == 24


@pytest.fixture
def fa_snap(fixture_raw_dir, fixture_history_root, chart_week6):
    """The week 6 snapshot with the hand-set free agents of conftest. Bigsby RB51 is the best free agent at RB and
    Darren Waller TE9 the best at TE. No free agent at QB or WR has a position rank."""
    return build_snapshot(with_free_agents(load_raw(fixture_raw_dir)), fixture_history_root, chart_week6,
                          returns=load_returns(fixture_history_root.parent / "returns.json"))


def test_the_hole_fact_names_the_cause_and_the_best_free_agent_at_rb_with_his_rank(fa_snap):
    # Roster 2 gives Jones and Jeanty, so Miller RB55 takes RB2 and Charbonnet, due back in week 14, takes RB1.
    sheet = trade_fact_sheet(_trade(2, [JONES, JEANTY], 12, [ST_BROWN, WILSON]), fa_snap)
    assert sheet["2.hole.rb2"].text == ("For All You Need Is Love, RB2 is a hole after the trade: Kendre Miller is "
                                        "RB55. The best free agent at RB is Tank Bigsby, RB51.")
    assert sheet["2.hole.rb1"].text == ("For All You Need Is Love, RB1 is a hole after the trade: Zach Charbonnet is "
                                        "out with no return week on file. The best free agent at RB is Tank Bigsby, "
                                        "RB51.")
    # The rank goes through Nums, so the analysis checker accepts "RB51" in the prose.
    assert {"2", "55", "51"} <= set(sheet["2.hole.rb2"].numbers)
    assert sheet["2.hole.rb2"].players == ["Kendre Miller", "Tank Bigsby"]
    # Roster 12 gives St. Brown and Wilson, so DJ Moore, out with no return week on file, takes WR2.
    # No free agent at WR has a rank.
    assert sheet["12.hole.wr2"].text == ("For Amon-Ra Dawg Your Team, WR2 is a hole after the trade: DJ Moore is out "
                                         "with no return week on file. No free agent at WR has a position rank.")


def test_a_hole_with_no_free_agent_with_a_rank_gets_a_fact_that_says_so(snap):
    # The week 6 players file holds no free agent.
    sheet = trade_fact_sheet(_trade(2, [JONES, JEANTY], 12, [ST_BROWN, WILSON]), snap)
    assert sheet["2.hole.rb2"].text == ("For All You Need Is Love, RB2 is a hole after the trade: Kendre Miller is "
                                        "RB55. No free agent at RB has a position rank.")


def test_a_flex_hole_reads_the_position_of_the_player_who_holds_it(fa_snap):
    # Tyson WR44 takes FLEX2, as in the flex hole test of the step. The free agents at RB and TE do not count for him.
    snap = fa_snap.model_copy(update={"returns": {**fa_snap.returns, ADAMS: 6, RICE: 6}})
    sheet = trade_fact_sheet(_trade(1, [ADAMS], 2, [ADDISON]), snap)
    assert sheet["1.hole.flex2"].text == ("For Brock ‘N’ Roll, FLEX2 is a hole after the trade: Jordyn Tyson is WR44. "
                                          "No free agent at WR has a position rank.")


def test_an_empty_flex_hole_reads_the_best_free_agent_at_every_position_the_slot_allows(fa_snap):
    # Roster 2 keeps only Burrow, Chase, Olave, and Strange and gets a defense, so no player fills FLEX1.
    # FLEX2 held Charbonnet, due back in week 14, so it was a hole before and only FLEX1 is new.
    # Waller TE9 ranks better than Bigsby RB51.
    gives = [JONES, JEANTY, CHARBONNET, LOVE, MILLER, "10213", "8126", ADDISON, "12517"]
    sheet = trade_fact_sheet(_trade(2, gives, 12, ["NE"]), fa_snap)
    assert sheet["2.hole.flex1"].text == ("For All You Need Is Love, FLEX1 is a hole after the trade: no player fills "
                                          "it. The best free agent at RB, WR, or TE is Darren Waller, TE9.")
    assert "2.hole.flex2" not in sheet


def test_the_hole_fact_never_says_replacement_floor_or_tier(fa_snap):
    sheet = trade_fact_sheet(_trade(2, [JONES, JEANTY], 12, [ST_BROWN, WILSON]), fa_snap)
    holes = [f.text for fid, f in sheet.items() if ".hole." in fid]
    assert holes and not any(FIT_BANNED.search(text) for text in holes)


# Standings through week 5: rosters 3, 6, 5, 1, 2, and 9 hold the six playoff spots,
# and roster 9 in the sixth has 5 wins.
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
    # His projection ahead would start him on roster 3, so this case drops the projections to reach the return bet.
    third, _ = grade(_trade(3, [WICKS], 11, [JACOBS]), snap.model_copy(update={"projections_ahead": None}))
    standing = _adjuster(third, "standing")
    assert standing.step == 1
    assert standing.reason == "The team holds a playoff spot, and Josh Jacobs is due back before the playoffs."


def _with_bounds(snap, **bounds):
    return snap.model_copy(update={"as_of": snap.as_of.model_copy(update=bounds)})


def test_the_return_bet_reads_the_completed_week_bound_and_not_the_player_stat_bound(snap):
    # The returns file has Jacobs back in week 7. A player stat bound of 7 alone must not put his return behind us.
    snap = _with_bounds(snap.model_copy(update={"projections_ahead": None}), stats_through=7)
    third, _ = grade(_trade(3, [WICKS], 11, [JACOBS]), snap)
    standing = _adjuster(third, "standing")
    assert standing.step == 1
    assert standing.reason == "The team holds a playoff spot, and Josh Jacobs is due back before the playoffs."


def test_the_lineup_value_of_a_player_due_back_reads_the_completed_week_bound_and_not_the_player_stat_bound(snap):
    # The returns file has Jacobs back in week 7. A player stat bound of 7 alone must not put his return behind us,
    # so he still counts for his projection ahead from week 7.
    snap = _with_bounds(snap.model_copy(update={"projections_ahead": {JACOBS: {7: 18.0}}}), stats_through=7)
    assert due_back_week(snap, JACOBS) == 7
    assert lineup_value(snap, JACOBS) == 18
    third, _ = grade(_trade(3, [WICKS], 11, [JACOBS]), snap)
    assert _adjuster(third, "roster fit").reason.endswith(
        "Josh Jacobs is due back in week 7, so he counts for his projection ahead of 18.0 a game.")


def test_the_return_bet_of_a_known_games_week_reads_the_completed_week_bound(known_snap):
    # The player stat bound is 6 and the completed week bound is 5. A return in week 6 is still ahead.
    snap = known_snap.model_copy(update={"projections_ahead": None, "returns": {JACOBS: 6}})
    assert (snap.as_of.stats_through, snap.as_of.completed_through) == (6, 5)
    third, _ = grade(_trade(3, [WICKS], 11, [JACOBS]), snap)
    standing = _adjuster(third, "standing")
    assert standing.step == 1
    assert standing.reason == "The team holds a playoff spot, and Josh Jacobs is due back before the playoffs."


def _with_known_game(snap, player: str, **fields):
    """The snapshot with `fields` set on the player's stat line of the known-games week.

    The roster points come first in the points reader, so a points field sets his roster points too.
    """
    week_n = snap.stats.weeks[snap.as_of.stats_through]
    stats = {**week_n.stats, player: {**(week_n.stats.get(player) or {}), **fields}}
    points = {**week_n.points, player: fields["pts_half_ppr"]} if "pts_half_ppr" in fields else week_n.points
    weeks = {**snap.stats.weeks, week_n.week: week_n.model_copy(update={"stats": stats, "points": points})}
    return snap.model_copy(update={"stats": snap.stats.model_copy(update={"weeks": weeks})})


def _jacobs_back_in_week_6(known_snap, **fields):
    """The known-games snapshot with Jacobs due back in week 6, the trade week, and `fields` on his week 6 line."""
    snap = known_snap.model_copy(update={"returns": {JACOBS: 6}, "projections_ahead": {JACOBS: {6: 24.0, 7: 12.0}}})
    return _with_known_game(snap, JACOBS, **fields)


def test_a_player_due_back_in_the_trade_week_who_played_counts_for_his_recent_points_with_no_return_note(known_snap):
    # Jacobs has no game in weeks 3 to 5, so his recent points per game are his week 6 game alone.
    snap = _jacobs_back_in_week_6(known_snap, gp=1.0, pts_half_ppr=21.0)
    assert due_back_week(snap, JACOBS) is None
    assert lineup_value(snap, JACOBS) == recent_points_per_game(snap, JACOBS) == 21
    third, eleventh = grade(_trade(3, [WICKS], 11, [JACOBS]), snap)
    for side in (third, eleventh):
        assert "Josh Jacobs" not in _adjuster(side, "roster fit").reason


def test_a_player_due_back_in_the_trade_week_with_no_game_yet_counts_for_his_projection_ahead(known_snap):
    # His week 6 line shows him active with no game played, so the mean of 24.0 and 12.0 from week 6 holds.
    snap = _jacobs_back_in_week_6(known_snap)
    assert due_back_week(snap, JACOBS) == 6
    assert lineup_value(snap, JACOBS) == 18


def test_a_known_game_keeps_a_later_return_week_and_the_rule_for_an_out_player_with_no_row(known_snap):
    played = _with_known_game(known_snap, JACOBS, gp=1.0, pts_half_ppr=21.0)
    # A returns row past the trade week is a return still ahead.
    assert due_back_week(played.model_copy(update={"returns": {JACOBS: 7}}), JACOBS) == 7
    # Jacobs is NA. With no returns row he is the player hurt in his game, so he counts as back at week 14.
    assert played.players[JACOBS].injury_status == "NA"
    assert due_back_week(played.model_copy(update={"returns": {}}), JACOBS) == 14


def test_a_known_game_ends_the_trend_exemption_of_a_player_due_back_in_the_trade_week(known_snap):
    before = _jacobs_back_in_week_6(known_snap)
    third, _ = grade(_trade(3, [WICKS], 11, [JACOBS]), before)
    assert "Josh Jacobs is due back, so his use does not count." in _adjuster(third, TREND).reason
    played = _jacobs_back_in_week_6(known_snap, gp=1.0, pts_half_ppr=21.0, off_snp=50.0, rec_tgt=4.0)
    third, _ = grade(_trade(3, [WICKS], 11, [JACOBS]), played)
    # His one game gives a share with no direction yet, so the reason has no sentence for him and no note either.
    assert "due back" not in _adjuster(third, TREND).reason
    assert snap_share(played.stats, JACOBS, 6).weeks_used == [6]


def test_a_known_game_ends_the_return_bet_of_a_player_due_back_in_the_trade_week(known_snap):
    played = _jacobs_back_in_week_6(known_snap, gp=1.0, pts_half_ppr=0.0).model_copy(
        update={"projections_ahead": None})
    assert not _return_bet(played, JACOBS)
    third, _ = grade(_trade(3, [WICKS], 11, [JACOBS]), played)
    assert "Josh Jacobs" not in _adjuster(third, "standing").reason


def test_the_player_stat_readers_read_the_player_stat_bound_and_not_the_completed_week_bound(snap):
    # A completed week bound of 0 alone must not move any number that reads the player stats.
    moved = _with_bounds(snap, completed_through=0)
    for pid in (COLLINS, CROSKEY, MCCAFFREY):
        assert recent_points_per_game(moved, pid) == recent_points_per_game(snap, pid)
    trade = _trade(4, [COLLINS, CROSKEY], 3, [MCCAFFREY])
    for before, after in zip(grade(trade, snap), grade(trade, moved)):
        # The position rank reads every player in the league. A bound of 0 puts each player with no week 5 game
        # last, so a rank in the hole sentence can move. The step and every other word must not.
        fit_after, fit_before = _adjuster(after, "roster fit"), _adjuster(before, "roster fit")
        assert fit_after.step == fit_before.step
        assert _without_ranks(fit_after.reason) == _without_ranks(fit_before.reason)
        assert _adjuster(after, TREND) == _adjuster(before, TREND)


def _without_ranks(reason: str) -> str:
    """The reason with each position rank, such as "RB38", cut to its position."""
    return re.sub(r"\b(QB|RB|WR|TE)\d+\b", r"\1", reason)


def test_the_player_stat_readers_of_a_known_games_week_read_its_games(known_snap):
    # The two bounds differ here, so a reader on the completed week bound gives the numbers of the week before.
    at_week_5 = _with_bounds(known_snap, stats_through=5)
    # McCaffrey scored 26.2 in week 6, so weeks 3 to 6 give (19.6 + 14.5 + 15.8 + 26.2) / 4.
    assert recent_points_per_game(known_snap, MCCAFFREY) == Decimal("19.025")
    assert recent_points_per_game(at_week_5, MCCAFFREY) == Decimal("17.625")
    trade = _trade(4, [COLLINS, CROSKEY], 3, [MCCAFFREY])
    assert grade(trade, known_snap) != grade(trade, at_week_5)
    # The share readers take the same bound, so the trend reason names week 6 and the fact sheet says so too.
    first, _ = grade(_trade(1, [WATSON], 4, [ODUNZE]), known_snap)
    assert "over weeks 5 and 6" in _adjuster(first, TREND).reason
    sheet = trade_fact_sheet(_trade(1, [WATSON], 4, [ODUNZE]), known_snap)
    # On a game day the record ends a week before the player stats, so the fact names both bounds.
    assert ("Player stats run through the known games of week 6. The record runs through week 5."
            in sheet["trade.week"].text)
    assert "Every stat" not in sheet["trade.week"].text
    # With the two bounds equal, one bound covers every stat.
    equal = trade_fact_sheet(_trade(1, [WATSON], 4, [ODUNZE]), at_week_5)
    assert "Every stat runs through week 5." in equal["trade.week"].text


# Nico Collins on roster 4 scored 8.1 in week 5 and 27.3 in week 4, and played no game in weeks 2 and 3.
def _collins_week_6(points: float | None):
    """An edit of the raw data that gives Collins `points` in week 6, or no week 6 line at all for None."""
    def edit(raw):
        if points is None:
            raw["stats"] = [row for row in raw["stats"] if row["player_id"] != COLLINS]
        for row in raw["stats"]:
            if row["player_id"] == COLLINS:
                row["stats"]["pts_half_ppr"] = points
        for entry in raw["matchups"]:
            players_points = entry.get("players_points") or {}
            if COLLINS in players_points:
                if points is None:
                    del players_points[COLLINS]
                else:
                    players_points[COLLINS] = points
    return edit


def _lineup_points(snap, roster_id: int) -> Decimal:
    roster = snap.rosters[roster_id]
    return sum((lineup_value(snap, pid) for pid in best_lineup(roster, snap.roster_positions, snap)), Decimal(0))


def test_a_30_point_known_game_counts_in_the_recent_points_per_game_and_moves_the_best_lineup(
        fixture_raw_dir, fixture_history_root, chart_week6):
    big = _known_games_snap(fixture_raw_dir, fixture_history_root, chart_week6, _collins_week_6(30.0))
    none = _known_games_snap(fixture_raw_dir, fixture_history_root, chart_week6, _collins_week_6(None))
    # Weeks 3 to 6 give (27.3 + 8.1 + 30) / 3 with the week 6 game, and (27.3 + 8.1) / 2 without it.
    assert recent_points_per_game(big, COLLINS) == Decimal("21.8")
    assert recent_points_per_game(none, COLLINS) == Decimal("17.7")
    assert COLLINS in best_lineup(big.rosters[4], big.roster_positions, big)
    assert _lineup_points(big, 4) - _lineup_points(none, 4) == Decimal("4.1")


def _no_week_6_line(player_id: str):
    """An edit of the raw data that takes out the week 6 stat line and the week 6 points of the player."""
    def edit(raw):
        raw["stats"] = [row for row in raw["stats"] if row["player_id"] != player_id]
        for entry in raw["matchups"]:
            (entry.get("players_points") or {}).pop(player_id, None)
    return edit


def test_a_player_with_no_known_game_keeps_his_points_per_game_and_no_zero_game(
        snap, fixture_raw_dir, fixture_history_root, chart_week6):
    # McCaffrey played every week from 1 to 5, so a window that slid to weeks 3 to 6 would drop his week 2 game.
    known = _known_games_snap(fixture_raw_dir, fixture_history_root, chart_week6, _no_week_6_line(MCCAFFREY))
    assert known.as_of.stats_through == 6
    # Weeks 2 to 5 give (20.6 + 19.6 + 14.5 + 15.8) / 4, as before week 6.
    assert recent_points_per_game(known, MCCAFFREY) == recent_points_per_game(snap, MCCAFFREY) == Decimal("17.625")
    assert points_per_game(known.stats, MCCAFFREY, 6) == points_per_game(snap.stats, MCCAFFREY, 5)


def test_trend_reads_the_known_game_shares_and_names_its_week(known_snap):
    first, _ = grade(_trade(1, [WATSON], 4, [ODUNZE]), known_snap)
    trend = _adjuster(first, TREND)
    assert "over weeks 5 and 6" in trend.reason


# Malik Nabers on roster 8 gains snap share and target share over weeks 5 and 6.
NABERS = "11632"


def _no_snaps_in_the_game_of(player_id: str):
    """An edit of the raw data that takes the snap counts off every week 6 line of the game of the player.

    Sleeper posts a Sunday game so on Sunday night: targets, points, and red zone touches, but no snaps.
    """
    def edit(raw):
        game = next(row["game_id"] for row in raw["stats"] if row["player_id"] == player_id)
        for row in raw["stats"]:
            if row.get("game_id") == game:
                for key in ("off_snp", "tm_off_snp"):
                    row["stats"].pop(key, None)
    return edit


def test_a_known_game_with_no_snap_count_leaves_the_snap_share_at_the_games_before(
        snap, known_snap, fixture_raw_dir, fixture_history_root, chart_week6):
    pending = _known_games_snap(fixture_raw_dir, fixture_history_root, chart_week6, _no_snaps_in_the_game_of(NABERS))
    assert pending.as_of.known_games.pending == {"snaps": 1}
    # The snap share skips the week 6 game and never reads it as zero snaps.
    assert snap_share(pending.stats, NABERS, 6) == snap_share(snap.stats, NABERS, 5)
    assert snap_share(pending.stats, NABERS, 6).weeks_used == [4, 5]
    # The target share, the points, and the red zone touches read the week 6 line.
    assert target_share(pending.stats, NABERS, 6) == target_share(known_snap.stats, NABERS, 6)
    assert target_share(pending.stats, NABERS, 6).weeks_used == [5, 6]
    assert recent_points_per_game(pending, NABERS) == recent_points_per_game(known_snap, NABERS)
    assert recent_points_per_game(pending, NABERS) != recent_points_per_game(snap, NABERS)
    assert red_zone(pending.stats, NABERS, 6) == red_zone(known_snap.stats, NABERS, 6)


def test_the_trend_reason_names_the_weeks_of_each_share_when_the_snaps_are_pending(
        fixture_raw_dir, fixture_history_root, chart_week6):
    pending = _known_games_snap(fixture_raw_dir, fixture_history_root, chart_week6, _no_snaps_in_the_game_of(NABERS))
    eighth, _ = grade(_trade(8, [NABERS], 1, [WATSON]), pending)
    assert re.search(r"Nabers: snap share \d+% \(weeks 4 and 5\), up, target share \d+% \(weeks 5 and 6\), up\.",
                     _adjuster(eighth, TREND).reason)


def test_a_known_game_with_snap_counts_moves_the_snap_share(snap, known_snap):
    assert known_snap.as_of.known_games.pending == {}
    assert snap_share(known_snap.stats, NABERS, 6).weeks_used == [5, 6]
    assert snap_share(known_snap.stats, NABERS, 6) != snap_share(snap.stats, NABERS, 5)


def test_the_wopr_window_of_a_known_games_week_reads_the_trade_week_row_when_the_file_has_it(known_snap):
    with_week_6 = known_snap.model_copy(update={"wopr": {NABERS: {3: 40, 4: 40, 5: 50, 6: 60}}})
    assert _wopr(with_week_6, NABERS).weeks_used == [5, 6]
    assert _wopr(with_week_6, NABERS).value == 55


def test_the_wopr_window_of_a_known_games_week_ends_at_the_week_before_when_the_file_lacks_the_trade_week(known_snap):
    without_week_6 = known_snap.model_copy(update={"wopr": {NABERS: {2: 40, 3: 40, 4: 50, 5: 60}}})
    assert _wopr(without_week_6, NABERS).weeks_used == [4, 5]
    assert _wopr(without_week_6, NABERS).direction == "up"


# Mike Evans, a WR on roster 1, and Wan'Dale Robinson, a WR on roster 2, played week 6 with flat shares.
EVANS, W_ROBINSON = "2216", "8126"


def test_the_trend_step_reads_a_week_n_wopr_row_when_the_file_has_it_and_ends_a_week_before_without_it(known_snap):
    # Evans gains 15 points of WOPR in both windows, so the step holds and only the weeks in the reason move.
    with_row = known_snap.model_copy(update={"wopr": {EVANS: {3: 40, 4: 40, 5: 55, 6: 55},
                                                      W_ROBINSON: {week: 50 for week in range(1, 7)}}})
    without_row = known_snap.model_copy(update={"wopr": {EVANS: {2: 40, 3: 40, 4: 55, 5: 55},
                                                         W_ROBINSON: {week: 50 for week in range(1, 6)}}})
    trade = _trade(1, [EVANS], 2, [W_ROBINSON])
    _, second_with = grade(trade, with_row)
    _, second_without = grade(trade, without_row)
    assert _adjuster(second_with, TREND).step == _adjuster(second_without, TREND).step == 1
    assert "Evans: WOPR 55, up, over weeks 5 and 6." in _adjuster(second_with, TREND).reason
    assert "Evans: WOPR 55, up, over weeks 4 and 5." in _adjuster(second_without, TREND).reason


def test_a_contender_steps_down_for_a_lineup_loss_now_for_a_player_with_no_return_week(snap):
    # Roster 3 loses McCaffrey at 17.63. Saquon Barkley counts for 12.64 from week 14 and takes his RB spot, a loss
    # of 4.99.
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
        "The team is out of the playoff race, but it gives the highest-value player in the trade "
        "for a lineup gain now.")


def test_the_adjusters_show_in_rubric_order(snap):
    for side in grade(_trade(10, [SAQUON], 5, [COOK]), snap):
        assert [a.name for a in side.adjusters] == [
            "roster fit", "standing", "trend and usage", "injury", "handcuff", "schedule"]


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
    # With stats through week 5, the lineup of roster 7 gains 4.15, so the gain alone earns the step.
    # This case grades the trade on the Tuesday after week 6, so points per game cover weeks 3 to 6.
    # Mahomes at 15.14 takes the QB spot from Lamar Jackson at 19.66, and Brian Robinson starts at flex.
    # The best lineup of roster 7 changes by about -0.60, which is less than the fit threshold.
    snap = build_snapshot(load_raw(fixture_raw_dir), fixture_history_root, chart_week6, trade_week=7)
    rosters = dict(snap.rosters)
    rosters[7] = [pid for pid in rosters[7] if pid not in (MAHOMES, B_ROBINSON)] + [LAMAR]
    rosters[6] = [pid for pid in rosters[6] if pid != LAMAR] + [MAHOMES, B_ROBINSON]
    # Lamar Jackson is Out with no return week, so his projection ahead would set his value. Healthy, he keeps 19.66.
    snap = _with_status(snap.model_copy(update={"rosters": rosters}), LAMAR, None)
    _, seventh = grade(_trade(6, [MAHOMES, B_ROBINSON], 7, [LAMAR]), snap)
    fit = _adjuster(seventh, "roster fit")
    assert fit.step == 1
    assert fit.reason == ("It gets the highest-value player in the trade, and the best lineup does not lose."
                          + NO_SCHEDULES)


# Snap and target share directions through week 5, the last two weeks against the two before.
# Rome Odunze on roster 4 is up in both. Christian Watson on roster 1 is down in both.
# Rashee Rice on roster 1 is down in snap share and up in target share.
ODUNZE, WATSON, RICE = "11620", "8167", "10229"


def test_trend_steps_up_for_the_side_that_gets_the_rising_player_and_down_for_the_other(snap):
    first, fourth = grade(_trade(1, [WATSON], 4, [ODUNZE]), snap)
    assert _adjuster(first, "trend and usage").step == 1
    assert _adjuster(first, "trend and usage").reason == (
        "The players it gets gain snap or target share, and the players it gives lose it. "
        "Odunze: snap share 93%, up, target share 25%, up, over weeks 4 and 5. "
        "Watson: snap share 74%, down, target share 25%, down, over weeks 4 and 5.")
    assert _adjuster(fourth, "trend and usage").step == -1
    assert _adjuster(fourth, "trend and usage").reason == (
        "The players it gets lose snap or target share, and the players it gives gain it. "
        "Watson: snap share 74%, down, target share 25%, down, over weeks 4 and 5. "
        "Odunze: snap share 93%, up, target share 25%, up, over weeks 4 and 5.")


def test_trend_gives_no_step_when_the_shares_point_both_ways(snap):
    # Roster 4 gets Watson, who is down, and Rice, who is down in snap share and up in target share.
    _, fourth = grade(_trade(1, [WATSON, RICE], 4, [ODUNZE]), snap)
    assert _adjuster(fourth, "trend and usage").step == 0
    # Rice played no game in week 5, so his shares cover weeks 3 and 4.
    assert _adjuster(fourth, "trend and usage").reason == (
        "The snap and target shares point both ways. "
        "Watson: snap share 74%, down, target share 25%, down, over weeks 4 and 5. "
        "Rice: snap share 41%, down, target share 31%, up, over weeks 3 and 4. "
        "Odunze: snap share 93%, up, target share 25%, up, over weeks 4 and 5.")


# Roster 2 gives Ja'Marr Chase and Jeremiyah Love, each down in both shares through week 5.
# Roster 6 gives Malik Washington, flat in snap share and up in target share.
CHASE, LOVE, M_WASHINGTON = "7564", "13287", "11610"


def test_trend_reason_gives_the_moved_shares_of_each_player_in_the_chase_trade(snap):
    _, sixth = grade(_trade(2, [CHASE, LOVE], 6, [M_WASHINGTON]), snap)
    trend = _adjuster(sixth, "trend and usage")
    assert trend.step == -1
    # Washington's snap share is flat, so his sentence names only the target share.
    assert trend.reason == (
        "The players it gets lose snap or target share, and the players it gives gain it. "
        "Chase: snap share 52%, down, target share 19%, down, over weeks 4 and 5. "
        "Love: snap share 47%, down, target share 3%, down, over weeks 4 and 5. "
        "Washington: target share 65%, up, over weeks 4 and 5.")


def test_trend_reason_gives_the_weeks_after_each_share_when_the_two_shares_have_different_weeks(snap):
    # With no team snaps in week 5, Chase's snap share covers weeks 3 and 4, and his target share weeks 4 and 5.
    week5 = snap.stats.weeks[5]
    stats = {**week5.stats, CHASE: {**week5.stats[CHASE], "tm_off_snp": 0.0}}
    weeks = {**snap.stats.weeks, 5: week5.model_copy(update={"stats": stats})}
    snap = snap.model_copy(update={"stats": snap.stats.model_copy(update={"weeks": weeks})})
    _, sixth = grade(_trade(2, [CHASE], 6, [M_WASHINGTON]), snap)
    assert _adjuster(sixth, "trend and usage").reason == (
        "The players it gets lose snap or target share, and the players it gives gain it. "
        "Chase: snap share 54% (weeks 3 and 4), down, target share 19% (weeks 4 and 5), down. "
        "Washington: target share 65%, up, over weeks 4 and 5.")


def test_trend_reason_gives_no_sentence_to_a_player_with_flat_shares(snap):
    # Harvey's shares are flat, so only Watson and Odunze get a sentence.
    _, fourth = grade(_trade(1, [WATSON, HARVEY], 4, [ODUNZE]), snap)
    reason = _adjuster(fourth, "trend and usage").reason
    assert "Watson: snap share 74%, down" in reason
    assert "Odunze: snap share 93%, up" in reason
    assert "Harvey" not in reason


# Both shares are flat through week 5 for RJ Harvey on roster 1, with 3 red-zone touches,
# and for Alvin Kamara on roster 9, with 5.
HARVEY, KAMARA = "12489", "4035"


def test_red_zone_use_breaks_the_tie_when_every_share_is_flat(snap):
    first, ninth = grade(_trade(1, [HARVEY], 9, [KAMARA]), snap)
    assert _adjuster(first, "trend and usage").step == 1
    assert _adjuster(first, "trend and usage").reason == (
        "The snap and target shares are flat, and the players it gets have more red-zone use.")
    assert _adjuster(ninth, "trend and usage").step == -1


# Both shares are flat through week 5 for Jameson Williams, a WR on roster 4 with 3 red-zone touches,
# and for Michael Wilson, a WR on roster 5 with 9. Red-zone use alone steps roster 4 up.
# Each played weeks 1 to 5, so the WOPR window is weeks 2 to 5.
J_WILLIAMS, M_WILSON = "8148", "10232"


def _with_wopr(snap, woprs: dict[str, list[int | None]]):
    """The snapshot with hand-set WOPR for weeks 2 to 5. A None leaves that week out, as a missing row of the file."""
    wopr = {pid: {week: value for week, value in zip(range(2, 6), values) if value is not None}
            for pid, values in woprs.items()}
    return snap.model_copy(update={"wopr": wopr})


def test_wopr_up_breaks_a_flat_trend_before_red_zone_use(snap):
    snap = _with_wopr(snap, {J_WILLIAMS: [40, 40, 55, 55], M_WILSON: [50] * 4})
    fourth, fifth = grade(_trade(4, [J_WILLIAMS], 5, [M_WILSON]), snap)
    assert _adjuster(fifth, "trend and usage").step == 1
    assert _adjuster(fifth, "trend and usage").reason == (
        "The snap and target shares are flat. The players it gets gain WOPR, and the players it gives lose it. "
        "Williams: WOPR 55, up, over weeks 4 and 5.")
    assert _adjuster(fourth, "trend and usage").step == -1
    assert _adjuster(fourth, "trend and usage").reason.startswith(
        "The snap and target shares are flat. The players it gets lose WOPR, and the players it gives gain it.")


def test_a_flat_wopr_falls_through_to_red_zone_use(snap):
    # Williams moves 7 points, under the WOPR swing of 8.
    snap = _with_wopr(snap, {J_WILLIAMS: [40, 40, 47, 47], M_WILSON: [50] * 4})
    fourth, _ = grade(_trade(4, [J_WILLIAMS], 5, [M_WILSON]), snap)
    assert _adjuster(fourth, "trend and usage").step == 1
    assert _adjuster(fourth, "trend and usage").reason == (
        "The snap and target shares are flat, and the players it gets have more red-zone use.")


def test_a_wopr_that_points_both_ways_falls_through_to_red_zone_use(snap):
    # Both WOPRs rise, so each side gets a gain and gives a gain.
    snap = _with_wopr(snap, {J_WILLIAMS: [40, 40, 55, 55], M_WILSON: [40, 40, 55, 55]})
    fourth, fifth = grade(_trade(4, [J_WILLIAMS], 5, [M_WILSON]), snap)
    assert _adjuster(fourth, "trend and usage").step == 1
    assert _adjuster(fourth, "trend and usage").reason == (
        "The snap and target shares are flat, and the players it gets have more red-zone use.")
    assert _adjuster(fifth, "trend and usage").step == -1


@pytest.mark.parametrize("woprs", [[None, 40, 55, 55], [40, None, 55, 55], [40, 40, 55, None]])
def test_a_wopr_with_no_value_at_either_end_of_the_window_falls_through_to_red_zone_use(snap, woprs):
    snap = _with_wopr(snap, {J_WILLIAMS: woprs, M_WILSON: [50] * 4})
    fourth, _ = grade(_trade(4, [J_WILLIAMS], 5, [M_WILSON]), snap)
    assert _adjuster(fourth, "trend and usage").step == 1
    assert "red-zone use" in _adjuster(fourth, "trend and usage").reason


def test_a_stats_outage_keeps_wopr_from_deciding(snap):
    # Week 3 has no stat lines, so the played weeks skip it and the window would be weeks 1, 2, 4, and 5.
    # Week 1 has a WOPR, so only the outage check keeps that window from deciding.
    week3 = snap.stats.weeks[3].model_copy(update={"stats": {}})
    stats = snap.stats.model_copy(update={"weeks": {**snap.stats.weeks, 3: week3}})
    snap = _with_wopr(snap.model_copy(update={"stats": stats}), {J_WILLIAMS: [40, 40, 55, 55], M_WILSON: [50] * 4})
    snap.wopr[J_WILLIAMS][1] = 40
    fourth, _ = grade(_trade(4, [J_WILLIAMS], 5, [M_WILSON]), snap)
    assert "WOPR" not in _adjuster(fourth, "trend and usage").reason


def test_a_running_backs_wopr_never_decides(snap):
    # Harvey and Kamara are RBs, so Kamara's rising WOPR leaves the red-zone tiebreak to decide.
    snap = _with_wopr(snap, {HARVEY: [10] * 4, KAMARA: [10, 10, 30, 30]})
    first, _ = grade(_trade(1, [HARVEY], 9, [KAMARA]), snap)
    assert _adjuster(first, "trend and usage").step == 1
    assert _adjuster(first, "trend and usage").reason == (
        "The snap and target shares are flat, and the players it gets have more red-zone use.")


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


def test_the_injury_report_of_a_known_games_week_ends_at_the_completed_week(known_snap):
    # The player stats run through week 6 here, but the injury report ends at week 5.
    # Weeks 3, 4, and 6 are three report weeks, so a read through week 6 would step down.
    assert known_snap.as_of.stats_through == 6
    assert known_snap.as_of.completed_through == 5
    snap = known_snap.model_copy(update={"id_map": {OLAVE: OLAVE_GSIS},
                                         "injuries": {OLAVE_GSIS: {3: "Questionable", 4: "Questionable", 6: "Out"}}})
    trade = _trade(3, [MEYERS], 2, [OLAVE])
    third, _ = grade(trade, snap)
    assert _adjuster(third, "injury").step == 0
    assert "on the NFL injury report in 2 weeks this season before the trade." in (
        trade_fact_sheet(trade, snap)[f"{OLAVE}.injury"].text)


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
# Mitchell takes 24 of 94 LAC carries in weeks 3 to 5, or 25.5%, so the gate frees him.
# At 4 carries a game he takes 12 of 82, or 15%, so he is a handcuff.
LAC_THIN = {3: 4.0, 4: 4.0, 5: 4.0}


def _lac_snap(slow_snap):
    """The week 5 bound snapshot with the LAC gsis_ids, and Mitchell at 15% of the carries."""
    return with_carries(_with_ids(slow_snap, LAC_IDS), MITCHELL, LAC_THIN)


def _with_ids(snap, ids: dict[str, str]):
    return snap.model_copy(update={"id_map": {**snap.id_map, **ids}})


def test_a_handcuff_with_a_chart_row_counts_as_zero_in_the_sums(slow_snap):
    # With Mitchell at 10.0 for Pollard at 9.0, roster 12 would start at B and roster 11 at C.
    snap = _with_values(_lac_snap(slow_snap), {MITCHELL: 10.0})
    twelfth, eleventh = grade(_trade(12, [POLLARD], 11, [MITCHELL]), snap)
    assert _letters([twelfth, eleventh]) == ["F", "A"]
    handcuff = _adjuster(twelfth, "handcuff")
    assert handcuff.step == 0
    assert handcuff.reason == "Keaton Mitchell backs up the team's own starter, so he counts as insurance."
    # The id map fixture lacks Pollard, so the reason of roster 11 also names him.
    assert _adjuster(eleventh, "handcuff").reason.startswith("No player it gets is a handcuff.")


def test_a_freed_backup_with_a_chart_row_counts_in_the_sums(slow_snap):
    # Mitchell takes 25.5% of the LAC carries, so he counts. At 10.0 for Pollard at 9.0, roster 12 starts at B
    # and roster 11 at C.
    snap = _with_values(_with_ids(slow_snap, LAC_IDS), {MITCHELL: 10.0})
    twelfth, eleventh = grade(_trade(12, [POLLARD], 11, [MITCHELL]), snap)
    assert _letters([twelfth, eleventh]) == ["B", "C"]
    assert _adjuster(twelfth, "handcuff").reason == (
        "Keaton Mitchell backs up the team's own starter but takes 26% of the carries, "
        "so he counts as a running back.")


def test_a_handcuff_with_no_chart_row_keeps_the_start_letter(slow_snap):
    # Mitchell has no trade value. As a handcuff he counts as zero, so no side starts at C for him.
    twelfth, eleventh = grade(_trade(12, [POLLARD], 11, [MITCHELL]), _lac_snap(slow_snap))
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
    # LAC moves its bye to week 12, past the window. Otherwise Hampton starts at FLEX2 with his bye in week 7 and no
    # cover, and that hole steps down, as a handcuff never blocks a hole.
    twelfth, _ = grade(_trade(12, [ST_BROWN], 11, [MITCHELL]), _with_bye(_lac_snap(slow_snap), "LAC", 12))
    fit = _adjuster(twelfth, "roster fit")
    assert fit.step == 0
    assert fit.reason == (
        "The best lineup loses after the trade, but Keaton Mitchell is a handcuff, so the loss does not count.")


def test_fit_can_step_down_for_a_freed_backup(slow_snap):
    # Mitchell takes 25.5% of the LAC carries, so he is no handcuff, and the lineup loss counts.
    twelfth, _ = grade(_trade(12, [ST_BROWN], 11, [MITCHELL]), _with_ids(slow_snap, LAC_IDS))
    fit = _adjuster(twelfth, "roster fit")
    assert fit.step == -1
    assert "handcuff" not in fit.reason


# The NE depth chart: Rhamondre Stevenson on roster 7 first, then TreVeyon Henderson on roster 8.
# Henderson's snap share is down through week 5. The Carolina defense has no share direction and no red-zone use.
STEVENSON, HENDERSON, CAR_DEF = "7611", "12529", "CAR"
NE_IDS = {STEVENSON: "00-0036875", HENDERSON: "00-0040734"}
# The other NE backs take 11, 21, and 21 carries in weeks 3 to 5. Henderson takes 26 of 79, or 33%.
# At 3 carries a game he takes 9 of 62, or 15%. At 11 a game he takes 33 of 86, or 38%.
# Edge: with Stevenson at 29 carries, Henderson at 16 takes 16 of 65, or 24.6%, and at 17 takes 17 of 66, or 25.8%.
EDGE_STEVENSON, EDGE_UNDER, EDGE_OVER = {3: 7.0, 4: 13.0, 5: 9.0}, {3: 5.0, 4: 5.0, 5: 6.0}, {3: 5.0, 4: 6.0, 5: 6.0}
THIN, REAL = {3: 3.0, 4: 3.0, 5: 3.0}, {3: 11.0, 4: 11.0, 5: 11.0}


def _ne_snap(slow_snap, carries=THIN):
    """The week 5 bound snapshot with the NE gsis_ids, and Henderson at `carries` in weeks 3 to 5."""
    return with_carries(_with_ids(slow_snap, NE_IDS), HENDERSON, carries)


def test_the_carry_share_reads_the_last_3_played_games(slow_snap):
    # The share is exact, so a gate can compare it. The reason rounds it.
    assert carry_share(slow_snap.stats, HENDERSON, 5) == pytest.approx(100 * 26 / 79)
    assert carry_share(_ne_snap(slow_snap).stats, HENDERSON, 5) == pytest.approx(100 * 9 / 62)
    assert carry_share(_ne_snap(slow_snap, REAL).stats, HENDERSON, 5) == pytest.approx(100 * 33 / 86)
    # Henderson played no game in week 1, so through week 2 he has 1 played game and no share.
    assert carry_share(slow_snap.stats, HENDERSON, 2) is None


def test_a_backup_at_38_percent_of_the_carries_is_no_handcuff(slow_snap):
    snap = _ne_snap(slow_snap, REAL)
    trade = _trade(7, [CAR_DEF], 8, [HENDERSON])
    assert rubric.trade_handcuffs(trade, snap) == []
    seventh, _ = grade(trade, snap)
    assert _adjuster(seventh, "handcuff").reason == (
        "TreVeyon Henderson backs up the team's own starter but takes 38% of the carries, "
        "so he counts as a running back.")
    # His falling snap share counts now, so the trend steps roster 7 down as for any running back.
    trend = _adjuster(seventh, "trend and usage")
    assert trend.step == -1
    assert "handcuff" not in trend.reason


def test_a_backup_at_15_percent_of_the_carries_is_a_handcuff(slow_snap):
    snap = _ne_snap(slow_snap)
    trade = _trade(7, [CAR_DEF], 8, [HENDERSON])
    assert rubric.trade_handcuffs(trade, snap) == [HENDERSON]
    seventh, _ = grade(trade, snap)
    assert _adjuster(seventh, "handcuff").reason == (
        "TreVeyon Henderson backs up the team's own starter, so he counts as insurance.")


def test_the_gate_compares_the_exact_share_and_the_reason_rounds_it(slow_snap):
    trade = _trade(7, [CAR_DEF], 8, [HENDERSON])
    base = with_carries(_with_ids(slow_snap, NE_IDS), STEVENSON, EDGE_STEVENSON)
    # 24.6% rounds to 25%, but the exact share is below the gate, so he is a handcuff.
    under = with_carries(base, HENDERSON, EDGE_UNDER)
    assert carry_share(under.stats, HENDERSON, 5) == pytest.approx(100 * 16 / 65)
    assert rubric.trade_handcuffs(trade, under) == [HENDERSON]
    over = with_carries(base, HENDERSON, EDGE_OVER)
    assert rubric.trade_handcuffs(trade, over) == []
    seventh, _ = grade(trade, over)
    assert _adjuster(seventh, "handcuff").reason == (
        "TreVeyon Henderson backs up the team's own starter but takes 26% of the carries, "
        "so he counts as a running back.")


def test_a_backup_with_1_played_game_or_no_carry_data_keeps_the_depth_chart_answer(slow_snap):
    trade = _trade(7, [CAR_DEF], 8, [HENDERSON])
    # Through week 2 Henderson has 1 played game, at 16 of 26 carries.
    one_game = _with_bounds(_with_ids(slow_snap, NE_IDS), stats_through=2)
    assert rubric.trade_handcuffs(trade, one_game) == [HENDERSON]
    # With no carries in any stat line, no team has carry data.
    snap = _with_ids(slow_snap, NE_IDS)
    weeks = {week: past.model_copy(update={"stats": {pid: {k: v for k, v in line.items() if k != "rush_att"}
                                                     for pid, line in past.stats.items()}})
             for week, past in snap.stats.weeks.items()}
    no_carries = snap.model_copy(update={"stats": snap.stats.model_copy(update={"weeks": weeks})})
    assert carry_share(no_carries.stats, HENDERSON, 5) is None
    assert rubric.trade_handcuffs(trade, no_carries) == [HENDERSON]


def test_a_known_game_can_lift_a_backup_over_the_carry_gate(fixture_raw_dir, fixture_history_root, chart_week6,
                                                            fixture_nflverse_dir, tmp_path):
    # Henderson takes 7 of 36 NE carries in week 6. At 3 carries in weeks 4 and 5, weeks 4 to 6 give 13 of 84,
    # or 15%.
    cache = tmp_path / "nflverse"
    shutil.copytree(fixture_nflverse_dir, cache)
    slow = load_slow_sources(cache, 2026, 6, fixture_history_root)
    known = _with_ids(_known_games_snap(fixture_raw_dir, fixture_history_root, chart_week6, slow=slow), NE_IDS)
    known = with_carries(known, HENDERSON, {4: 3.0, 5: 3.0})
    assert (known.as_of.stats_through, known.as_of.completed_through) == (6, 5)
    trade = _trade(7, [CAR_DEF], 8, [HENDERSON])
    assert rubric.trade_handcuffs(trade, known) == [HENDERSON]
    # A breakout of 20 carries in a Thursday game gives 26 of 97, or 27%, before the week is complete.
    breakout = with_carries(known, HENDERSON, {6: 20.0})
    assert rubric.trade_handcuffs(trade, breakout) == []
    seventh, _ = grade(trade, breakout)
    assert _adjuster(seventh, "handcuff").reason == (
        "TreVeyon Henderson backs up the team's own starter but takes 27% of the carries, "
        "so he counts as a running back.")


def test_trend_never_steps_down_because_of_a_handcuff(snap, slow_snap):
    trade = _trade(7, [CAR_DEF], 8, [HENDERSON])
    # With no depth chart, Henderson is no handcuff, and his falling share steps roster 7 down.
    seventh, _ = grade(trade, snap)
    assert _adjuster(seventh, "trend and usage").step == -1
    seventh, _ = grade(trade, _ne_snap(slow_snap))
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


def test_schedule_without_its_sources_is_even_and_says_so(snap):
    for side in grade(_trade(10, [SAQUON], 5, [COOK]), snap):
        schedule = _adjuster(side, "schedule")
        assert (schedule.step, schedule.lean) == (0, "even")
        assert schedule.reason == "The schedule sources are not available."


# Byes and playoff opponents from the nflverse fixture, for a trade in week 6.
# Saquon Barkley plays for PHI, with the bye in week 10 still left. His week 15 to 17 opponents are SEA, HOU, and SF,
# ranked 18, 28, and 15 in points allowed to running backs, a mean of 20.33.
# James Cook plays for BUF, with the bye in week 7 still left. His opponents are CHI, DEN, and MIA,
# ranked 25, 7, and 6, a mean of 12.67. That is 7.67 softer, past the gap of 4.
def test_schedule_leans_for_the_side_that_gets_softer_playoff_opponents_and_against_the_other(slow_snap):
    tenth, fifth = grade(_trade(10, [SAQUON], 5, [COOK]), slow_snap)
    for_tenth, against_fifth = _adjuster(tenth, "schedule"), _adjuster(fifth, "schedule")
    assert (for_tenth.step, for_tenth.lean) == (0, "for")
    assert for_tenth.reason == (
        "The players it gets and the players it gives have the same count of byes left, "
        "and the players it gets face softer playoff opponents at their positions. The schedule leans for this side.")
    assert (against_fifth.step, against_fifth.lean) == (0, "against")
    assert against_fifth.reason == (
        "The players it gets and the players it gives have the same count of byes left, "
        "and the players it gets face harder playoff opponents at their positions. "
        "The schedule leans against this side.")


def _with_bye(snap, team: str, week: int):
    schedules = dict(snap.schedules)
    schedules[team] = schedules[team].model_copy(update={"bye_week": week})
    return snap.model_copy(update={"schedules": schedules})


def test_schedule_is_even_when_the_byes_and_the_playoff_opponents_conflict(slow_snap):
    # With the PHI bye moved to week 5, Saquon Barkley's bye is done and James Cook's bye is left.
    # Roster 10 then gets more byes left, which leans against, and softer playoff opponents, which lean for.
    tenth, _ = grade(_trade(10, [SAQUON], 5, [COOK]), _with_bye(slow_snap, "PHI", 5))
    schedule = _adjuster(tenth, "schedule")
    assert (schedule.step, schedule.lean) == (0, "even")
    assert schedule.reason == (
        "The players it gets have more byes left than the players it gives, "
        "and the players it gets face softer playoff opponents at their positions. The schedule is even.")


def test_schedule_leans_on_the_byes_alone_when_the_playoff_opponents_are_even(slow_snap):
    # With the BUF opponents set to those of PHI, the playoff signal is even.
    # With the BUF bye moved to week 5, roster 10 gets fewer byes left, which leans for.
    schedules = dict(slow_snap.schedules)
    schedules["BUF"] = schedules["PHI"].model_copy(update={"bye_week": 5})
    tenth, fifth = grade(_trade(10, [SAQUON], 5, [COOK]), slow_snap.model_copy(update={"schedules": schedules}))
    assert (_adjuster(tenth, "schedule").lean, _adjuster(fifth, "schedule").lean) == ("for", "against")
    assert _adjuster(tenth, "schedule").reason.startswith(
        "The players it gets have fewer byes left than the players it gives, "
        "and the playoff opponents are about as hard on both sides.")


def test_a_kicker_does_not_count_in_the_byes_left(slow_snap):
    # Saquon Barkley's PHI bye in week 10 is still left. As a kicker, he has no points allowed rank,
    # so he counts on neither signal.
    players = dict(slow_snap.players)
    players[SAQUON] = players[SAQUON].model_copy(update={"position": "K"})
    kicker_snap = slow_snap.model_copy(update={"players": players})
    assert _byes_left(slow_snap, [SAQUON]) == 1
    assert _byes_left(kicker_snap, [SAQUON]) == 0


# Bucky Irving on roster 1, Derrick Henry on roster 3, and Rashee Rice on roster 1, who is out with no return week.
IRVING, HENRY = "11584", "3198"


def test_the_clamp_holds_three_steps_up_to_one(snap):
    # Roster 1, a contender, gets Henry for Irving. Its best lineup gains now, and the shares favor it:
    # roster fit, standing, and trend each step up. Irving at 40 for Henry at 20 starts roster 1 at F.
    # Three steps up from F would reach B. The clamp holds the sum at one, so the final letter is D.
    first, _ = grade(_trade(1, [IRVING], 3, [HENRY]), _with_values(snap, {IRVING: 40.0, HENRY: 20.0}))
    assert first.start_letter == "F"
    assert [a.step for a in first.adjusters] == [1, 1, 1, 0, 0, 0]
    assert first.final_letter == "D"


def test_the_clamp_holds_three_steps_down_to_one(snap):
    # Roster 5, a contender, gets Rice for Cook. Its best lineup loses now for a player with no return week,
    # and Rice is out: roster fit, standing, and injury each step down. Rice at 40 for Cook at 20 starts it at A.
    # Three steps down from A would reach D. The clamp holds the sum at one, so the final letter is B.
    fifth, _ = grade(_trade(5, [COOK], 1, [RICE]), _with_values(snap, {RICE: 40.0, COOK: 20.0}))
    assert fifth.start_letter == "A"
    assert [a.step for a in fifth.adjusters] == [-1, -1, 0, -1, 0, 0]
    assert fifth.final_letter == "B"


def test_the_same_trade_on_the_same_snapshot_gives_the_same_breakdown_every_time(slow_snap):
    trade = _trade(11, [TUTEN, WILSON], 12, [JACOBS, VELE])
    snap = _before_the_jacobs_trade(slow_snap)
    first = grade(trade, snap)
    assert all(grade(trade, snap) == first for _ in range(3))


def _graded(roster_id: int, final: str, lean: str = "even") -> Breakdown:
    """A breakdown with a final letter and a schedule lean, the two parts the verdict reads."""
    schedule = Adjuster(name="schedule", step=0, lean=lean, reason="The schedule is even.")
    return Breakdown(roster_id=roster_id, start_letter=final, reason="", adjusters=[schedule], final_letter=final)


def _verdict_for(asker_final: str, other_final: str, lean: str = "even") -> Verdict:
    """The verdict for roster 4, the asker, in a trade with roster 12."""
    trade = _trade(4, [CROSKEY], 12, [KINCAID], asker=4)
    return verdict(trade, (_graded(4, asker_final, lean), _graded(12, other_final)))


@pytest.mark.parametrize("asker, other", [("A", "A"), ("B", "A"), ("B", "F")])
def test_the_verdict_accepts_at_b_or_better(asker, other):
    assert _verdict_for(asker, other).choice == "accept"
    assert _verdict_for(asker, other).reason == "The trade favors the asking side."


@pytest.mark.parametrize("other, sides", [
    ("C", "The two sides are about even"), ("D", "The asking side does better"), ("F", "The asking side does better"),
])
def test_the_verdict_accepts_at_c_when_the_other_side_is_at_c_or_worse(other, sides):
    result = _verdict_for("C", other)
    assert result.choice == "accept"
    assert result.reason == f"{sides}, so the trade is fair."


@pytest.mark.parametrize("asker, other", [("D", "F"), ("F", "F"), ("D", "A")])
def test_the_verdict_declines_at_d_or_worse(asker, other):
    result = _verdict_for(asker, other)
    assert result.choice == "decline"
    assert result.reason == "The trade costs the asking side too much."


@pytest.mark.parametrize("other", ["A", "B"])
def test_the_verdict_counters_at_c_when_the_other_side_does_better(other):
    result = _verdict_for("C", other)
    assert result.choice == "counter"
    assert result.reason == "The other side does better, so ask for more."


def test_a_schedule_for_the_asker_turns_a_counter_into_an_accept():
    result = _verdict_for("C", "B", lean="for")
    assert result.choice == "accept"
    assert result.reason == (
        "The other side does better, but the schedule leans for the asking side, "
        "so the trade is worth it.")


def test_a_schedule_against_the_asker_turns_an_accept_at_c_into_a_counter():
    result = _verdict_for("C", "D", lean="against")
    assert result.choice == "counter"
    assert result.reason == (
        "The asking side does better, but the schedule leans against the asking side, "
        "so ask for more.")


def test_a_schedule_against_the_asker_at_even_letters_turns_an_accept_into_a_counter():
    result = _verdict_for("C", "C", lean="against")
    assert result.choice == "counter"
    assert result.reason == (
        "The two sides are about even, but the schedule leans against the asking side, so ask for more.")


@pytest.mark.parametrize("asker, lean, choice", [("B", "against", "accept"), ("D", "for", "decline")])
def test_the_schedule_never_turns_a_clear_accept_or_a_decline(asker, lean, choice):
    assert _verdict_for(asker, "C", lean=lean).choice == choice


def test_the_verdict_reads_the_asker_side_whichever_side_it_is():
    trade = _trade(4, [CROSKEY], 12, [KINCAID], asker=12)
    assert verdict(trade, (_graded(4, "A"), _graded(12, "F"))).choice == "decline"


# The adjusters in rubric order before the schedule, which never steps.
STEPPED = ("roster fit", "standing", "trend and usage", "injury", "handcuff")


def _sided(roster_id: int, final: str, start: str | None = None, steps: tuple[int, ...] = ()) -> Breakdown:
    """A breakdown with a start letter, the steps of the adjusters in rubric order, and a final letter.

    Each reason names its side and its adjuster, so a test sees which reason the fairness rule took.
    """
    adjusters = [Adjuster(name=name, step=step, reason=f"Side {roster_id} {name}.")
                 for name, step in zip(STEPPED, steps)]
    adjusters.append(Adjuster(name="schedule", step=0, lean="even", reason="The schedule is even."))
    return Breakdown(roster_id=roster_id, start_letter=start or final, reason=f"Side {roster_id} start.",
                     adjusters=adjusters, final_letter=final)


def _fairness_for(first: Breakdown, second: Breakdown, letters: tuple[str, str] | None = None):
    """The fairness of a trade between roster 4 and roster 12. The letters default to the breakdowns' final letters."""
    letters = letters or (first.final_letter, second.final_letter)
    return fairness(letters, (first, second))


@pytest.mark.parametrize("first, second", [("B", "B"), ("A", "B"), ("B", "A")])
def test_fairness_is_win_win_when_both_sides_are_at_b_or_better(first, second):
    result = _fairness_for(_sided(4, first), _sided(12, second))
    assert result.state == "win_win"
    assert result.gives_more is None


def test_fairness_is_fair_when_both_sides_are_at_c():
    result = _fairness_for(_sided(4, "C"), _sided(12, "C"))
    assert result.state == "fair"
    assert result.gives_more is None


@pytest.mark.parametrize("first, second, gives_more", [("C", "D", 12), ("D", "C", 4), ("A", "F", 12), ("F", "A", 4)])
def test_fairness_is_lopsided_when_either_side_is_at_d_or_worse_and_names_the_lower_side(first, second, gives_more):
    result = _fairness_for(_sided(4, first), _sided(12, second))
    assert result.state == "lopsided"
    assert result.gives_more == gives_more


def test_at_equal_letters_the_side_with_the_lower_start_letter_gives_more():
    result = _fairness_for(_sided(4, "D", start="C", steps=(-1,)), _sided(12, "D", start="F", steps=(1,)))
    assert result.state == "lopsided"
    assert result.gives_more == 12


def test_at_equal_letters_and_equal_starts_the_first_side_gives_more():
    result = _fairness_for(_sided(4, "F"), _sided(12, "F"))
    assert result.gives_more == 4


def test_the_reason_of_a_side_is_its_first_adjuster_with_a_step_up_in_rubric_order():
    # Standing steps down before trend steps up, and injury steps up after trend.
    result = _fairness_for(_sided(4, "B", start="C", steps=(0, -1, 1, 1)), _sided(12, "B", start="C", steps=(1,)))
    assert [(side.roster_id, side.reason) for side in result.sides] == [
        (4, "Side 4 trend and usage."), (12, "Side 12 roster fit.")]


def test_a_side_with_no_step_up_gets_the_reason_of_its_start_letter():
    result = _fairness_for(_sided(4, "D", start="C", steps=(0, -1)), _sided(12, "C", steps=(1, -1)))
    assert [side.reason for side in result.sides] == ["Side 4 start.", "Side 12 roster fit."]


def test_the_sides_come_in_the_order_of_the_inputs():
    result = fairness(("C", "C"), (_sided(12, "C"), _sided(4, "C")))
    assert [side.roster_id for side in result.sides] == [12, 4]


def test_fairness_reads_the_letters_it_gets_and_not_the_breakdown_final_letters():
    # Claude may move a final letter one step, and that letter stands, so the rule reads it.
    result = _fairness_for(_sided(4, "C"), _sided(12, "C"), letters=("B", "B"))
    assert result.state == "win_win"


# The six real week 6 trades, newest first, as in the transactions file: (roster a, a gives, roster b, b gives, asker).
# The asker is the roster that made the trade in Sleeper.
# The saved rosters show the league after all six. To grade one trade, the test sets back that trade and every
# trade newer than it, newest first. Roster 7 is in four trades: with roster 8, then 6, then 4, then 12.
# Brian Robinson moves in two of them, so the order matters: the 7-8 set-back puts him on roster 7,
# and the 6-7 set-back then puts him on roster 6.
REAL_TRADES = [
    (7, [HARRISON, B_ROBINSON, BIJAN], 8, ["11576", "11632", "3163", "8155"], 8),
    # The Josh Jacobs trade.
    (11, [TUTEN, WILSON], 12, [JACOBS, VELE], 12),
    (6, [MAHOMES, B_ROBINSON], 7, [LAMAR], 7),
    (4, ["11635", "7611"], 7, ["12481", COLLINS], 7),
    (7, [KINCAID], 12, ["13330"], 12),
    (4, ["12507", "5967"], 12, [CROSKEY, "5892"], 12),
]


def _before_real_trade(snap, index: int):
    """The snapshot with the rosters set back to before REAL_TRADES[index], one trade at a time, newest first."""
    rosters = {roster_id: list(players) for roster_id, players in snap.rosters.items()}
    for a, a_gives, b, b_gives, _ in REAL_TRADES[:index + 1]:
        rosters[a] = [pid for pid in rosters[a] if pid not in b_gives] + a_gives
        rosters[b] = [pid for pid in rosters[b] if pid not in a_gives] + b_gives
    return snap.model_copy(update={"rosters": rosters})


# Each row: the start letter, the six adjuster steps, the schedule lean, and the final letter of side a, then of
# side b, then the verdict for the asker. Worked by hand from the rubric on the week 6 snapshot with the nflverse
# fixture and the returns file: trade values from the week 6 chart, points per game over weeks 2 to 5,
# standings through week 5, and shares of weeks 4 and 5 against weeks 2 and 3. Trade week N is 6, so a bye in
# week 6 or later is left. Roster 4 is a seller at 1-9. Roster 6 is a contender. Rosters 7, 8, 11, and 12 are
# in the middle at 4-6.
HAND_WORKED = [
    # Roster 7 gives Marvin Harrison 36.0, Brian Robinson 22.0, and Bijan Robinson 20.5, a sum of 78.5.
    # Roster 8 gives Braelon Allen 1.5, Malik Nabers 6.5, Jared Goff 13.0, and Breece Hall 41.0, a sum of 62.0.
    # Three for four is no consolidation. Roster 7: 62.0 over 78.5 is 0.790, D. Roster 8: 1.266, A.
    # Breece Hall at 41.0 is the highest-value player.
    # Roster 7: Breece Hall is out with no return week, so he counts as back in week 14 at 11.7 a game. The lineup
    # changes by minus 2.18, no loss, and it gets the highest-value player, fit up. Middle, no standing step. Gets
    # up shares only, gives up and down shares, so trend is mixed. Breece Hall is out with no return week, injury
    # down. Byes left: four got against three gave, against. Playoff opponent mean rank 18.58 got against 16.67
    # gave, inside the gap, even. Schedule against. Sum zero, D stays D.
    # Roster 8: the lineup gains 0.34, under the threshold, and it gives the highest-value player, no fit step.
    # Middle. Trend mixed. Nothing out. Byes three got against four gave, for. Schedule for. Sum zero, A.
    # Roster 8 asked and grades A: accept.
    (("D", [1, 0, 0, -1, 0, 0], "against", "D"), ("A", [0, 0, 0, 0, 0, 0], "for", "A"), "accept"),
    # The Josh Jacobs trade. Roster 11 gives Bhayshul Tuten 3.0 and Garrett Wilson 27.5, a sum of 30.5.
    # Roster 12 gives Josh Jacobs 11.5 and Devaughn Vele 55.0, a sum of 66.5. Two for two, no consolidation.
    # Roster 11: 66.5 over 30.5 is 2.18, A. Roster 12: 0.459, F. Vele is the highest-value player.
    # Jacobs is due back in week 7, so his use does not count, and week 7 is inside the return window of week 8.
    # Roster 11: the lineup loses 6.94, fit down. Middle. Gets Vele, flat, and gives Tuten and Wilson, each with
    # one share up, so trend down. No injury step. Byes two and two, even. Playoff mean rank 13.83 got against
    # 16.83 gave, a gap of 3.0, inside the gap, even. Schedule even. Sum minus two, clamped to minus one, A to B.
    # Roster 12: the lineup gains 5.57, fit up. Middle. Trend up. No injury step. Schedule even.
    # Sum plus two, clamped to plus one, F to D.
    # Roster 12 asked and grades D, with roster 11 at B: decline.
    (("A", [-1, 0, -1, 0, 0, 0], "even", "B"), ("F", [1, 0, 1, 0, 0, 0], "even", "D"), "decline"),
    # Roster 6 gives Patrick Mahomes 15.5 and Brian Robinson 22.0, a sum of 37.5. Roster 7 gives Lamar Jackson 7.0.
    # One for two: the depth sum counts as 37.5 over 1.25, which is 30.0. Roster 6: 7.0 over 30.0 is 0.233, F.
    # Roster 7: 4.29, A. Brian Robinson at 22.0 is the highest-value player.
    # Roster 6: Lamar Jackson is out with no return week, so he counts as back in week 14 at 22.7 a game. The
    # lineup changes by minus 0.22, about the same, no fit step. A contender with no lineup gain and no return bet,
    # no standing step. Gets one share down, gives one share down, so trend is mixed. Lamar Jackson is out with no
    # return week, injury down. Byes one left and one left, even. Playoff mean rank 19.67 got against 22.17 gave,
    # inside the gap, even. Schedule even. Sum minus one, F stays F.
    # Roster 7: the lineup gains 4.15 and both players it gets start, fit up. Middle. Trend mixed. No injury step.
    # Schedule even. Sum plus one, A stays A.
    # Roster 7 asked and grades A: accept.
    (("F", [0, 0, 0, -1, 0, 0], "even", "F"), ("A", [1, 0, 0, 0, 0, 0], "even", "A"), "accept"),
    # Roster 4 gives Ladd McConkey 4.5 and Rhamondre Stevenson 2.5, a sum of 7.0.
    # Roster 7 gives Cam Skattebo 18.0 and Nico Collins 46.5, a sum of 64.5. Two for two, no consolidation.
    # Roster 4: 64.5 over 7.0 is 9.21, A. Roster 7: 0.109, F. Nico Collins is the highest-value player.
    # Roster 4: the lineup gains 4.75, fit up. A seller that gets the highest-value player, standing up.
    # Gets one share down, gives shares up and down, so trend is mixed. No injury step. Byes two and two, even.
    # Playoff mean rank 14.00 got against 19.67 gave, a gap of 5.67, for. Schedule for.
    # Sum plus two, clamped to plus one, A stays A.
    # Roster 7: the lineup loses 4.63, fit down. Middle. Trend mixed. Ladd McConkey is out with no return week,
    # injury down. Schedule against. Sum minus two, clamped to minus one, F stays F.
    # Roster 7 asked and grades F: decline.
    (("A", [1, 1, 0, 0, 0, 0], "for", "A"), ("F", [-1, 0, 0, -1, 0, 0], "against", "F"), "decline"),
    # Roster 7 gives Dalton Kincaid 31.5. Roster 12 gives Kenyon Sadiq, with no row on the chart, so both start at C.
    # Points per game pick the highest-value player: Kincaid at 6.55 against Sadiq at 5.50.
    # Roster 7: the lineup changes by minus 1.05, no loss, and it gives Kincaid, no fit step. Middle. Each player
    # has one share down, so trend is mixed. Sadiq is healthy. Byes one and one, even. Playoff mean rank 17.67
    # got against 13.67 gave, a gap of exactly 4, against. Schedule against. Sum zero, C.
    # Roster 12: no lineup change, and it gets Kincaid, fit up. Middle. Trend mixed. Kincaid is Questionable,
    # which is not out. Schedule for. Sum plus one, C to B.
    # Roster 12 asked and grades B: accept.
    (("C", [0, 0, 0, 0, 0, 0], "against", "C"), ("C", [1, 0, 0, 0, 0, 0], "for", "B"), "accept"),
    # Roster 4 gives Omarion Hampton 68.5 and Tony Pollard 9.0, a sum of 77.5.
    # Roster 12 gives Jacory Croskey-Merritt 24.0 and David Montgomery 12.5, a sum of 36.5.
    # Roster 4: 36.5 over 77.5 is 0.471, F. Roster 12: 2.12, A. Omarion Hampton is the highest-value player.
    # Roster 4: Croskey-Merritt and David Montgomery are out with no return week, so they count as back in week 14
    # at 6.8 and 10.3 a game. The lineup changes by 0.14, about the same, no fit step. A seller that gives the
    # highest-value player with no lineup gain, no standing step. Gets shares up and down, so trend is mixed.
    # Croskey-Merritt is on IR with no return week, injury down. Byes two and two, even. Playoff mean rank 23.17
    # got against 10.67 gave, against. Schedule against. Sum minus one, F stays F.
    # Roster 12: the lineup changes by minus 0.59, no loss, and it gets Hampton, fit up. Middle. Trend mixed.
    # No injury step. Schedule for. Sum plus one, A stays A.
    # Roster 12 asked and grades A: accept.
    (("F", [0, 0, 0, -1, 0, 0], "against", "F"), ("A", [1, 0, 0, 0, 0, 0], "for", "A"), "accept"),
]


# A new hole moves these rows. Each waits for Brian's word before HAND_WORKED changes.
HOLE_MOVES = {
    0: "Roster 7 gets Breece Hall, so RB1 is a hole: he is out with no return week on file. Malik Nabers takes WR1 "
       "with his bye in week 8, and no bench player covers him. Fit +1 to 0, final D to F, still accept.",
    2: "Roster 6 gets Lamar Jackson, so QB is a hole: he is out with no return week on file. Pat Freiermuth leaves "
       "the bench for FLEX2, so no cover is left for the bye of Parker Washington in week 7. Fit 0 to -1, final "
       "stays F, still accept.",
    5: "Roster 4 gives Omarion Hampton and Tony Pollard, so David Montgomery takes RB2. He is out with no return week "
       "on file. Fit 0 to -1, final stays F, still accept.",
}


@pytest.mark.parametrize("index", [
    pytest.param(index, marks=pytest.mark.xfail(strict=True, reason=HOLE_MOVES[index])) if index in HOLE_MOVES
    else index for index in range(len(REAL_TRADES))])
def test_each_real_week_6_trade_grades_as_worked_by_hand(slow_snap, index):
    a, a_gives, b, b_gives, asker = REAL_TRADES[index]
    trade = _trade(a, a_gives, b, b_gives, asker=asker)
    result = grade(trade, _before_real_trade(slow_snap, index))
    side_a, side_b, choice = HAND_WORKED[index]
    for breakdown, (start, steps, lean, final) in zip(result, (side_a, side_b)):
        assert breakdown.start_letter == start
        assert [adjuster.step for adjuster in breakdown.adjusters] == steps
        assert _adjuster(breakdown, "schedule").lean == lean
        assert breakdown.final_letter == final
    assert verdict(trade, result).choice == choice


# The expected gap adjuster sits behind EXPECTED_ADJUSTER_ON, so these tests turn it on in the rubric.
@pytest.fixture
def expected_on(monkeypatch):
    monkeypatch.setattr(rubric, "ADJUSTERS", rubric_adjusters(expected_on=True))


def _with_expected(snap, players: dict[str, list[tuple[int, float, float]]]):
    """The snapshot with hand-set games for each player: the week, his league points, and his expected points."""
    weeks = dict(snap.stats.weeks)
    for pid, games in players.items():
        for week, actual, _ in games:
            past = weeks[week]
            line = {**(past.stats.get(pid) or {}), "gp": 1.0}
            weeks[week] = past.model_copy(
                update={"points": {**past.points, pid: actual}, "stats": {**past.stats, pid: line}})
    expected = ExpectedPoints(through_week=5, players={
        pid: [ExpectedGame(week=week, game_id=f"2026_{week:02d}_{pid}", expected=exp) for week, _, exp in games]
        for pid, games in players.items()})
    return snap.model_copy(update={"stats": snap.stats.model_copy(update={"weeks": weeks}), "expected": expected})


# Each game runs 4 points per game under or over expected.
UNDER = [(3, 10.0, 14.0), (4, 12.0, 16.0), (5, 8.0, 12.0)]
OVER = [(3, 14.0, 10.0), (4, 16.0, 12.0), (5, 12.0, 8.0)]


def test_expected_gap_steps_up_for_a_side_that_gets_a_player_under_expected(snap, expected_on):
    tenth, fifth = grade(_trade(10, [SAQUON], 5, [COOK]), _with_expected(snap, {COOK: UNDER}))
    gap = _adjuster(tenth, "expected gap")
    assert gap.step == 1
    assert "Cook: -4.00 points per game against expected, over weeks 3, 4 and 5." in gap.reason
    # Roster 5 gives Cook under expected, so it sells low.
    assert _adjuster(fifth, "expected gap").step == -1


def test_expected_gap_steps_up_for_a_side_that_gives_a_player_over_expected(snap, expected_on):
    tenth, fifth = grade(_trade(10, [SAQUON], 5, [COOK]), _with_expected(snap, {COOK: OVER}))
    assert _adjuster(fifth, "expected gap").step == 1
    # Roster 10 gets Cook over expected, so it buys high.
    assert _adjuster(tenth, "expected gap").step == -1


def test_expected_gap_under_on_the_gets_and_over_on_the_gives_steps_up_once(snap, expected_on):
    tenth, _ = grade(_trade(10, [SAQUON], 5, [COOK]), _with_expected(snap, {COOK: UNDER, SAQUON: OVER}))
    gap = _adjuster(tenth, "expected gap")
    assert gap.step == 1
    assert "Barkley: +4.00" in gap.reason and "Cook: -4.00" in gap.reason


def test_expected_gap_steps_down_for_a_side_that_gets_a_player_over_expected(snap, expected_on):
    tenth, _ = grade(_trade(10, [SAQUON], 5, [COOK]), _with_expected(snap, {COOK: OVER}))
    gap = _adjuster(tenth, "expected gap")
    assert gap.step == -1
    assert gap.reason.startswith("The players it gets run over their expected points, so their points can fall.")


def test_expected_gap_steps_down_for_a_side_that_gives_a_player_under_expected(snap, expected_on):
    _, fifth = grade(_trade(10, [SAQUON], 5, [COOK]), _with_expected(snap, {COOK: UNDER}))
    gap = _adjuster(fifth, "expected gap")
    assert gap.step == -1
    assert gap.reason.startswith("The players it gives run under their expected points, so their points can rise.")


def test_expected_gap_of_one_get_under_and_one_get_over_takes_no_step(snap, expected_on):
    tenth, _ = grade(_trade(10, [SAQUON], 5, [COOK, HUBBARD]), _with_expected(snap, {COOK: UNDER, HUBBARD: OVER}))
    gap = _adjuster(tenth, "expected gap")
    assert gap.step == 0
    assert gap.reason.startswith("The players it gets and the players it gives run near their expected points.")


def test_expected_gap_of_gets_under_and_gives_under_takes_no_step(snap, expected_on):
    tenth, _ = grade(_trade(10, [SAQUON], 5, [COOK]), _with_expected(snap, {COOK: UNDER, SAQUON: UNDER}))
    gap = _adjuster(tenth, "expected gap")
    assert gap.step == 0
    assert gap.reason.startswith(
        "The players it gets run under their expected points, so their points can rise. "
        "The players it gives run under their expected points, so their points can rise. "
        "The step up and the step down cancel.")


def test_expected_gap_of_a_handcuff_does_not_count(slow_snap, expected_on):
    snap = _with_expected(_ne_snap(slow_snap), {HENDERSON: UNDER})
    seventh, _ = grade(_trade(7, [CAR_DEF], 8, [HENDERSON]), snap)
    gap = _adjuster(seventh, "expected gap")
    assert gap.step == 0
    assert gap.reason.endswith("TreVeyon Henderson is a handcuff, so his gap does not count.")


def test_expected_gap_of_a_player_due_back_does_not_count(snap, expected_on):
    snap = _with_expected(_before_the_jacobs_trade(snap), {JACOBS: UNDER})
    eleventh, _ = grade(_trade(11, [TUTEN, WILSON], 12, [JACOBS, VELE]), snap)
    gap = _adjuster(eleventh, "expected gap")
    assert gap.step == 0
    assert gap.reason.endswith("Josh Jacobs is due back, so his gap does not count.")


def test_a_player_with_one_game_in_the_window_has_no_expected_gap(snap, expected_on):
    tenth, _ = grade(_trade(10, [SAQUON], 5, [COOK]), _with_expected(snap, {COOK: UNDER[-1:]}))
    gap = _adjuster(tenth, "expected gap")
    assert gap.step == 0
    # Barkley has no rows in the expected file, so he has no gap either, and the reason names him too.
    assert gap.reason.endswith(
        "James Cook and Saquon Barkley have fewer than 2 games in the expected window, so they have no gap.")


def test_expected_gap_reason_gives_the_players_it_gets_before_the_players_it_gives(snap, expected_on):
    tenth, fifth = grade(_trade(10, [SAQUON], 5, [COOK]), _with_expected(snap, {COOK: UNDER, SAQUON: OVER}))
    tenth_gap, fifth_gap = _adjuster(tenth, "expected gap"), _adjuster(fifth, "expected gap")
    assert tenth_gap.reason.index("Cook: -4.00") < tenth_gap.reason.index("Barkley: +4.00")
    assert fifth_gap.reason.index("Barkley: +4.00") < fifth_gap.reason.index("Cook: -4.00")


def test_expected_gap_without_the_expected_points_says_no_check_ran(snap, expected_on):
    tenth, _ = grade(_trade(10, [SAQUON], 5, [COOK]), snap)
    gap = _adjuster(tenth, "expected gap")
    assert (gap.step, gap.reason) == (0, "The expected points are not available, so no gap check ran.")


def test_with_the_tunable_off_no_breakdown_holds_the_expected_gap(snap):
    for side in grade(_trade(10, [SAQUON], 5, [COOK]), _with_expected(snap, {COOK: UNDER})):
        assert "expected gap" not in [a.name for a in side.adjusters]


# The lineup value of a player due back. Jacobs has no games in weeks 2 to 5, and the returns file has him back in
# week 7. Wicks sits on roster 3's bench, so a trade of Wicks for Jacobs moves only the value of Jacobs.
def _with_projections(snap, projections: dict[str, dict[int, float]] | None):
    return snap.model_copy(update={"projections_ahead": projections})


def test_a_side_that_gets_a_player_due_back_gains_by_his_projection_and_the_reason_names_it(snap):
    snap = _with_projections(snap, {JACOBS: {week: 18.0 for week in range(7, 15)}})
    third, eleventh = grade(_trade(3, [WICKS], 11, [JACOBS]), snap)
    fit = _adjuster(third, "roster fit")
    # Jacobs takes RB2 and is due back in week 7, inside the bye window. Roster 3 has no bench back above the line to
    # cover him, so his slot is a new hole, and the gain and the hole cancel to no step.
    assert fit.step == 0
    assert fit.reason == (
        "The best lineup gains after the trade. RB2 is a hole after the trade: Josh Jacobs is due back in week 7, "
        "and no bench player covers him." + NO_SCHEDULES + " Josh Jacobs is due back in week 7, so he counts for his "
        "projection ahead of 18.0 a game.")
    assert _adjuster(eleventh, "roster fit").step == -1


def test_a_contender_whose_lineup_gain_comes_from_a_player_due_back_names_him_and_his_return_week(snap):
    # Roster 3 holds a playoff spot. Jacobs does not play this week, so the gain comes after his return.
    snap = _with_projections(snap, {JACOBS: {week: 18.0 for week in range(9, 15)}})
    third, _ = grade(_trade(3, [WICKS], 11, [JACOBS]), snap.model_copy(update={"returns": {JACOBS: 9}}))
    standing = _adjuster(third, "standing")
    assert standing.step == 1
    assert standing.reason == (
        "The team holds a playoff spot, and the best lineup gains after Josh Jacobs returns in week 9.")


# Shakir sits on roster 3's bench. A.J. Brown and Jonathan Taylor are on roster 11.
SHAKIR, AJ_BROWN, J_TAYLOR = "8134", "5859", "6813"


def test_a_contender_whose_lineup_gain_comes_from_two_players_due_back_names_both_and_the_latest_week(snap):
    # Both start on roster 3 after the trade, so the gain comes after the later return, in week 10.
    snap = _with_projections(snap, {JACOBS: {week: 18.0 for week in range(9, 15)},
                                    AJ_BROWN: {week: 20.0 for week in range(10, 15)}})
    third, _ = grade(_trade(3, [WICKS, SHAKIR], 11, [JACOBS, AJ_BROWN]),
                     snap.model_copy(update={"returns": {JACOBS: 9, AJ_BROWN: 10}}))
    standing = _adjuster(third, "standing")
    assert standing.step == 1
    assert standing.reason == (
        "The team holds a playoff spot, and the best lineup gains after Josh Jacobs and A.J. Brown return in week 10.")


def test_a_contender_whose_player_due_back_sits_on_the_bench_gains_now(snap):
    # Taylor takes an RB spot on roster 3 now. Jacobs projects 1.0 a game, so he sits on the bench.
    snap = _with_projections(snap, {JACOBS: {9: 1.0}})
    third, _ = grade(_trade(3, [WICKS, SHAKIR], 11, [JACOBS, J_TAYLOR]),
                     snap.model_copy(update={"returns": {JACOBS: 9}}))
    standing = _adjuster(third, "standing")
    assert standing.step == 1
    assert standing.reason == "The team holds a playoff spot, and the best lineup gains now."


def test_a_player_not_due_back_keeps_his_recent_points_whatever_his_projection(snap):
    # Saquon Barkley is Out with no return week, so he would count as due back. Healthy, neither player is.
    # Judkins is healthy too. With no projections, he counts by his recent points and takes a flex spot. Out with no
    # return week, that slot would be a hole in one case and not the other.
    snap = _with_status(_with_status(snap, SAQUON, None), JUDKINS, None)
    today = grade(_trade(10, [SAQUON], 5, [COOK]), _with_projections(snap, None))
    projected = grade(_trade(10, [SAQUON], 5, [COOK]), _with_projections(snap, {COOK: {7: 0.0}, SAQUON: {7: 99.0}}))
    assert projected == today


def test_a_player_due_back_with_no_projection_row_counts_as_0(snap):
    snap = _with_projections(snap, {COOK: {7: 18.0}})
    third, _ = grade(_trade(3, [WICKS], 11, [JACOBS]), snap)
    fit = _adjuster(third, "roster fit")
    assert fit.reason.startswith("The best lineup stays about the same.")
    assert fit.reason.endswith(
        "Josh Jacobs is due back in week 7, so he counts for his projection ahead of 0.0 a game.")


def test_without_the_projections_every_grade_is_as_by_recent_points_and_the_reason_says_so(snap):
    missing = _with_projections(snap, None)
    third, eleventh = grade(_trade(3, [WICKS], 11, [JACOBS]), missing)
    # With no return week and a healthy status, Jacobs is not due back, so the grade uses his recent points of 0.
    healthy = _with_status(missing.model_copy(update={"returns": {}}), JACOBS, None)
    by_recent = grade(_trade(3, [WICKS], 11, [JACOBS]), healthy)
    for side, today in zip((third, eleventh), by_recent):
        assert _adjuster(side, "roster fit").step == _adjuster(today, "roster fit").step
        assert _adjuster(side, "roster fit").reason == (
            _adjuster(today, "roster fit").reason
            + " The projections ahead are not available, so Josh Jacobs counts for his recent points per game.")
    # A trade with no player due back says nothing of the projections. Saquon Barkley is healthy here.
    for side in grade(_trade(10, [SAQUON], 5, [COOK]), _with_status(missing, SAQUON, None)):
        assert "projections" not in _adjuster(side, "roster fit").reason


def test_the_projection_skips_the_bye_and_stops_at_the_last_regular_week(snap):
    # Week 11 is before his return, week 13 is his bye, and week 15 is after the last regular week.
    snap = _with_projections(snap, {JACOBS: {11: 99.0, 12: 16.0, 14: 20.0, 15: 99.0}})
    third, _ = grade(_trade(3, [WICKS], 11, [JACOBS]), snap.model_copy(update={"returns": {JACOBS: 12}}))
    assert _adjuster(third, "roster fit").reason.endswith(
        "Josh Jacobs is due back in week 12, so he counts for his projection ahead of 18.0 a game.")


def test_a_return_after_the_last_regular_week_gives_0(snap):
    snap = _with_projections(snap, {JACOBS: {15: 99.0, 16: 99.0}})
    third, _ = grade(_trade(3, [WICKS], 11, [JACOBS]), snap.model_copy(update={"returns": {JACOBS: 15}}))
    assert _adjuster(third, "roster fit").reason.endswith(
        "Josh Jacobs is due back in week 15, so he counts for his projection ahead of 0.0 a game.")


def test_a_player_due_back_in_the_trade_week_counts_for_that_week(snap):
    snap = _with_projections(snap, {JACOBS: {6: 24.0, 7: 12.0}})
    third, _ = grade(_trade(3, [WICKS], 11, [JACOBS]), snap.model_copy(update={"returns": {JACOBS: 6}}))
    assert _adjuster(third, "roster fit").reason.endswith(
        "Josh Jacobs is due back in week 6, so he counts for his projection ahead of 18.0 a game.")


# Saquon Barkley on roster 10 is Out and has no row in the returns file, so he counts as due back in week 14.
# Sleeper projects 0 for the weeks he is out, so the rows before week 14 never count.
SAQUON_AHEAD = {**{week: 0.0 for week in range(6, 14)}, 14: 20.0}


def test_a_player_out_with_no_return_week_counts_for_his_projection_ahead_from_week_14(snap):
    snap = _with_projections(snap, {SAQUON: SAQUON_AHEAD})
    assert lineup_value(snap, SAQUON) == 20
    third, _ = grade(_trade(3, [WICKS], 10, [SAQUON]), snap)
    assert _adjuster(third, "roster fit").reason.endswith(
        "Saquon Barkley has no return week on file, so he counts as back in week 14 "
        "for his projection ahead of 20.0 a game.")
    # The injury adjuster still docks one step for out with no near return.
    assert _adjuster(third, "injury").step == -1
    assert _adjuster(third, "injury").reason == "Saquon Barkley is out with no near return."


def test_a_contender_whose_lineup_gain_comes_from_a_player_out_with_no_return_week_says_he_counts_as_back(snap):
    # Roster 3 holds a playoff spot. Saquon Barkley starts there at 20.0 a game, but only from week 14.
    third, _ = grade(_trade(3, [WICKS], 10, [SAQUON]), _with_projections(snap, {SAQUON: SAQUON_AHEAD}))
    standing = _adjuster(third, "standing")
    assert standing.step == 1
    assert standing.reason == (
        "The team holds a playoff spot, and the best lineup gains from week 14, when Saquon Barkley counts as back.")


def test_a_player_out_with_a_return_week_counts_from_that_week(snap):
    # Week 14 holds 40.0, so the mean from week 9 differs from the mean from week 14.
    snap = _with_projections(snap, {SAQUON: {**SAQUON_AHEAD, **{week: 16.0 for week in range(9, 14)}, 14: 40.0}})
    snap = snap.model_copy(update={"returns": {**snap.returns, SAQUON: 9}})
    assert lineup_value(snap, SAQUON) == 20
    third, _ = grade(_trade(3, [WICKS], 10, [SAQUON]), snap)
    assert _adjuster(third, "roster fit").reason.endswith(
        "Saquon Barkley is due back in week 9, so he counts for his projection ahead of 20.0 a game.")


def test_a_questionable_player_keeps_his_recent_points_whatever_his_projection(snap):
    # Wicks is Questionable, which is not out.
    snap = _with_projections(snap, {WICKS: {week: 30.0 for week in range(6, 15)}})
    assert lineup_value(snap, WICKS) == recent_points_per_game(snap, WICKS)


def test_without_the_projections_a_player_out_with_no_return_week_keeps_his_recent_points(snap):
    snap = _with_projections(snap, None)
    assert lineup_value(snap, SAQUON) == recent_points_per_game(snap, SAQUON)
    third, _ = grade(_trade(3, [WICKS], 10, [SAQUON]), snap)
    assert _adjuster(third, "roster fit").reason.endswith(
        "The projections ahead are not available, so Saquon Barkley counts for his recent points per game.")


# Stefon Diggs on roster 3 scores 10.17 a game over weeks 2 to 5. Jacobs is due back in week 7 with no recent games.
DIGGS = "2449"


def test_with_no_chart_a_player_due_back_is_the_highest_value_player_by_his_projection(snap):
    snap = _with_projections(snap, {JACOBS: {week: 18.0 for week in range(7, 15)}})
    no_chart = snap.model_copy(update={"chart": None})
    assert rubric._highest_value_player(_trade(3, [DIGGS], 11, [JACOBS]), no_chart, []) == JACOBS


def test_with_a_chart_that_lists_every_player_trade_value_picks_the_highest_value_player(snap):
    # Jacobs projects to 18 a game, but the chart values Diggs above him, so the chart decides.
    snap = _with_values(_with_projections(snap, {JACOBS: {week: 18.0 for week in range(7, 15)}}),
                        {DIGGS: 20.0, JACOBS: 5.0})
    assert rubric._highest_value_player(_trade(3, [DIGGS], 11, [JACOBS]), snap, []) == DIGGS


# Jameson Williams on roster 4 scores 10.53 a game. Roster 4 is last, out of the playoff race.
J_WILLIAMS = "8148"


def test_with_no_chart_a_seller_that_gets_a_player_due_back_gets_the_highest_value_player(snap):
    snap = _with_projections(snap, {JACOBS: {week: 18.0 for week in range(7, 15)}}).model_copy(update={"chart": None})
    fourth, _ = grade(_trade(4, [J_WILLIAMS], 11, [JACOBS]), snap)
    standing = _adjuster(fourth, "standing")
    assert standing.step == 1
    assert standing.reason == "The team is out of the playoff race, and it gets the highest-value player in the trade."


def test_with_no_chart_a_handcuff_due_back_is_never_the_highest_value_player(slow_snap):
    # Mitchell backs up Hampton on roster 12, so he is a handcuff there. His projection of 30 does not count.
    snap = _with_projections(_lac_snap(slow_snap), {MITCHELL: {week: 30.0 for week in range(7, 15)}})
    snap = snap.model_copy(update={"chart": None, "returns": {**snap.returns, MITCHELL: 7}})
    trade = _trade(12, [POLLARD], 11, [MITCHELL])
    handcuffs = rubric.trade_handcuffs(trade, snap)
    assert handcuffs == [MITCHELL]
    assert rubric._highest_value_player(trade, snap, handcuffs) == POLLARD


# Odunze plays for the Bears, whose week 6 game at the Falcons kicks off at 1 pm Eastern on Sunday 2026-10-18.
# Watson plays for the Packers, whose game has no kickoff here, so it counts as final.
CHI_ATL_KICKOFF = datetime(2026, 10, 18, 13, 0, tzinfo=ZoneInfo("America/New_York"))
CHI_ATL = SlowSources(kickoffs={"CHI": CHI_ATL_KICKOFF, "ATL": CHI_ATL_KICKOFF})


def _chi_atl_snap(fixture_raw_dir, fixture_history_root, chart_week6, hours: int):
    """The week 6 snapshot with the clock `hours` after the kickoff of the Bears at the Falcons."""
    return _known_games_snap(fixture_raw_dir, fixture_history_root, chart_week6, slow=CHI_ATL,
                             now=CHI_ATL_KICKOFF + timedelta(hours=hours))


def test_the_trend_reason_of_a_player_whose_known_game_is_in_progress_ends_with_the_label(
        fixture_raw_dir, fixture_history_root, chart_week6):
    snap = _chi_atl_snap(fixture_raw_dir, fixture_history_root, chart_week6, 2)
    first, _ = grade(_trade(1, [WATSON], 4, [ODUNZE]), snap)
    trend = _adjuster(first, TREND)
    assert "Odunze: snap share 97%, up, over weeks 5 and 6, game in progress." in trend.reason
    assert "Watson: snap share 85%, up, over weeks 5 and 6." in trend.reason


def test_the_label_reads_the_team_on_the_week_n_stat_row_before_the_sleeper_team(
        fixture_raw_dir, fixture_history_root, chart_week6):
    # Sleeper now lists Odunze on the Packers, but his week 6 stat row is with the Bears, whose game is on.
    snap = _chi_atl_snap(fixture_raw_dir, fixture_history_root, chart_week6, 2)
    moved = snap.players[ODUNZE].model_copy(update={"nfl_team": "GB"})
    snap = snap.model_copy(update={"players": {**snap.players, ODUNZE: moved}})
    assert snap.stats.weeks[6].nfl_teams[ODUNZE] == "CHI"
    first, _ = grade(_trade(1, [WATSON], 4, [ODUNZE]), snap)
    assert "Odunze: snap share 97%, up, over weeks 5 and 6, game in progress." in _adjuster(first, TREND).reason


def test_the_hole_reason_of_a_player_whose_known_game_is_in_progress_ends_with_the_label(
        fixture_raw_dir, fixture_history_root, chart_week6):
    # Roster 6 gives Freiermuth, Malik Washington, and Corum for Odunze, who takes FLEX2 at WR61.
    trade = _trade(6, [FREIERMUTH, M_WASHINGTON, CORUM], 4, [ODUNZE])
    on, _ = grade(trade, _chi_atl_snap(fixture_raw_dir, fixture_history_root, chart_week6, 2))
    off, _ = grade(trade, _chi_atl_snap(fixture_raw_dir, fixture_history_root, chart_week6, 5))
    assert _adjuster(on, "roster fit").reason == (
        "FLEX2 is a hole after the trade: Rome Odunze is WR61, game in progress." + NO_SCHEDULES)
    assert _adjuster(off, "roster fit").reason == "FLEX2 is a hole after the trade: Rome Odunze is WR61." + NO_SCHEDULES


def test_the_adjuster_steps_are_the_same_with_the_label_on_and_off(fixture_raw_dir, fixture_history_root, chart_week6):
    on = _chi_atl_snap(fixture_raw_dir, fixture_history_root, chart_week6, 2)
    off = _chi_atl_snap(fixture_raw_dir, fixture_history_root, chart_week6, 5)
    assert on.as_of.known_games.in_progress == 1 and off.as_of.known_games.in_progress == 0
    trade = _trade(1, [WATSON], 4, [ODUNZE])
    for labeled, plain in zip(grade(trade, on), grade(trade, off)):
        assert [a.step for a in labeled.adjusters] == [a.step for a in plain.adjusters]
        assert labeled.final_letter == plain.final_letter
        # The label is the only change to the reasons.
        assert [a.reason.replace(", game in progress", "") for a in labeled.adjusters] == [
            a.reason for a in plain.adjusters]


def test_no_reason_and_no_stamp_of_a_game_in_progress_says_live_partial_or_current_week(
        fixture_raw_dir, fixture_history_root, chart_week6):
    snap = _chi_atl_snap(fixture_raw_dir, fixture_history_root, chart_week6, 2)
    breakdowns = grade(_trade(1, [WATSON], 4, [ODUNZE]), snap)
    texts = [_breakdown_text(breakdowns), snap.as_of.model_dump_json()]
    for text in texts:
        for word in ("live", "partial", "current week"):
            assert not re.search(rf"\b{word}\b", text, re.IGNORECASE)


def test_the_prose_checks_of_the_analysis_pass_on_a_reason_with_the_label(
        fixture_raw_dir, fixture_history_root, chart_week6):
    snap = _chi_atl_snap(fixture_raw_dir, fixture_history_root, chart_week6, 2)
    breakdowns = grade(_trade(1, [WATSON], 4, [ODUNZE]), snap)
    breakdown_text = _breakdown_text(breakdowns)
    assert "game in progress" in breakdown_text
    names = [*(t.name for t in snap.teams.values()), *(p.name for p in snap.players.values())]
    allowed = _allowed({}, [], breakdown_text)
    trend = _adjuster(breakdowns[0], TREND).reason
    # The analysis can echo the label as a phrase joined by a comma.
    prose = "Rome Odunze's snap share of 97% is up over weeks 5 and 6, game in progress."
    for text in (trend, prose):
        assert _prose_failures("roster 1 analysis", text, allowed, breakdown_text, names) == []
        assert _letter_failures("roster 1 analysis", text) == []
