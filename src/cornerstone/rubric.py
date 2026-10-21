"""
The trade analyzer rubric in code: the proposed trade, its input check, and the grade of each side.
The grade gives each side a start letter, then runs the adjusters in ADJUSTERS in rubric order.
"""
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, model_validator

from cornerstone.adjusters import ADJUSTERS, Adjuster, build_side, named, recent_points_per_game, trade_handcuffs
from cornerstone.snapshot import Snapshot
from cornerstone.tunables import CONSOLIDATION_MARGIN, START_LETTER_BANDS

# The breakdown per side holds no trade value, sum, or ratio.

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
    """The grade of one side: the start letter, the reason for it, and each adjuster in rubric order."""

    roster_id: int
    start_letter: Letter
    reason: str
    adjusters: list[Adjuster] = []


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


def _both_at_c(a: TradeSide, b: TradeSide, reason: str) -> tuple[Breakdown, Breakdown]:
    return (Breakdown(roster_id=a.roster_id, start_letter="C", reason=reason),
            Breakdown(roster_id=b.roster_id, start_letter="C", reason=reason))


def _trade_values(snapshot: Snapshot, handcuffs: list[str]) -> dict[str, float]:
    """The trade value of each player on the chart, with every handcuff in the trade at zero, listed or not."""
    return {**snapshot.chart.values, **{pid: 0.0 for pid in handcuffs}}


def _start_letters(trade: ProposedTrade, snapshot: Snapshot, handcuffs: list[str]) -> tuple[Breakdown, Breakdown]:
    """The start letter and its reason for each side, before any adjuster. A handcuff counts as zero in the sums."""
    a, b = trade.sides
    if snapshot.chart is None:
        return _both_at_c(a, b, NO_CHART_REASON)
    values = _trade_values(snapshot, handcuffs)
    unlisted = [pid for side in trade.sides for pid in side.gives if pid not in values]
    if unlisted:
        reason = (named(snapshot, unlisted, "has", "have")
                  + " no trade value, so neither side gets a start letter and both start at C.")
        return _both_at_c(a, b, reason)
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


def _highest_value_player(trade: ProposedTrade, snapshot: Snapshot, handcuffs: list[str]) -> str | None:
    """The single highest-value player in the trade, or None when two or more tie at the top.

    Trade value picks him, with a handcuff at zero as in the sums. When the week has no chart or a traded
    player is unlisted, the trade values of the two sides do not compare, so recent points per game pick him.
    """
    players = [pid for side in trade.sides for pid in side.gives]
    values = _trade_values(snapshot, handcuffs) if snapshot.chart is not None else {}
    if all(pid in values for pid in players):
        worth = {pid: Decimal(str(values[pid])) for pid in players}
    else:
        worth = {pid: recent_points_per_game(snapshot, pid) for pid in players}
    top = max(worth.values())
    leaders = [pid for pid, w in worth.items() if w == top]
    return leaders[0] if len(leaders) == 1 else None


def grade(trade: ProposedTrade, snapshot: Snapshot) -> tuple[Breakdown, Breakdown]:
    """The breakdown of each side, in the order of trade.sides. It raises TradeInputError on a bad trade."""
    check_trade(trade, snapshot)
    a, b = trade.sides
    # The handcuffs come first, because the start letter sums and the highest-value player count them at zero.
    handcuffs = trade_handcuffs(trade, snapshot)
    top = _highest_value_player(trade, snapshot, handcuffs)
    sides = (build_side(snapshot, a.roster_id, a.gives, b.gives, top, handcuffs),
             build_side(snapshot, b.roster_id, b.gives, a.gives, top, handcuffs))
    starts = _start_letters(trade, snapshot, handcuffs)
    return tuple(  # type: ignore[return-value]
        start.model_copy(update={"adjusters": [adjuster(snapshot, side) for adjuster in ADJUSTERS]})
        for start, side in zip(starts, sides)
    )
