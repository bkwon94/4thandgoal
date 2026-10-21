"""
Tests for the grade of a proposed trade: the start letter, consolidation, and unlisted rules.
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
            assert set(side.model_dump()) == {"roster_id", "start_letter", "reason"}
            assert not re.search(r"\d", side.reason)
            assert not re.search(r"ratio|sum|peaked|chart", side.reason, re.IGNORECASE)
