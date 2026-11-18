"""
Property tests of the pure functions of the roster grade: the score, the letter, the depth word, the league scale,
and the ranks of the rosters and of the positions. Hypothesis draws the inputs, so edge cases get tested too.
"""
import random

from hypothesis import given, settings
from hypothesis import strategies as st

from managers.grade import (
    SLOT_POSITIONS,
    GradeParts,
    _against_league,
    _ranks,
    depth_word,
    grade_letter,
    grade_score,
    position_ranks,
)
from managers.tunables import GRADE_WEIGHTS

unit = st.floats(min_value=0.0, max_value=1.0)
# A whole score is a likely edge of a band, so the draw mixes whole scores with any float.
scores = st.one_of(st.integers(min_value=0, max_value=100).map(float), st.floats(min_value=0.0, max_value=100.0))
totals = st.dictionaries(st.integers(min_value=1, max_value=12), st.integers(min_value=-1000, max_value=1000),
                         min_size=1, max_size=12)


def test_the_weights_sum_to_100():
    assert sum(GRADE_WEIGHTS.values()) == 100


@given(unit, unit, unit, unit)
def test_the_score_stays_in_0_to_100_when_each_part_is_in_0_to_1(projection, production, trade_value, depth):
    score = grade_score(GradeParts(projection, production, trade_value, depth))
    assert 0 <= score <= 100


# A band edge sits on a whole score, so one step of 1 from a whole score reaches each edge from below. There are only
# 100 whole scores, so 500 examples cover each of them.
@settings(max_examples=500)
@given(scores, st.one_of(st.just(1.0), st.floats(min_value=0.0, max_value=100.0)))
def test_the_letter_never_gets_worse_as_the_score_goes_up(low, step):
    high = min(100.0, low + step)
    order = "DCBA"
    assert order.index(grade_letter(low)) <= order.index(grade_letter(high)), (
        f"score {low} gives {grade_letter(low)} and score {high} gives {grade_letter(high)}")


@given(scores)
def test_the_letter_is_a_b_c_or_d(score):
    assert grade_letter(score) in {"A", "B", "C", "D"}


@given(st.integers(min_value=0, max_value=50))
def test_a_position_with_a_hole_reads_thin_with_any_spares(spares):
    assert depth_word(spares, hole=True) == "thin"


@given(totals)
def test_the_scale_against_the_league_runs_0_to_1_and_ignores_a_shift(values):
    scaled = _against_league({rid: float(total) for rid, total in values.items()})
    assert all(0 <= part <= 1 for part in scaled.values())
    if len(set(values.values())) > 1:
        assert scaled[min(values, key=lambda rid: values[rid])] == 0
        assert scaled[max(values, key=lambda rid: values[rid])] == 1
    shifted = _against_league({rid: float(total + 500) for rid, total in values.items()})
    assert shifted == scaled


@given(totals)
def test_the_ranks_of_the_rosters_run_1_to_n_with_no_tie_and_no_gap(values):
    ranks = _ranks({rid: float(total) for rid, total in values.items()})
    assert sorted(ranks.values()) == list(range(1, len(values) + 1))


players = st.dictionaries(st.text(alphabet="abcdefgh0123456789", min_size=1, max_size=4),
                          st.tuples(st.floats(min_value=0.0, max_value=500.0), st.sampled_from([*SLOT_POSITIONS, "K"])),
                          max_size=30)


@given(players, st.randoms(use_true_random=False))
def test_the_ranks_at_each_position_run_1_to_n_and_ignore_the_order_of_the_input(drawn, shuffler: random.Random):
    values = {pid: value for pid, (value, _) in drawn.items()}
    positions = {pid: position for pid, (_, position) in drawn.items()}
    ranks = position_ranks(values, positions)
    for position in SLOT_POSITIONS:
        places = sorted(place for pid, place in ranks.items() if positions[pid] == position)
        assert places == list(range(1, len(places) + 1))
    order = list(values)
    shuffler.shuffle(order)
    assert position_ranks({pid: values[pid] for pid in order}, positions) == ranks
