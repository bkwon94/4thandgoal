"""
The players that a typed start question names, found by code over the rostered players of the league: Your players
in the order of the question, and each player of another roster. A name match is a fact, so no Jev read runs here.
"""
import re
from collections.abc import Mapping
from dataclasses import dataclass

# The suffixes after a last name, such as "Jr." in "Mike Washington Jr.". A question names a player without them.
SUFFIXES = frozenset({"jr", "sr", "ii", "iii", "iv", "v"})
# The words of a start question that are never a name, even when a rostered player has that last or first name.
NOT_NAMES = frozenset({"start", "sit", "or", "and", "the", "a", "i", "my", "me", "who", "should", "this", "week",
                       "flex", "over", "vs", "bench", "play", "in", "at"})


@dataclass(frozen=True)
class Named:
    """The players that a question names: the player ids of Your roster in the order of the question, and the player
    ids of the other rosters."""

    own: list[str]
    others: list[str]


def _words(text: str) -> list[str]:
    """The words of `text` in lower case. An apostrophe or a period joins its word, so "Ja'Marr" and "A.J." stay one
    word, and each other sign splits words."""
    return re.sub(r"[^a-z0-9]+", " ", re.sub(r"['’.]", "", text.lower())).split()


def _name_words(name: str) -> list[str]:
    return [word for word in _words(name) if word not in SUFFIXES]


def _at(words: list[str], part: list[str]) -> int | None:
    """The index of the first run of `part` in `words`, or None."""
    for start in range(len(words) - len(part) + 1):
        if part and words[start:start + len(part)] == part:
            return start
    return None


def _by_last(word: str, names: Mapping[str, str]) -> list[str]:
    return [pid for pid, name in names.items() if _name_words(name)[-1:] == [word]]


def _by_first(word: str, names: Mapping[str, str]) -> list[str]:
    """The one player whose first name is `word`, or none when no player or more than one has it."""
    hits = [pid for pid, name in names.items() if len(_name_words(name)) > 1 and _name_words(name)[0] == word]
    return hits if len(hits) == 1 else []


def named_players(question: str, own: Mapping[str, str], others: Mapping[str, str]) -> Named:
    """The players that `question` names, from the names of Your players `own` and of the players of the other rosters
    `others`, each by player id.

    A full name matches first. A last name then matches Your players before the players of the other rosters, so "Start
    Williams" means the Williams on Your team. A first name matches last, and only when one rostered player has it, as
    "Bijan" does.
    """
    words = _words(question)
    taken: set[int] = set()
    found: dict[str, tuple[int, bool]] = {}
    everyone = [(pid, name, True) for pid, name in own.items()] + [(pid, name, False) for pid, name in others.items()]
    for pid, name, mine in everyone:
        part = _name_words(name)
        start = _at(words, part) if len(part) > 1 else None
        if start is not None:
            found[pid] = (start, mine)
            taken.update(range(start, start + len(part)))
    for index, word in enumerate(words):
        if index in taken or word in NOT_NAMES:
            continue
        hits = _by_last(word, own) or _by_last(word, others) or _by_first(word, {**own, **others})
        for pid in hits:
            found.setdefault(pid, (index, pid in own))
        if hits:
            taken.add(index)
    ordered = sorted(found, key=lambda pid: found[pid][0])
    return Named(own=[pid for pid in ordered if found[pid][1]], others=[pid for pid in ordered if not found[pid][1]])
