"""
The blocks of the league Topics in topics.json: the data of the one card that a Topic Answer shows, keyed by `kind`.
Each kind has a model and a builder here. The site holds the same union over `kind` (ADR 0013).
"""
import re
from typing import Literal

from pydantic import BaseModel


class RecapMark(BaseModel):
    """One team on the strip of the recap card. `you` marks the team of the Answer."""
    roster_id: int
    name: str
    score: float
    you: bool = False


class RecapTop(BaseModel):
    """The top scorer of the team of the Answer, against his projection of the week."""
    name: str
    position: str
    points: float
    projection: float | None


class RecapBlock(BaseModel):
    """The recap card of Week recap: the score and the place of the team, its opponent, a strip with a mark for each
    team, the top scorer, and the first sentence of the recap of its game. The median is None in a league that plays
    no median game, so the site draws no median tick there."""
    kind: Literal["recap"] = "recap"
    score: float
    place: int
    teams: int
    opponent: str | None
    opponent_score: float | None
    strip: list[RecapMark]
    median: float | None
    top: RecapTop | None
    sentence: str | None


# The block of one league Topic. A new kind joins this union with its model above and its builder below.
TopicBlock = RecapBlock

# A sentence ends at a stop followed by a space and a capital letter, so "III" or "49.5" never cut it short.
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")


def first_sentence(text: str | None) -> str | None:
    """The first sentence of a text, or None for no text."""
    if not text or not text.strip():
        return None
    return _SENTENCE_END.split(text.strip(), maxsplit=1)[0]


def recap_block(rid: int, page: dict) -> RecapBlock:
    """The recap card of one team, from the page.json of the week."""
    sides = [side for m in page["matchups"] for side in m["sides"]]
    strip = sorted((RecapMark(roster_id=s["team"]["roster_id"], name=s["team"]["name"], score=s["score"],
                              you=s["team"]["roster_id"] == rid) for s in sides), key=lambda mark: -mark.score)
    mine = next(mark for mark in strip if mark.you)
    game = next(m for m in page["matchups"] if any(s["team"]["roster_id"] == rid for s in m["sides"]))
    side = next(s for s in game["sides"] if s["team"]["roster_id"] == rid)
    other = next((s for s in game["sides"] if s["team"]["roster_id"] != rid), None)
    top = side.get("top")
    # Ties share the higher place, as the place of the stats does.
    place = [mark.score for mark in strip].index(mine.score) + 1
    return RecapBlock(
        score=mine.score, place=place, teams=len(strip),
        opponent=other["team"]["name"] if other else None, opponent_score=other["score"] if other else None,
        strip=strip, median=page["median"]["value"] if page.get("median") else None,
        top=RecapTop(name=top["name"], position=top["position"], points=top["points"],
                     projection=top.get("projection")) if top else None,
        sentence=first_sentence(game.get("recap")))
