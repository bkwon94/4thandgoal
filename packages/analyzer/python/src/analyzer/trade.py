"""
The proposed trade of the analyzer and the Finder: its sides, its input check, its fairness, and the reads of its sides.
The Advisor reads the trade, and the Measures and the fact sheet read the sides that build_sides gives.
"""
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, model_validator

from analyzer.measures import Side, build_side
from league.ranks import lineup_value
from league.snapshot import Snapshot


class TradeInputError(ValueError):
    """A proposed trade that does not fit the snapshot, such as a player who is not on the giving roster."""

    def __init__(self, message: str, player_id: str | None = None) -> None:
        super().__init__(message)
        self.player_id = player_id


class GivenPlayer(BaseModel):
    """One player a side gives and the roster id of the side he goes to."""

    player_id: str
    # Every given player names his destination, in a two-side trade too, so the API checks one shape (ADR 0008).
    to: int


class TradeSide(BaseModel):
    """One roster in a proposed trade and the players it gives. What it gets derives from the other sides."""

    roster_id: int
    gives: list[GivenPlayer]

    @property
    def player_ids(self) -> list[str]:
        """The ids of the players this side gives, in order, with no destination."""
        return [given.player_id for given in self.gives]


# A trade has two to four sides. A fifth side is out of scope, so the model rejects it with a plain message.
MIN_SIDES, MAX_SIDES = 2, 4


class ProposedTrade(BaseModel):
    """A trade the analyzer grades before it happens. Two to four sides, and players only, with no picks."""

    season: int
    # In the order of the request. Each list that the grade gives back keeps this order.
    sides: list[TradeSide]
    # The roster id of the side that asked. The Lean is for this side.
    asker: int

    @model_validator(mode="after")
    def _check_shape(self) -> "ProposedTrade":
        # The count checks run in the validator, so the message is plain and not the pydantic length text.
        if len(self.sides) > MAX_SIDES:
            raise ValueError("A proposed trade has four sides at most")
        if len(self.sides) < MIN_SIDES:
            raise ValueError("A proposed trade needs two to four sides")
        rosters = [side.roster_id for side in self.sides]
        if len(set(rosters)) != len(rosters):
            raise ValueError("A proposed trade needs a different roster on each side")
        if not all(side.gives for side in self.sides):
            raise ValueError("Each side of a proposed trade must give at least one player")
        given = self.player_ids
        if len(set(given)) != len(given):
            raise ValueError("A player can appear only once in a proposed trade")
        if self.asker not in rosters:
            raise ValueError(f"The asker {self.asker} is not one of the rosters in the trade")
        for side in self.sides:
            for player in side.gives:
                if player.to not in rosters:
                    raise ValueError(f"Player {player.player_id} goes to roster {player.to}, "
                                     "which is not a side of the trade")
        # The gets check runs before the own-roster check. A side that gets nothing can have a player sent home on
        # another side, and the missing gets is the plainer fault to name.
        for side in self.sides:
            if not self.gets(side.roster_id):
                raise ValueError(f"Roster {side.roster_id} gets no player in the trade")
        for side in self.sides:
            for player in side.gives:
                if player.to == side.roster_id:
                    raise ValueError(f"Player {player.player_id} goes to his own roster {side.roster_id}")
        return self

    @property
    def player_ids(self) -> list[str]:
        """The ids of every player in the trade, in the order of the sides and of each side's gives."""
        return [pid for side in self.sides for pid in side.player_ids]

    @property
    def givers(self) -> dict[str, int]:
        """The roster id of the side that gives each player in the trade, by player id."""
        return {player.player_id: side.roster_id for side in self.sides for player in side.gives}

    def gets(self, roster_id: int) -> list[str]:
        """The ids of the players the other sides send to `roster_id`, in the order of the sides."""
        return [player.player_id for side in self.sides if side.roster_id != roster_id
                for player in side.gives if player.to == roster_id]


class FairnessSide(BaseModel):
    """One side of the fairness: the roster and the one reason that says what it gains."""

    roster_id: int
    reason: str


class Fairness(BaseModel):
    """Whether the trade is good for every side, fair, or lopsided, with one reason per side.

    It is for every side, not only the asker, so a manager knows if the other sides will take the trade.
    """

    state: Literal["win_win", "fair", "lopsided"]
    # None when no side gives more, so a win-win or a fair trade names no loser.
    gives_more: int | None
    # In the order of the trade's sides, so the block lines up with the sides of the document.
    sides: tuple[FairnessSide, ...]


def check_trade(trade: ProposedTrade, snapshot: Snapshot) -> None:
    """Raise TradeInputError when the trade does not fit the snapshot's season and rosters."""
    if trade.season != snapshot.season:
        raise TradeInputError(f"The trade is for season {trade.season}, but the snapshot is season {snapshot.season}")
    for side in trade.sides:
        roster = snapshot.rosters.get(side.roster_id)
        if roster is None:
            raise TradeInputError(f"Roster {side.roster_id} is not in the league")
        for pid in side.player_ids:
            if pid not in roster:
                # A player who left the league is not in snapshot.players, so the id stands in for the name.
                player = snapshot.players.get(pid)
                name = player.name if player else pid
                raise TradeInputError(f"{name} is no longer on {snapshot.teams[side.roster_id].name}.", player_id=pid)


def _trade_values(snapshot: Snapshot, handcuffs: list[str]) -> dict[str, float]:
    """The trade value of each player on the chart, with every handcuff in the trade at zero, listed or not.

    A player out for the season and off the chart is at zero too. ADR 0005: he counts zero for the side that gets
    him, listed or not, so he is never unlisted. A listed one keeps his chart value for the side that gives him.
    """
    off_chart_season = {pid: 0.0 for pid in snapshot.out_for_season if pid not in snapshot.chart.values}
    return {**snapshot.chart.values, **off_chart_season, **{pid: 0.0 for pid in handcuffs}}


def _highest_value_player(trade: ProposedTrade, snapshot: Snapshot, handcuffs: list[str]) -> str | None:
    """The single highest-value player in the trade, or None when two or more tie at the top.

    Trade value picks him, with a handcuff at zero as in the sums. When the week has no chart or a traded
    player is unlisted, the trade values of the sides do not compare, so the lineup value picks him.
    The lineup value is recent points per game, or the projection ahead of a player due back, who has no recent games.
    """
    players = trade.player_ids
    values = _trade_values(snapshot, handcuffs) if snapshot.chart is not None else {}
    if all(pid in values for pid in players):
        worth = {pid: Decimal(str(values[pid])) for pid in players}
    else:
        # A handcuff counts as zero here too, so a handcuff due back with a high projection is never the pick.
        worth = {pid: Decimal(0) if pid in handcuffs else lineup_value(snapshot, pid) for pid in players}
    top = max(worth.values())
    leaders = [pid for pid, w in worth.items() if w == top]
    return leaders[0] if len(leaders) == 1 else None


def build_sides(trade: ProposedTrade, snapshot: Snapshot, handcuffs: list[str]) -> tuple[Side, ...]:
    """The reads of each side, in the order of trade.sides: the best lineup, its slots, and the holes.

    The Measures and the trade fact sheet both read the sides here, so the facts name the same slots.
    """
    top = _highest_value_player(trade, snapshot, handcuffs)
    return tuple(build_side(snapshot, side.roster_id, side.player_ids, trade.gets(side.roster_id), top, handcuffs)
                 for side in trade.sides)
