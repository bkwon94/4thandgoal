"""
The record book with the seven awards, the last chapter of Act II: the high, the low, the biggest margin, the closest
game, and the awards of decision ticket 10. Heartbreak and Beatdown are games of the record book, so each shows once.
"""
from collections import Counter
from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from facts.tokens import Nums, fact
from league.history import player_points
from league.models import Blurb, Fact, History
from league.numbers import r2
from league.provider.raw import RawTransaction
from midseason.lineups import LineupChoices
from midseason.moves import line_scores
from midseason.players import PlayerCard
from midseason.state import LeagueState
from midseason.waivers import WaiverFacts

AwardKey = Literal["mvp", "streaming-king", "bench-crime", "heartbreak", "beatdown", "most-active", "set-and-forget"]
# The seven awards in page order, with the title of each. Decision ticket 10.
AWARD_TITLES: dict[AwardKey, str] = {
    "mvp": "MVP",
    "streaming-king": "Streaming king",
    "bench-crime": "Bench crime of the year",
    "heartbreak": "Heartbreak of the year",
    "beatdown": "Beatdown of the year",
    "most-active": "Most active",
    "set-and-forget": "Set and forget",
}
# The positions of the MVP. K and DEF have no line, so they have no Points over the line.
MVP_POSITIONS = ("QB", "RB", "WR", "TE")
# The moves that the move count reads: each complete add and each trade.
ADD_TYPES = ("waiver", "free_agent")


class TeamScore(BaseModel):
    """One team's score of one week."""
    week: int
    roster_id: int
    team: str
    score: float


class Game(BaseModel):
    """One head-to-head game with a winner."""
    week: int
    winner_roster_id: int
    winner: str
    winner_score: float
    loser_roster_id: int
    loser: str
    loser_score: float
    margin: float


class Award(BaseModel):
    """One award: its winner, the number behind it, and its fact as the page shows it."""
    key: AwardKey
    title: str
    roster_id: int
    team: str
    # The number of the fact: the points, the margin, or the count of moves.
    value: float
    # The player of the MVP. None on any other award.
    player: str | None = None
    # The week of a game award. None on a season award.
    week: int | None = None
    # True for Heartbreak and Beatdown, which the page shows on their game of the record book.
    in_record_book: bool = False
    fact: str = ""


class RecordBook(BaseModel):
    """The facts of the record book: the four records of the season, then the seven awards in page order."""
    high: TeamScore
    low: TeamScore
    biggest_margin: Game
    closest: Game
    awards: list[Award]


class RecordsChapter(BaseModel):
    """The record book with the awards, the last chapter of Act II."""
    key: Literal["records"] = "records"
    title: str = "The record book"
    facts: RecordBook
    blurb: Blurb | None = None
    roast: Blurb | None = None


def _games(history: History, through: int, names: Mapping[int, str]) -> list[Game]:
    """Every head-to-head game with a winner, oldest first. A tie has no winner, so it is in no record."""
    games = []
    for number in range(1, through + 1):
        past = history.weeks[number]
        for a, b in past.pairs:
            sa, sb = Decimal(str(past.scores[a])), Decimal(str(past.scores[b]))
            if sa == sb:
                continue
            (win, ws), (lose, ls) = sorted(((a, sa), (b, sb)), key=lambda side: -side[1])
            games.append(Game(week=number, winner_roster_id=win, winner=names[win], winner_score=float(ws),
                              loser_roster_id=lose, loser=names[lose], loser_score=float(ls), margin=r2(float(ws - ls))))
    return games


def _scores(history: History, through: int, names: Mapping[int, str]) -> list[TeamScore]:
    return [TeamScore(week=number, roster_id=rid, team=names[rid], score=score)
            for number in range(1, through + 1) for rid, score in sorted(history.weeks[number].scores.items())]


def _mvp(history: History, through: int, names: Mapping[int, str], players: Mapping[str, PlayerCard],
         lines: Mapping[str, int]) -> Award | None:
    """The started QB, RB, WR, or TE with the most Points over the line, and the team that got the most of them."""
    line_at = line_scores(history, lines, through)
    over: dict[str, dict[int, Decimal]] = {}
    for number in range(1, through + 1):
        past = history.weeks[number]
        for rid, starters in past.starters.items():
            for pid in starters:
                position = past.positions.get(pid) or (players[pid].position if pid in players else None)
                line = line_at[number].get(position or "")
                if position not in MVP_POSITIONS or line is None:
                    continue
                points = Decimal(str(player_points(past, pid) or 0)) - Decimal(str(line))
                by_team = over.setdefault(pid, {})
                by_team[rid] = by_team.get(rid, Decimal(0)) + points
    if not over:
        return None
    name = {pid: players[pid].name if pid in players else pid for pid in over}
    best = min(over, key=lambda pid: (-sum(over[pid].values()), name[pid]))
    team = min(over[best], key=lambda rid: (-over[best][rid], rid))
    return Award(key="mvp", title=AWARD_TITLES["mvp"], roster_id=team, team=names[team],
                 value=r2(float(sum(over[best].values()))), player=name[best])


def move_counts(transactions: Mapping[int, Sequence[RawTransaction]], names: Mapping[int, str]) -> dict[int, int]:
    """The moves of each team: each complete waiver claim or free agent add, and each trade it took part in."""
    counts: Counter[int] = Counter({rid: 0 for rid in names})
    for week in transactions.values():
        for row in week:
            if row.status != "complete":
                continue
            if row.type in ADD_TYPES and row.adds:
                counts.update(set(row.adds.values()))
            elif row.type == "trade":
                counts.update(set(row.roster_ids))
    return {rid: counts[rid] for rid in names}


def _award(key: AwardKey, roster_id: int, names: Mapping[int, str], value: float, **extra) -> Award:
    return Award(key=key, title=AWARD_TITLES[key], roster_id=roster_id, team=names[roster_id], value=value, **extra)


def record_book(
    history: History, through: int, names: Mapping[int, str], *, players: Mapping[str, PlayerCard],
    lines: Mapping[str, int], transactions: Mapping[int, Sequence[RawTransaction]], waivers: WaiverFacts,
    lineups: LineupChoices, state: LeagueState,
) -> RecordBook:
    """The record book of weeks 1 to `through`. A tie of a record goes to the earlier week, and a tie of a season
    award goes to the name that sorts first. An award with no candidate, such as a league with no streamer, is out."""
    scores = _scores(history, through, names)
    games = _games(history, through, names)
    high = min(scores, key=lambda s: (-s.score, s.week, s.team))
    low = min(scores, key=lambda s: (s.score, s.week, s.team))
    closest = min(games, key=lambda g: (g.margin, g.week, g.loser))
    biggest = min(games, key=lambda g: (-g.margin, g.week, g.winner))
    awards: list[Award | None] = [_mvp(history, through, names, players, lines)]
    if waivers.streamers:
        king = waivers.streamers[0]
        awards.append(_award("streaming-king", king.roster_id, names, king.points))
    crimes = [(team, week) for team in lineups.teams for week in team.lost_with_better]
    if crimes:
        team, week = min(crimes, key=lambda c: (-c[1].bench_points, c[1].week, c[0].name))
        awards.append(_award("bench-crime", team.roster_id, names, week.bench_points, week=week.week))
    awards.append(_award("heartbreak", closest.loser_roster_id, names, closest.margin, week=closest.week,
                         in_record_book=True))
    awards.append(_award("beatdown", biggest.winner_roster_id, names, biggest.margin, week=biggest.week,
                         in_record_book=True))
    moves = move_counts(transactions, names)
    most = min(moves, key=lambda rid: (-moves[rid], names[rid]))
    fewest = min(moves, key=lambda rid: (moves[rid], names[rid]))
    awards.append(_award("most-active", most, names, moves[most]))
    awards.append(_award("set-and-forget", fewest, names, moves[fewest]))
    book = RecordBook(high=high, low=low, biggest_margin=biggest, closest=closest,
                      awards=[award for award in awards if award is not None])
    facts = {f.id: f.text for f in records_facts(book, waivers=waivers, lineups=lineups, state=state)}
    return book.model_copy(update={"awards": [a.model_copy(update={"fact": facts[f"AW.{a.key}"]})
                                              for a in book.awards]})


def _record(n: Nums, state: LeagueState, roster_id: int) -> str:
    team = next(team for team in state.teams if team.roster_id == roster_id)
    return n.text(f"{team.wins}-{team.losses}-{team.ties}") if team.ties else n.record(team.wins, team.losses)


def _award_fact(award: Award, book: RecordBook, waivers: WaiverFacts, lineups: LineupChoices,
                state: LeagueState) -> Fact:
    n = Nums()
    fid = f"AW.{award.key}"
    if award.key == "mvp":
        return fact(fid, f"{award.player} of {award.team} has {n(award.value)} points over the line in his starts, "
                    f"the most of any QB, RB, WR, or TE.", n, [award.team], [award.player or ""])
    if award.key == "streaming-king":
        king = waivers.streamers[0]
        return fact(fid, f"{king.team} started streamed QBs, kickers, and defenses {n(king.starts)} times for "
                    f"{n(king.points)} points, the most in the league.", n, [king.team], [])
    if award.key == "bench-crime":
        team = next(team for team in lineups.teams if team.roster_id == award.roster_id)
        week = next(week for week in team.lost_with_better if week.week == award.week)
        return fact(fid, f"{team.name} left {n(week.bench_points)} points on the bench in its week {n(week.week)} loss "
                    f"to {week.opponent}, the most in a loss that a better lineup would have won.",
                    n, [team.name, week.opponent], [])
    if award.key == "heartbreak":
        game = book.closest
        return fact(fid, f"{game.loser} lost to {game.winner} by {n(game.margin)} in week {n(game.week)}, the closest "
                    f"head-to-head game of the season.", n, [game.loser, game.winner], [])
    if award.key == "beatdown":
        game = book.biggest_margin
        return fact(fid, f"{game.winner} beat {game.loser} by {n(game.margin)} in week {n(game.week)}, the biggest "
                    f"head-to-head margin of the season.", n, [game.winner, game.loser], [])
    if award.key == "most-active":
        return fact(fid, f"{award.team} made {n(int(award.value))} moves, adds and trades, the most in the league.", n,
                    [award.team], [])
    return fact(fid, f"{award.team} made {n(int(award.value))} moves, the fewest in the league, and is "
                f"{_record(n, state, award.roster_id)}.", n, [award.team], [])


def records_facts(book: RecordBook, *, waivers: WaiverFacts, lineups: LineupChoices, state: LeagueState) -> list[Fact]:
    """The facts of the record book: the high, the low, and each award. The biggest margin and the closest game are
    the facts of Beatdown and Heartbreak, so each game has one fact."""
    facts = []
    for fid, entry, word in (("RB.high", book.high, "highest"), ("RB.low", book.low, "lowest")):
        n = Nums()
        facts.append(fact(fid, f"{entry.team} scored {n(entry.score)} in week {n(entry.week)}, the {word} score of the "
                          f"season.", n, [entry.team], []))
    facts += [_award_fact(award, book, waivers, lineups, state) for award in book.awards]
    return facts
