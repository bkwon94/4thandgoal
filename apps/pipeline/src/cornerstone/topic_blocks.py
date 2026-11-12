"""
The blocks of the league Topics in topics.json: the data of the one card that a Topic Answer shows, keyed by `kind`.
Each kind has a model and a builder here. The site holds the same union over `kind` (ADR 0013).
"""
import re
from typing import Literal

from pydantic import BaseModel

from league.lineup import BENCH_SLOTS, fill_slots
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


class MatchupPlayer(BaseModel):
    """The player of one side in one slot of a matchup card. The points are final for a played game and the
    projection for a game ahead."""
    name: str
    position: str
    nfl_team: str | None
    points: float


class MatchupSlot(BaseModel):
    """One starting slot of a matchup card, such as RB or FLEX, with the player of each side. A side with an empty
    slot has None there. The site draws the gap of the slot from the two points."""
    slot: str
    you: MatchupPlayer | None
    them: MatchupPlayer | None


class MatchupTeam(BaseModel):
    """One team of a matchup card with its total: the final score or the projected score."""
    roster_id: int
    name: str
    score: float


class MatchupBlock(BaseModel):
    """The matchup card of Your last matchup and Your next matchup: the two teams, their scores, and the starting
    slots in the Sleeper order of the league. `final` tells final scores from projected ones. `odds` is the win chance
    of Your team from 0 to 1 for a game ahead, or None when no odds are known, such as for a played game. The weekly
    build and the live card of the API share this model."""
    kind: Literal["matchup"] = "matchup"
    final: bool
    you: MatchupTeam
    them: MatchupTeam
    odds: float | None = None
    slots: list[MatchupSlot]


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


class LadderRow(BaseModel):
    """One team of the standings ladder: its standing, its record, and its playoff odds in percent. The odds are None
    when the week has no odds for the team."""
    roster_id: int
    name: str
    rank: int
    record: str
    odds: int | None
    you: bool = False


class LadderBlock(BaseModel):
    """The standings ladder of Playoff race: one row per team, by standing. The playoff line sits after the row of
    rank `playoff_teams`, the playoff spots of `settings.playoff_teams` in the league file."""
    kind: Literal["ladder"] = "ladder"
    playoff_teams: int
    rows: list[LadderRow]


class ScheduleRow(BaseModel):
    """One week left of the schedule strip: the opponent of that week with its standing and its record now."""
    week: int
    roster_id: int
    opponent: str
    rank: int
    record: str


class ScheduleBlock(BaseModel):
    """The schedule strip of Your season: one row per week left in the regular season. The site draws the ranks of
    the opponents as a step path against the playoff line, the row of rank `playoff_teams`, out of `teams`."""
    kind: Literal["schedule"] = "schedule"
    playoff_teams: int
    teams: int
    rows: list[ScheduleRow]


# The block of one league Topic. A new kind joins this union with its model above and its builder below.
TopicBlock = RecapBlock | MatchupBlock | RankMoversBlock | LadderBlock | ScheduleBlock

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


def starting_slots(roster_positions: list[str]) -> list[str]:
    """The starting slots of a league in the Sleeper order, such as QB, RB, RB, FLEX, with the bench slots left out."""
    return [slot for slot in roster_positions if slot not in BENCH_SLOTS]


def matchup_slots(slots: list[str], you: list[tuple[str, MatchupPlayer]],
                  them: list[tuple[str, MatchupPlayer]]) -> list[MatchupSlot]:
    """The rows of a matchup card: each starting slot in `slots` with the next player of each side for that slot.
    Each side lists its starters as pairs of the slot and the player, best first within a slot, so RB1 meets RB1."""
    def take(side: list[tuple[str, MatchupPlayer]], slot: str) -> MatchupPlayer | None:
        at = next((i for i, (each, _) in enumerate(side) if each == slot), None)
        return None if at is None else side.pop(at)[1]

    left, right = list(you), list(them)
    return [MatchupSlot(slot=slot, you=take(left, slot), them=take(right, slot)) for slot in slots]


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


def ladder_block(rid: int, page: dict, ranked: dict | None) -> LadderBlock:
    """The standings ladder of one team, from the table of page.json and the odds of the week of rankings.json.
    The table marks each team over the playoff line with `in_playoffs`, from `settings.playoff_teams`, so their count
    is the playoff line."""
    odds = {r["roster_id"]: r["odds"]["playoff"] for r in (ranked or {}).get("rows", []) if r.get("odds")}
    standings = sorted((entry["standing"] for entry in page["table"]), key=lambda s: s["rank"])
    names = {entry["team"]["roster_id"]: entry["team"]["name"] for entry in page["table"]}
    return LadderBlock(
        playoff_teams=sum(1 for s in standings if s["in_playoffs"]),
        rows=[LadderRow(roster_id=s["roster_id"], name=names[s["roster_id"]], rank=s["rank"],
                        record=f"{s['wins']}-{s['losses']}", odds=odds.get(s["roster_id"]), you=s["roster_id"] == rid)
              for s in standings])


def schedule_block(rid: int, page: dict, week: Week) -> ScheduleBlock | None:
    """The schedule strip of one team, from the pairs of the next week and of the weeks after it in the parsed raw
    `week`, and the standings of the table of page.json. A week with no game for the team, such as a bye, has no row.
    None when no week is left."""
    standings = {entry["team"]["roster_id"]: entry["standing"] for entry in page["table"]}
    weeks = {week.week + 1: week.next_matchups, **week.schedule}
    rows = []
    for number in sorted(weeks):
        pair = next((p for p in weeks[number] if rid in p), None)
        if pair is None:
            continue
        other = pair[1] if pair[0] == rid else pair[0]
        standing = standings[other]
        rows.append(ScheduleRow(week=number, roster_id=other, opponent=week.teams[other].name, rank=standing["rank"],
                                record=f"{standing['wins']}-{standing['losses']}"))
    if not rows:
        return None
    return ScheduleBlock(playoff_teams=sum(1 for s in standings.values() if s["in_playoffs"]), teams=len(standings),
                         rows=rows)
