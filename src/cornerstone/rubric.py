"""
The trade analyzer rubric in code: the proposed trade, its input check, the grade of each side, and the verdict.
The grade gives each side a start letter, runs the adjusters in ADJUSTERS, and clamps their sum into a final letter.
"""
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, model_validator

from cornerstone.adjusters import (
    ADJUSTERS, SCHEDULE, Adjuster, Lean, build_side, named, recent_points_per_game, trade_handcuffs,
)
from cornerstone.snapshot import Snapshot
from cornerstone.tunables import (
    ACCEPT_AT_OR_ABOVE, CLAMP_STEPS, CONSOLIDATION_MARGIN, DECLINE_AT_OR_BELOW, START_LETTER_BANDS,
)

# The breakdown per side holds no trade value, sum, or ratio.

Letter = Literal["A", "B", "C", "D", "F"]
# The letters from the best down, so a step up moves one place toward the front.
LETTERS: tuple[Letter, ...] = ("A", "B", "C", "D", "F")

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
    """The grade of one side: the start letter, the reason for it, each adjuster in rubric order, and the final letter."""

    roster_id: int
    start_letter: Letter
    reason: str
    adjusters: list[Adjuster] = []
    # The start letter moved by the sum of the adjuster steps, clamped to CLAMP_STEPS either way.
    final_letter: Letter

    @property
    def lean(self) -> Lean | None:
        """The lean of the schedule adjuster, or None when the side has none."""
        return next((a.lean for a in self.adjusters if a.name == SCHEDULE), None)


class Verdict(BaseModel):
    """Accept, counter, or decline, for the side that asked, with one reason."""

    choice: Literal["accept", "counter", "decline"]
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
                # A player who left the league is not in snapshot.players, so the id stands in for the name.
                player = snapshot.players.get(pid)
                name = player.name if player else pid
                raise TradeInputError(f"{name} is no longer on {snapshot.teams[side.roster_id].name}.", player_id=pid)


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


def _both_at_c(reason: str) -> tuple[tuple[Letter, str], tuple[Letter, str]]:
    return ("C", reason), ("C", reason)


def _trade_values(snapshot: Snapshot, handcuffs: list[str]) -> dict[str, float]:
    """The trade value of each player on the chart, with every handcuff in the trade at zero, listed or not."""
    return {**snapshot.chart.values, **{pid: 0.0 for pid in handcuffs}}


def _start_letters(
    trade: ProposedTrade, snapshot: Snapshot, handcuffs: list[str],
) -> tuple[tuple[Letter, str], tuple[Letter, str]]:
    """The start letter and its reason for each side, as a pair, before any adjuster. A handcuff counts as zero in the sums."""
    a, b = trade.sides
    if snapshot.chart is None:
        return _both_at_c(NO_CHART_REASON)
    values = _trade_values(snapshot, handcuffs)
    unlisted = [pid for side in trade.sides for pid in side.gives if pid not in values]
    if unlisted:
        reason = (named(snapshot, unlisted, "has", "have")
                  + " no trade value, so neither side gets a start letter and both start at C.")
        return _both_at_c(reason)
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

    def start(got: Decimal, gave: Decimal) -> tuple[Letter, str]:
        letter = _letter(got, gave)
        return letter, BAND_REASONS[letter] + (" " + CONSOLIDATION_REASON if consolidation else "")

    return start(sum_b, sum_a), start(sum_a, sum_b)


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


def _final_letter(start: Letter, adjusters: list[Adjuster]) -> Letter:
    """The start letter moved by the sum of the steps. The sum clamps to CLAMP_STEPS either way, the letter to A to F."""
    total = max(-CLAMP_STEPS, min(CLAMP_STEPS, sum(adjuster.step for adjuster in adjusters)))
    return LETTERS[max(0, min(len(LETTERS) - 1, LETTERS.index(start) - total))]


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
    breakdowns = []
    for trade_side, (letter, reason), side in zip(trade.sides, starts, sides):
        adjusters = [adjuster(snapshot, side) for adjuster in ADJUSTERS]
        breakdowns.append(Breakdown(roster_id=trade_side.roster_id, start_letter=letter, reason=reason,
                                    adjusters=adjusters, final_letter=_final_letter(letter, adjusters)))
    return breakdowns[0], breakdowns[1]


def _at_or_above(letter: Letter, bound: Letter) -> bool:
    return LETTERS.index(letter) <= LETTERS.index(bound)


def _at_or_below(letter: Letter, bound: Letter) -> bool:
    return LETTERS.index(letter) >= LETTERS.index(bound)


def verdict(trade: ProposedTrade, breakdowns: tuple[Breakdown, Breakdown]) -> Verdict:
    """The code's default verdict for the asker, from the final letters of both sides and the asker's schedule lean."""
    asker = next(b for b in breakdowns if b.roster_id == trade.asker)
    other = next(b for b in breakdowns if b.roster_id != trade.asker)
    mine, theirs = asker.final_letter, other.final_letter
    lean = asker.lean
    if _at_or_above(mine, ACCEPT_AT_OR_ABOVE):
        return Verdict(choice="accept", reason=f"The asking side grades {mine}, so the trade favors it.")
    if _at_or_below(mine, DECLINE_AT_OR_BELOW):
        return Verdict(choice="decline", reason=f"The asking side grades {mine}, so the trade costs it too much.")
    # The letters between the two bands accept only when the other side does no better than the asker.
    grades = f"The asking side grades {mine} and the other side grades {theirs}"
    if _at_or_above(mine, theirs):
        # Schedule is the tie break between fair and not quite fair. It never turns a clear letter.
        if lean == "against":
            return Verdict(choice="counter",
                           reason=f"{grades}, but the schedule leans against the asking side, so ask for more.")
        return Verdict(choice="accept", reason=f"{grades}, so the trade is fair.")
    if lean == "for":
        return Verdict(choice="accept",
                       reason=f"{grades}, but the schedule leans for the asking side, so the trade is worth it.")
    return Verdict(choice="counter", reason=f"{grades}, so ask for more.")
