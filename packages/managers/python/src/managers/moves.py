"""
The moves of a managers entry: the adds, the drops, and the trades of one roster per week, and the season totals.
Pure code over the saved history. The names and the positions come from the raw players file of the week.
"""
from pydantic import BaseModel, ConfigDict, Field

from league.models import History, PastWeek, Trade
from league.parse import player_name


class MovePlayer(BaseModel):
    """A player of a move. The name falls back to the id, and the position to None, when the players file lacks him."""
    player_id: str
    name: str
    position: str | None


class MoveAdd(MovePlayer):
    """An add by a waiver claim or a free agent pickup. A free agent pickup has no bid."""
    kind: str
    bid: int | None


class MoveTrade(BaseModel):
    """One trade from the side of the roster: the other rosters, the players it gave, and the players it got."""
    # "with" is a Python keyword, so the field takes it as an alias. The render dumps the entry with no
    # by_alias flag, so the model turns the alias on for every dump.
    model_config = ConfigDict(serialize_by_alias=True)
    with_: list[int] = Field(serialization_alias="with")
    gave: list[MovePlayer]
    got: list[MovePlayer]


class MoveWeek(BaseModel):
    """The moves of one roster in one week. A week with no moves holds empty lists."""
    week: int
    adds: list[MoveAdd]
    drops: list[MovePlayer]
    trades: list[MoveTrade]


class Moves(BaseModel):
    """The season totals of the roster, and every week from the history week down to week 1."""
    adds: int
    drops: int
    trades: int
    weeks: list[MoveWeek]


def _player(player_id: str, players: dict[str, dict]) -> MovePlayer:
    entry = players.get(player_id)
    return MovePlayer(
        player_id=player_id, name=player_name(player_id, entry), position=entry.get("position") if entry else None,
    )


def _trade(trade: Trade, roster_id: int, players: dict[str, dict]) -> MoveTrade:
    # The draft picks of a trade are out of the moves, so only the players count.
    return MoveTrade(
        with_=sorted(r for r in trade.roster_ids if r != roster_id),
        gave=[_player(pid, players) for pid, rid in sorted(trade.drops.items()) if rid == roster_id],
        got=[_player(pid, players) for pid, rid in sorted(trade.adds.items()) if rid == roster_id],
    )


def _week(past: PastWeek | None, number: int, roster_id: int, players: dict[str, dict]) -> MoveWeek:
    if past is None:
        return MoveWeek(week=number, adds=[], drops=[], trades=[])
    return MoveWeek(
        week=number,
        # A trade add is a side of its trade, not an add.
        adds=[
            MoveAdd(**_player(m.player_id, players).model_dump(), kind=m.kind, bid=m.bid)
            for m in past.moves if m.roster_id == roster_id and m.kind != "trade"
        ],
        drops=[_player(d.player_id, players) for d in past.drops if d.roster_id == roster_id],
        trades=[_trade(t, roster_id, players) for t in past.trades if roster_id in t.roster_ids],
    )


def roster_moves(history: History, roster_id: int, players: dict[str, dict]) -> Moves:
    """The moves of the roster in every week from 1 to the history week, newest first, with the season totals."""
    weeks = [_week(history.weeks.get(n), n, roster_id, players) for n in range(history.week, 0, -1)]
    return Moves(
        adds=sum(len(w.adds) for w in weeks),
        drops=sum(len(w.drops) for w in weeks),
        trades=sum(len(w.trades) for w in weeks),
        weeks=weeks,
    )
