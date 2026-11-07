"""
Tests for the count of the letters of a roster in an egg word, which the rules, the drop, and the routes share.
The claims are plain Claim values, newest first, as the store lists them.
"""
from eggs.letters import drop_letters
from eggs.rules import letters_of, winner
from eggs.store import Claim


def _claim(egg_id: int, letter: str, roster_id: int, word: str | None) -> Claim:
    return Claim(egg_id=egg_id, letter=letter, roster_id=roster_id, word=word, claimed_at=f"2026-11-10T09:0{egg_id}")


# Newest first: the roster 3 claimed L, then a block of A, then E into EAGLES, then A into LANSDALE.
CLAIMS = [_claim(4, "A", 3, "LANSDALE"), _claim(3, "E", 3, "EAGLES"), _claim(2, "A", 3, None), _claim(1, "L", 3, "LANSDALE")]


def test_the_letters_of_a_roster_in_a_word_come_oldest_first_and_count_no_block():
    assert letters_of(CLAIMS, 3, "LANSDALE") == ["L", "A"]
    assert letters_of(CLAIMS, 3, "EAGLES") == ["E"]
    assert letters_of(CLAIMS, 12, "LANSDALE") == []


def test_the_drop_gives_no_letter_to_a_word_that_has_a_winner():
    claims = [_claim(index, letter, 3, "EAGLES") for index, letter in enumerate("EAGLES")]
    assert winner(claims, "EAGLES") == 3
    # G sits only in EAGLES, so with EAGLES won, no manager needs a G.
    assert "G" not in drop_letters(["CORNERSTONE", "LANSDALE", "EAGLES"], [3, 12], claims, 6)
