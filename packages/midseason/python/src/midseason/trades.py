"""
The trade report card of Act II: every trade with its Trade result, from the gap of the net Points over the line of
each side since the trade. It reads the trades of the transactions of each week that the app fetched again.
"""
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from facts.tokens import Nums, fact
from league.models import Fact, History
from league.numbers import r2
from league.provider.raw import RawTransaction
from league.standings_table import week_median
from league.trades import default_cutoff
from midseason.moves import line_scores, stint
from midseason.players import PlayerCard

TradeResult = Literal["Robbery", "Clear win", "Slight edge", "Even", "Too soon"]
# The tunables of the Trade result, PRD "The report: chapters and rules". A gap at or above a line takes its label.
# On the CPC week 8 data, they give 2 Robberies and 2 Clear wins.
RESULT_LINES: tuple[tuple[float, TradeResult], ...] = (
    (90, "Robbery"), (60, "Clear win"), (10, "Slight edge"))
# A trade with fewer weeks than this since it is Too soon.
TOO_SOON_WEEKS = 2


class TradePlayer(BaseModel):
    """One player that a side got, with his starts and Points over the line for that side during his stint."""
    player_id: str
    player: str
    position: str
    starts: int
    # None for a position with no line, such as K and DEF.
    points_over_line: float | None
    # True when he missed his NFL team's game in the first week after the trade.
    hurt_on_arrival: bool


class Record(BaseModel):
    wins: int
    losses: int
    ties: int


class TradeSide(BaseModel):
    roster_id: int
    team: str
    got: list[TradePlayer]
    # What it got and started, minus what it gave away as the other team started those players.
    net: float
    # The record of the team since the trade, as context. It does not count in the result.
    since: Record


class TradeCard(BaseModel):
    transaction_id: str
    # The week of the Trade window of the trade. Its games are the first that count.
    week: int
    weeks_since: int
    sides: list[TradeSide]
    # The net of the best side minus the net of the worst side.
    gap: float
    result: TradeResult
    # The team of the best side. None for an Even trade or Too soon.
    winner: str | None


class TradeFacts(BaseModel):
    """Every trade, the biggest gap first, with each Too soon trade last. The page shows the first 3 as full cards."""
    trades: list[TradeCard]


def trade_week(created: datetime, season_start: date, tz: ZoneInfo, through: int) -> int:
    """The week of the Trade window that holds `created`: the last week whose Tuesday cutoff came before it."""
    week = 1
    for number in range(2, through + 2):
        if created > default_cutoff(season_start, number, tz):
            week = number
    return week


def trade_result(gap: float, weeks_since: int) -> TradeResult:
    if weeks_since < TOO_SOON_WEEKS:
        return "Too soon"
    for line, label in RESULT_LINES:
        if gap >= line:
            return label
    return "Even"


def _record(history: History, roster_id: int, start: int, through: int, median_game: bool) -> Record:
    wins = losses = ties = 0

    def settle(mine: Decimal, theirs: Decimal) -> None:
        nonlocal wins, losses, ties
        if mine > theirs:
            wins += 1
        elif mine < theirs:
            losses += 1
        else:
            ties += 1

    for number in range(start, through + 1):
        past = history.weeks[number]
        if roster_id not in past.scores:
            continue
        # Exact decimals, as the standings compare them.
        mine = Decimal(str(past.scores[roster_id]))
        for a, b in past.pairs:
            if roster_id in (a, b):
                settle(mine, Decimal(str(past.scores[b if roster_id == a else a])))
        median = week_median(past) if median_game else None
        if median is not None:
            settle(mine, median)
    return Record(wins=wins, losses=losses, ties=ties)


def _hurt_on_arrival(history: History, player_id: str, info: PlayerCard, week: int) -> bool:
    """True when the player played no game in `week` while his NFL team played one. No injury source has a date, so a
    missed game of his team is the test. PRD, "Missing injury rows"."""
    past = history.weeks.get(week)
    if past is None:
        return False
    team = past.nfl_teams.get(player_id) or info.nfl_team
    played = {pid for pid, line in past.stats.items() if (line.get("gp") or 0) >= 1}
    team_played = any(past.nfl_teams.get(pid) == team for pid in played)
    return team is not None and team_played and player_id not in played


def trade_facts(
    history: History, through: int, transactions: Mapping[int, Sequence[RawTransaction]],
    players: Mapping[str, PlayerCard], names: Mapping[int, str], lines: Mapping[str, int], *,
    season_start: date, tz: ZoneInfo, median_game: bool = True,
) -> TradeFacts:
    """The Trade result of each complete trade of weeks 1 to `through`.

    "Since" starts at the week of the Trade window of the trade, and a player counts only during his stint on the
    side that got him. In a trade of 3 teams, the gap runs from the best side to the worst side.
    """
    line_at = line_scores(history, lines, through)
    rows = {t.transaction_id: t for week in transactions.values() for t in week
            if t.type == "trade" and t.status == "complete"}
    cards: list[TradeCard] = []
    for row in sorted(rows.values(), key=lambda t: t.created):
        created = datetime.fromtimestamp(row.created / 1000, tz=UTC)
        week = trade_week(created, season_start, tz, through)
        adds = row.adds or {}
        over: dict[str, float] = {}
        got: dict[int, list[TradePlayer]] = {rid: [] for rid in row.roster_ids}
        for player_id, roster_id in adds.items():
            info = players.get(player_id) or PlayerCard(player_id=player_id, name=player_id, position="")
            run = stint(history, line_at, player_id, info.position, roster_id, week, through)
            over[player_id] = run.points_over_line or 0.0
            got.setdefault(roster_id, []).append(TradePlayer(
                player_id=player_id, player=info.name, position=info.position, starts=run.starts,
                points_over_line=run.points_over_line,
                hurt_on_arrival=_hurt_on_arrival(history, player_id, info, week)))
        sides = []
        for roster_id in row.roster_ids:
            gained = sum((Decimal(str(over[pid])) for pid, rid in adds.items() if rid == roster_id), Decimal(0))
            gave = sum((Decimal(str(over[pid])) for pid, rid in (row.drops or {}).items()
                        if rid == roster_id and pid in over), Decimal(0))
            sides.append(TradeSide(roster_id=roster_id, team=names[roster_id], got=got[roster_id],
                                   net=r2(float(gained - gave)),
                                   since=_record(history, roster_id, week, through, median_game)))
        best = max(sides, key=lambda s: s.net)
        gap = r2(float(Decimal(str(best.net)) - Decimal(str(min(s.net for s in sides)))))
        weeks_since = through - week + 1
        result = trade_result(gap, weeks_since)
        cards.append(TradeCard(transaction_id=row.transaction_id, week=week, weeks_since=weeks_since, sides=sides,
                               gap=gap, result=result,
                               winner=None if result in ("Even", "Too soon") else best.team))
    cards.sort(key=lambda c: (c.result == "Too soon", -c.gap, c.week))
    return TradeFacts(trades=cards)


def trade_prose_facts(facts: TradeFacts) -> list[Fact]:
    """The facts that the trade prose block cites. Each trade has one fact with each side, the gap, and the Trade
    result, then the net and the record since of each side, so each fact holds two numbers at most, as a sentence of
    the writer may."""
    out = []
    for place, card in enumerate(facts.trades, start=1):
        n = Nums()
        parts = [f"{side.team} got {', '.join(p.player for p in side.got) or 'no player'}" for side in card.sides]
        result = card.result if card.winner is None else f"{card.result} for {card.winner}"
        out.append(fact(
            f"TR.{place}",
            f"In the trade of week {n(card.week)}, " + "; ".join(parts) + f". The gap is {n(card.gap)}. "
            f"The Trade result is {result}.",
            n, [side.team for side in card.sides], [p.player for side in card.sides for p in side.got]))
        for side in card.sides:
            players = [p.player for p in side.got]
            n = Nums()
            out.append(fact(f"TR.{place}.{side.roster_id}",
                            f"{side.team} has a net of {n(side.net)} points over the line since the week "
                            f"{n(card.week)} trade.", n, [side.team], players))
            n = Nums()
            out.append(fact(f"TR.{place}.{side.roster_id}.since",
                            f"{side.team} is {n.text(_record_text(side.since))} since the week {n(card.week)} trade.",
                            n, [side.team], players))
    return out


def _record_text(record: Record) -> str:
    return f"{record.wins}-{record.losses}" + (f"-{record.ties}" if record.ties else "")
