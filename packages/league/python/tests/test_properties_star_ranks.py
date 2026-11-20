"""
Property test of the star ranks of a league: no count is negative, and a position with no slot has no entry.
Hypothesis draws the team count and the roster slots.
"""
from hypothesis import given
from hypothesis import strategies as st

from league.league_settings import KNOWN_SLOTS, RANKED_POSITIONS, star_ranks

slots = st.lists(st.sampled_from(sorted(KNOWN_SLOTS)), max_size=12).map(tuple)


@given(st.integers(min_value=1, max_value=32), slots)
def test_a_star_count_is_never_negative_and_a_position_with_no_slot_is_absent(team_count, roster_slots):
    ranks = star_ranks(team_count, roster_slots)
    assert all(count >= 0 for count in ranks.values())
    assert set(ranks) == {position for position in RANKED_POSITIONS if position in roster_slots}
