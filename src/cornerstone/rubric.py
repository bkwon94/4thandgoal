"""
The trade analyzer rubric in code: the proposed trade, its input check, and the grade of each side.
The grade reads a snapshot and gives a breakdown per side that holds no trade value, sum, or ratio.
"""
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, model_validator

from cornerstone.snapshot import Snapshot
from cornerstone.tunables import CONSOLIDATION_MARGIN, START_LETTER_BANDS

Letter = Literal["A", "B", "C", "D", "F"]

# The reasons name a direction only. A trade value, a sum, or a ratio never reaches the breakdown.
BAND_REASONS: dict[str, str] = {
    "A": "It gets far more trade value than it gives.",
    "B": "It gets more trade value than it gives.",
    "C": "The trade value it gets and the trade value it gives are about even.",
    "D": "It gives more trade value than it gets.",
    "F": "It gives far more trade value than it gets.",
}
CONSOLIDATION_REASON = (
    "The trade is one player for two or more, so the side with more players needs a margin "
    "before the sides count as even."
)
NO_CHART_REASON = "The week has no trade values, so both sides start at C."


class TradeInputError(ValueError):
    """A proposed trade that does not fit the snapshot, such as a player who is not on the giving roster."""

    def __init__(self, message: str, player_id: str | None = None) -> None:
        super().__init__(message)
        self.player_id = player_id


class TradeSide(BaseModel):
    """One roster in a proposed trade and the players it gives."""

    roster_id: int
    gives: list[str]


class ProposedTrade(BaseModel):
    """A trade the analyzer grades before it happens. Two sides only, and players only, with no picks."""

    season: int
    sides: tuple[TradeSide, TradeSide]
    # The roster id of the side that asked. The verdict is for this side.
    asker: int

    @model_validator(mode="after")
    def _check_shape(self) -> "ProposedTrade":
        a, b = self.sides
        if a.roster_id == b.roster_id:
            raise ValueError("A proposed trade needs two different rosters")
        if not a.gives or not b.gives:
            raise ValueError("Each side of a proposed trade must give at least one player")
        given = a.gives + b.gives
        if len(set(given)) != len(given):
            raise ValueError("A player can appear only once in a proposed trade")
        if self.asker not in (a.roster_id, b.roster_id):
            raise ValueError(f"The asker {self.asker} is not one of the two rosters in the trade")
        return self


class Breakdown(BaseModel):
    """The grade of one side: the start letter and the reason for it, in plain words."""

    roster_id: int
    start_letter: Letter
    reason: str


def check_trade(trade: ProposedTrade, snapshot: Snapshot) -> None:
    """Raise TradeInputError when the trade does not fit the snapshot's season and rosters."""
    if trade.season != snapshot.season:
        raise TradeInputError(f"The trade is for season {trade.season}, but the snapshot is season {snapshot.season}")
    for side in trade.sides:
        roster = snapshot.rosters.get(side.roster_id)
        if roster is None:
            raise TradeInputError(f"Roster {side.roster_id} is not in the league")
        for pid in side.gives:
            if pid not in roster:
                raise TradeInputError(f"Player {pid} is not on roster {side.roster_id}", player_id=pid)


def _letter(got: Decimal, gave: Decimal) -> Letter:
    """The band of the ratio got over gave, with each lower bound inclusive."""
    if gave == 0:
        # Something for nothing is the top band. Nothing for nothing is even.
        return "A" if got > 0 else "C"
    ratio = got / gave
    for lower, letter in START_LETTER_BANDS:
        if ratio >= lower:
            return letter
    return "F"


def _join(names: list[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def grade(trade: ProposedTrade, snapshot: Snapshot) -> tuple[Breakdown, Breakdown]:
    """The breakdown of each side, in the order of trade.sides. It raises TradeInputError on a bad trade."""
    check_trade(trade, snapshot)
    a, b = trade.sides
    if snapshot.chart is None:
        return (Breakdown(roster_id=a.roster_id, start_letter="C", reason=NO_CHART_REASON),
                Breakdown(roster_id=b.roster_id, start_letter="C", reason=NO_CHART_REASON))
    values = snapshot.chart.values
    unlisted = [pid for side in trade.sides for pid in side.gives if pid not in values]
    if unlisted:
        names = [snapshot.players[pid].name for pid in unlisted]
        verb = "has" if len(names) == 1 else "have"
        reason = f"{_join(names)} {verb} no trade value, so neither side gets a start letter and both start at C."
        return (Breakdown(roster_id=a.roster_id, start_letter="C", reason=reason),
                Breakdown(roster_id=b.roster_id, start_letter="C", reason=reason))
    # Decimal sums keep half-point trade values exact, so a ratio at a band's lower bound stays in that band.
    sum_a = sum((Decimal(str(values[pid])) for pid in a.gives), Decimal(0))
    sum_b = sum((Decimal(str(values[pid])) for pid in b.gives), Decimal(0))
    # Only one player for two or more is a consolidation. A three-for-two trade gets no discount.
    consolidation = (len(a.gives) == 1) != (len(b.gives) == 1)
    if consolidation:
        if len(a.gives) > 1:
            sum_a /= CONSOLIDATION_MARGIN
        else:
            sum_b /= CONSOLIDATION_MARGIN

    def breakdown(roster_id: int, got: Decimal, gave: Decimal) -> Breakdown:
        letter = _letter(got, gave)
        reason = BAND_REASONS[letter] + (" " + CONSOLIDATION_REASON if consolidation else "")
        return Breakdown(roster_id=roster_id, start_letter=letter, reason=reason)

    return breakdown(a.roster_id, sum_b, sum_a), breakdown(b.roster_id, sum_a, sum_b)
