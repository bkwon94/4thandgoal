"""
The letter rule of the egg drop: each egg gets the letter that the most managers still need over the open egg words.
A tie goes to the earlier letter, no letter repeats in one drop, and the guard keeps the last letter of each leader.
"""
from collections import Counter
from collections.abc import Iterable

from eggs.rules import letters_of, winner
from eggs.store import Claim


def drop_letters(words: Iterable[str], managers: Iterable[int], claims: Iterable[Claim], count: int) -> list[str]:
    """The letters of at most `count` eggs of one drop, in the order of the eggs. No letter repeats in one drop, so
    with fewer letters to pick than `count`, the list is shorter than `count`.

    `words` are the egg words, `managers` the roster ids of the managers who hunt, and `claims` each claim that holds.
    """
    words = list(words)
    claims = list(claims)
    managers = list(managers)
    # An egg word with a winner takes no more letters.
    open_words = [word for word in words if winner(claims, word) is None]
    need: Counter[str] = Counter()
    guarded: set[str] = set()
    for roster in managers:
        needs = [_needs(word, Counter(letters_of(claims, roster, word))) for word in open_words]
        need.update(set().union(*needs))
        # A manager who needs one letter more leads the egg word, so one egg of that letter would end the race.
        guarded |= {letter for each in needs if sum(each.values()) == 1 for letter in each}
    # The most managers first, then the earlier letter of the alphabet.
    ranked = sorted(need, key=lambda letter: (-need[letter], letter))
    picks = [letter for letter in ranked if letter not in guarded]
    # If the guard rules out a letter that the drop needs, the next letters by need fill the drop.
    picks += [letter for letter in ranked if letter in guarded]
    # With every egg word won, no manager needs a letter, so the letters of the egg words keep the drop whole.
    picks = picks or sorted(set("".join(words)))
    # No letter repeats within one drop, so a drop larger than the count of letters to pick gets fewer letters.
    return picks[:count]


def _needs(word: str, letters: Counter[str]) -> Counter[str]:
    """The letters that a manager with `letters` still needs to fill `word`. An empty count means the word is full."""
    return Counter(word) - letters
