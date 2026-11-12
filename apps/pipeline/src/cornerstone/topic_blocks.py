"""
The blocks of the league Topics in topics.json: the data of the one card that a Topic Answer shows, keyed by `kind`.
Each kind has a model and a builder here. The site holds the same union over `kind` (ADR 0013). The model of the
matchup card lives in league.matchup_card, because the live card of the API shares it.
"""
import re
from typing import Literal

from pydantic import BaseModel

from league.lineup import fill_slots
from league.matchup_card import (
    MatchupBlock,
    MatchupPlayer,
    MatchupTeam,
    matchup_slots,
    starting_slots,
)
from league.models import PlayerLine, Week


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


class RankMover(BaseModel):
    """One team of the rank mover list: its power rank and its move in places since the week before. The move is
    positive up and negative down, and None in the first ranked week."""
    roster_id: int
    name: str
    rank: int
    move: int | None
    you: bool = False


class RankMoversBlock(BaseModel):
    """The rank mover list of Power rankings: one row per team, by power rank."""
    kind: Literal["rank_movers"] = "rank_movers"
    rows: list[RankMover]


# The block of one league Topic. A new kind joins this union with its model above and its builder below.
TopicBlock = RecapBlock | MatchupBlock | RankMoversBlock

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


def _played(line: PlayerLine) -> MatchupPlayer:
    return MatchupPlayer(name=line.name, position=line.position, nfl_team=line.nfl_team, points=line.points)


def _starters(lines: list[PlayerLine]) -> list[tuple[str, MatchupPlayer]]:
    # The parse keeps the slot of each starter but not his place among the slots of the same name, so the most
    # points lead within a slot.
    started = sorted((line for line in lines if line.started and line.slot), key=lambda line: -line.points)
    return [(line.slot, _played(line)) for line in started if line.slot]


def last_matchup_block(rid: int, week: Week) -> MatchupBlock | None:
    """The matchup card of the played game of one team, with the final scores, from the parsed raw week.
    None when the team had no game."""
    game = next((m for m in week.matchups if rid in (m.a.roster_id, m.b.roster_id)), None)
    if game is None:
        return None
    mine, other = (game.a, game.b) if game.a.roster_id == rid else (game.b, game.a)
    return MatchupBlock(
        final=True,
        you=MatchupTeam(roster_id=mine.roster_id, name=week.teams[mine.roster_id].name, score=mine.points),
        them=MatchupTeam(roster_id=other.roster_id, name=week.teams[other.roster_id].name, score=other.points),
        slots=matchup_slots(starting_slots(week.roster_positions), _starters(mine.lines), _starters(other.lines)))


def _projected(rid: int, week: Week, projections: dict[str, float]) -> tuple[float, list[tuple[str, MatchupPlayer]]]:
    """The projected total and the starters of the best lineup of one current roster by the projections of a week.
    A player with no projection that week, such as a player on his bye, counts 0, so a bench player takes his slot."""
    positions = week.rosters.get(rid, {})
    points = {pid: projections.get(pid) or 0.0 for pid in positions}
    starters = []
    for slot, pid in fill_slots(list(points), week.roster_positions, positions, points):
        if pid is None:
            continue
        name, team = week.roster_players.get(pid, (pid, None))
        starters.append((slot, MatchupPlayer(name=name, position=positions[pid], nfl_team=team, points=points[pid])))
    return round(sum(player.points for _, player in starters), 2), starters


def next_matchup_block(rid: int, week: Week) -> MatchupBlock | None:
    """The matchup card of the next game of one team, with the projected scores of the best lineup of each current
    roster for the next week, from the parsed raw week. None when the team has no next game or the week has no
    projections. The weekly build knows no win odds."""
    pair = next((p for p in week.next_matchups if rid in p), None)
    projections = week.projections_ahead.get(week.week + 1)
    if pair is None or not projections:
        return None
    other = pair[1] if pair[0] == rid else pair[0]
    (my_score, mine), (their_score, theirs) = _projected(rid, week, projections), _projected(other, week, projections)
    return MatchupBlock(
        final=False,
        you=MatchupTeam(roster_id=rid, name=week.teams[rid].name, score=my_score),
        them=MatchupTeam(roster_id=other, name=week.teams[other].name, score=their_score),
        slots=matchup_slots(starting_slots(week.roster_positions), mine, theirs))


def rank_movers_block(rid: int, ranked: dict) -> RankMoversBlock:
    """The rank mover list of one team, from the week of rankings.json that the build ranked."""
    return RankMoversBlock(rows=[
        RankMover(roster_id=r["roster_id"], name=r["name"], rank=r["rank"], move=r.get("movement"),
                  you=r["roster_id"] == rid)
        for r in sorted(ranked["rows"], key=lambda r: r["rank"])])
