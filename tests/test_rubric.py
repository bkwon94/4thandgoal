"""
Tests for the grade of a proposed trade: the start letter, consolidation, unlisted, fit, and standing rules.
They feed a proposed trade and the week 6 snapshot at the grade seam.
"""
import re

import pytest

from cornerstone.rubric import ProposedTrade, TradeInputError, TradeSide, grade
from cornerstone.snapshot import load_snapshot

# Week 6 trade values from the fixture: Collins 46.5 and Croskey-Merritt 24.0 on roster 4,
# McCaffrey 64.0 on roster 3, Kincaid 31.5 and Wilson 27.5 on roster 12,
# Harrison 36.0, Brian Robinson 22.0, and Bijan Robinson 20.5 on roster 7.
COLLINS, CROSKEY, MCCAFFREY = "7569", "12533", "4034"
KINCAID, WILSON = "10236", "8146"
HARRISON, B_ROBINSON, BIJAN = "11628", "8154", "9509"


@pytest.fixture
def snap(fixture_raw_dir, fixture_history_root, chart_week6):
    return load_snapshot(fixture_raw_dir, fixture_history_root, chart_week6)


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
                assert not re.search(r"ratio|sum|peaked|chart", reason, re.IGNORECASE)


# Points per game over weeks 3 to 6, the last four completed weeks of the week 6 snapshot.
# Roster 10, in the middle at 6-6: Saquon Barkley 4.50 on the bench, Monangai 15.30 and Judkins 11.33 at RB,
# Egbuka 9.88 at the last flex spot.
# Roster 5, a contender: James Cook 19.70, Hubbard 19.00, and Javonte Williams 17.57 at RB and flex,
# Michael Wilson 10.97 at the last flex spot, Metcalf 10.55 and Woody Marks 9.10 on the bench.
SAQUON, COOK, HUBBARD, MARKS = "4866", "8138", "7594", "12474"


def _adjuster(breakdown, name: str):
    return next(a for a in breakdown.adjusters if a.name == name)


def test_fit_steps_up_for_a_lineup_gain_and_down_for_a_lineup_loss(snap):
    # Cook takes Egbuka's flex spot on roster 10, a gain of 9.82. Roster 5 loses Cook for Metcalf, a loss of 9.15.
    tenth, fifth = grade(_trade(10, [SAQUON], 5, [COOK]), snap)
    assert _adjuster(tenth, "roster fit").step == 1
    assert _adjuster(tenth, "roster fit").reason == "The best lineup gains after the trade."
    assert _adjuster(fifth, "roster fit").step == -1
    assert _adjuster(fifth, "roster fit").reason == "The best lineup loses after the trade."


# Roster 12: Tony Pollard 9.10 sits behind St. Brown 9.77 at the last flex spot.
POLLARD = "5967"


def test_fit_steps_up_for_the_best_player_in_the_trade_with_no_lineup_loss(snap):
    # Both players sit on the bench after the trade, so neither lineup changes.
    snap = _with_values(snap, {SAQUON: 30.0})
    tenth, twelfth = grade(_trade(10, [SAQUON], 12, [POLLARD]), snap)
    assert _adjuster(twelfth, "roster fit").step == 1
    assert _adjuster(twelfth, "roster fit").reason == (
        "It gets the best player in the trade, and the best lineup does not lose.")
    assert _adjuster(tenth, "roster fit").step == 0


def test_an_unlisted_player_makes_points_per_game_pick_the_best_player_in_the_trade(snap):
    # Saquon Barkley has no trade value. Pollard has more points per game, so roster 10 gets the best player.
    tenth, twelfth = grade(_trade(10, [SAQUON], 12, [POLLARD]), snap)
    assert _adjuster(tenth, "roster fit").step == 1
    assert _adjuster(twelfth, "roster fit").step == 0


def test_fit_holds_at_one_step_when_the_gain_is_large_and_the_side_gets_the_best_player(snap):
    # Cook and Hubbard take both RB spots on roster 10, and Monangai and Judkins move to flex, a gain of 18.36.
    # Cook is also the best player in the trade by points per game.
    tenth, _ = grade(_trade(10, [SAQUON], 5, [COOK, HUBBARD]), snap)
    assert _adjuster(tenth, "roster fit").step == 1


def test_the_side_that_gets_the_depth_steps_up_only_when_every_player_it_gets_starts(snap):
    # Cook starts on roster 10, but Woody Marks at 9.10 sits behind Egbuka at 9.88 on the bench.
    tenth, _ = grade(_trade(10, [SAQUON], 5, [COOK, MARKS]), snap)
    assert _adjuster(tenth, "roster fit").step == 0
    assert _adjuster(tenth, "roster fit").reason == (
        "The best lineup gains after the trade, but not every player it gets starts.")


# Week 6 standings: rosters 3, 5, 6, 9, 2, and 1 hold the six playoff spots, and roster 1 has 6 wins.
# Roster 4 has 1 win, more than two games out, so it is a seller. Rosters 7, 8, 10, 11, and 12 are in the middle.
WICKS, JACOBS = "9486", "5850"


def test_a_team_in_the_middle_gets_no_standing_step(snap):
    tenth, _ = grade(_trade(10, [SAQUON], 5, [COOK]), snap)
    standing = _adjuster(tenth, "standing")
    assert standing.step == 0
    assert standing.reason == "The team is neither in a playoff spot nor out of the race."


def test_a_contender_steps_up_for_a_lineup_gain_now(snap):
    # Cook takes an RB spot on roster 3, and Henry moves to flex for Meyers.
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
    # Roster 3 loses McCaffrey at RB, and Diggs at 8.23 takes the last flex spot, a loss of 10.79.
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


def test_a_seller_steps_up_when_it_gets_the_best_player_in_the_trade(snap):
    # McCaffrey at 64.0 is worth more than Collins at 46.5.
    fourth, _ = grade(_trade(4, [COLLINS], 3, [MCCAFFREY]), snap)
    standing = _adjuster(fourth, "standing")
    assert standing.step == 1
    assert standing.reason == "The team is out of the playoff race, and it gets the best player in the trade."


def test_a_seller_steps_down_when_it_gives_the_best_player_for_a_lineup_gain_now(snap):
    # Cook at 19.70 takes an RB spot on roster 4 for Collins at 14.93, a gain of 5.52.
    snap = _with_values(snap, {COOK: 20.0})
    fourth, _ = grade(_trade(4, [COLLINS], 5, [COOK]), snap)
    standing = _adjuster(fourth, "standing")
    assert standing.step == -1
    assert standing.reason == (
        "The team is out of the playoff race, but it gives the best player in the trade for a lineup gain now.")


def test_the_adjusters_show_in_rubric_order(snap):
    for side in grade(_trade(10, [SAQUON], 5, [COOK]), snap):
        assert [a.name for a in side.adjusters] == ["roster fit", "standing"]


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
    """The snapshot with the roster moved to the sixth playoff spot, at the record of the team it moves past."""
    ranked = sorted(snap.standings, key=lambda s: s.rank)
    team = next(s for s in ranked if s.roster_id == roster_id)
    sixth = ranked[5]
    others = [s for s in ranked if s.roster_id != roster_id]
    moved = team.model_copy(update={"wins": sixth.wins, "losses": sixth.losses, "points_for": sixth.points_for + 1})
    order = others[:5] + [moved] + others[5:]
    return snap.model_copy(update={"standings": [s.model_copy(update={"rank": i + 1}) for i, s in enumerate(order)]})


def test_the_jacobs_trade_as_a_contender_bet_on_jacobs_back_in_week_7_gets_the_standing_step_up(snap):
    # Roster 11 was 4-8 and tenth in week 6, so this case moves it into the sixth playoff spot to test the bet.
    snap = _as_contender(_before_the_jacobs_trade(snap), 11)
    eleventh, _ = grade(_trade(11, [TUTEN, WILSON], 12, [JACOBS, VELE]), snap)
    standing = _adjuster(eleventh, "standing")
    assert standing.step == 1
    assert "Josh Jacobs is due back before the playoffs" in standing.reason


def test_the_jacobs_trade_never_steps_the_side_that_got_jacobs_down_for_standing(snap):
    # With the real week 6 standings, roster 11 is in the middle, two games out of the last spot.
    eleventh, _ = grade(_trade(11, [TUTEN, WILSON], 12, [JACOBS, VELE]), _before_the_jacobs_trade(snap))
    assert _adjuster(eleventh, "standing").step == 0
