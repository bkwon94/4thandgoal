"""
Unit tests for the number helpers in `league.numbers`.
Each case pins the rounding or the wording that the golden pages rely on.
"""
from league.numbers import count_noun, one_decimal, one_decimal_text, ordinal, plural, r2, round_half_up


def test_r2_rounds_half_up_where_python_rounds_half_even():
    assert r2(2.785) == 2.79


def test_round_half_up_takes_a_count_of_places():
    assert round_half_up(2.5) == 3.0
    assert round_half_up(0.25, 1) == 0.3


def test_one_decimal_rounds_half_up():
    assert one_decimal(118.75) == 118.8


def test_one_decimal_text_keeps_the_trailing_zero():
    assert one_decimal_text(4.0) == "4.0"
    assert one_decimal_text(118.75) == "118.8"


def test_ordinal_spells_the_suffix_and_the_teens():
    spelled = [ordinal(n) for n in (1, 2, 3, 4, 11, 12, 13, 21)]
    assert spelled == ["1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "21st"]


def test_plural_picks_the_word_for_the_count():
    assert plural(1, "carry", "carries") == "carry"
    assert plural(2, "carry", "carries") == "carries"


def test_count_noun_gives_the_count_and_the_word():
    assert count_noun(1, "roster") == "1 roster"
    assert count_noun(0, "roster") == "0 rosters"
