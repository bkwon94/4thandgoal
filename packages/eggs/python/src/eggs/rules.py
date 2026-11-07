"""
The claim rules of the egg hunt: which slots of an egg word are open, who won a word, and why a claim is refused.
Each function reads the claims that hold their eggs, so an undo changes every answer.
"""
from collections import Counter

from eggs.store import Claim
from eggs.values import EggsValues


def letters_of(claims: list[Claim], roster_id: int, word: str) -> list[str]:
    """The letters of the roster in the egg word, oldest claim first. A block holds no egg word, so it counts for none.

    The rules, the letter rule of the drop, the claim, and the board each count the letters of a roster with it.
    """
    # The store lists the claims newest first, so the reverse gives the order of the claims.
    return [claim.letter for claim in reversed(claims) if claim.roster_id == roster_id and claim.word == word]


def _held(claims: list[Claim], roster_id: int, word: str) -> Counter[str]:
    return Counter(letters_of(claims, roster_id, word))


def winner(claims: list[Claim], word: str) -> int | None:
    """The roster id of the manager whose letters fill the egg word, or None while no manager fills it."""
    rosters = {claim.roster_id for claim in claims if claim.word == word}
    return next((roster_id for roster_id in sorted(rosters) if _held(claims, roster_id, word) == Counter(word)), None)


def has_open_slot(claims: list[Claim], roster_id: int, word: str, letter: str) -> bool:
    """True when the egg word has no winner and the manager holds fewer of the letter than the word has."""
    return winner(claims, word) is None and _held(claims, roster_id, word)[letter] < Counter(word)[letter]


def refusal(values: EggsValues, claims: list[Claim], roster_id: int, word: str | None, letter: str) -> str | None:
    """The reason to refuse the claim of the letter, or None when the claim stands."""
    if roster_id == values.commissioner:
        return "The commissioner places the eggs and cannot hunt them."
    words = [each.word for each in values.words]
    if word is None:
        if any(has_open_slot(claims, roster_id, each, letter) for each in words):
            return f"The letter {letter} fits an egg word of the manager, so a block is not open."
        return None
    if winner(claims, word) is not None:
        return f"{word} has a winner."
    if not has_open_slot(claims, roster_id, word, letter):
        return f"{word} has no open slot for the letter {letter}."
    return None
