"""
The trade analyzer rubric in code: the proposed trade, its input check, each side's grade, the verdict, and fairness.
The grade gives each side a start letter, runs the adjusters in ADJUSTERS, and clamps their sum into a final letter.
"""
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, model_validator

from cornerstone.adjusters import (
    ADJUSTERS, SCHEDULE, Adjuster, Lean, Side, build_side, lineup_value, named, trade_handcuffs,
)
from cornerstone.snapshot import Snapshot
from cornerstone.tunables import (
    ACCEPT_AT_OR_ABOVE, CLAMP_STEPS, CONSOLIDATION_MARGIN, DECLINE_AT_OR_BELOW, LOPSIDED_AT_OR_BELOW,
    START_LETTER_BANDS, WIN_WIN_AT_OR_ABOVE,
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
NO_CHART_REASON = "The week has no trade values, so the chart gives neither side an edge."


class TradeInputError(ValueError):
    """A proposed trade that does not fit the snapshot, such as a player who is not on the giving roster."""

    def __init__(self, message: str, player_id: str | None = None) -> None:
        super().__init__(message)
        self.player_id = player_id


class GivenPlayer(BaseModel):
    """One player a side gives and the roster id of the side he goes to."""

    player_id: str
    # Every given player names his destination, in a two-side trade too, so the API checks one shape (ADR 0003).
    to: int


class TradeSide(BaseModel):
    """One roster in a proposed trade and the players it gives. What it gets derives from the other sides."""

    roster_id: int
    gives: list[GivenPlayer]

    @property
    def player_ids(self) -> list[str]:
        """The ids of the players this side gives, in order, with no destination."""
        return [given.player_id for given in self.gives]


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
        given = a.player_ids + b.player_ids
        if len(set(given)) != len(given):
            raise ValueError("A player can appear only once in a proposed trade")
        if self.asker not in (a.roster_id, b.roster_id):
            raise ValueError(f"The asker {self.asker} is not one of the two rosters in the trade")
        rosters = [side.roster_id for side in self.sides]
        for side in self.sides:
            for player in side.gives:
                if player.to not in rosters:
                    raise ValueError(f"Player {player.player_id} goes to roster {player.to}, "
                                     "which is not a side of the trade")
        # The gets check runs before the own-roster check. With two sides a side that gets nothing has a player
        # sent home on the other side, and the missing gets is the plainer fault to name.
        for side in self.sides:
            if not self.gets(side.roster_id):
                raise ValueError(f"Roster {side.roster_id} gets no player in the trade")
        for side in self.sides:
            for player in side.gives:
                if player.to == side.roster_id:
                    raise ValueError(f"Player {player.player_id} goes to his own roster {side.roster_id}")
        return self

    def gets(self, roster_id: int) -> list[str]:
        """The ids of the players the other sides send to `roster_id`, in the order of the sides."""
        return [player.player_id for side in self.sides if side.roster_id != roster_id
                for player in side.gives if player.to == roster_id]


class Breakdown(BaseModel):
    """The grade of one side: the start letter, the reason for it, each adjuster in rubric order,
    and the final letter."""

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


class FairnessSide(BaseModel):
    """One side of the fairness: the roster and the one reason that says what it gains."""

    roster_id: int
    reason: str


class Fairness(BaseModel):
    """Whether the trade is good for both sides, fair, or lopsided, with one reason per side.

    It is for both sides, not only the asker, so a manager knows if the other side will take the trade.
    """

    state: Literal["win_win", "fair", "lopsided"]
    # None when no side gives more, so a win-win or a fair trade names no loser.
    gives_more: int | None
    # In the order of the trade's sides, so the block lines up with the sides of the document.
    sides: tuple[FairnessSide, FairnessSide]


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


def unlisted_players(snapshot: Snapshot, players: list[str], handcuffs: list[str] | None = None) -> list[str]:
    """The players with no trade value on the week's chart. A handcuff in the trade counts as listed, at zero.

    A trade with an unlisted player starts both sides at C. With no chart, every player is unlisted.
    """
    if snapshot.chart is None:
        return list(players)
    values = _trade_values(snapshot, handcuffs or [])
    return [pid for pid in players if pid not in values]


def _start_letters(
    trade: ProposedTrade, snapshot: Snapshot, handcuffs: list[str],
) -> tuple[tuple[Letter, str], tuple[Letter, str]]:
    """The start letter and its reason for each side, as a pair, before any adjuster.
    A handcuff counts as zero in the sums."""
    a, b = trade.sides
    if snapshot.chart is None:
        return _both_at_c(NO_CHART_REASON)
    values = _trade_values(snapshot, handcuffs)
    unlisted = unlisted_players(snapshot, [pid for side in trade.sides for pid in side.player_ids], handcuffs)
    if unlisted:
        reason = (named(snapshot, unlisted, "has", "have")
                  + " no trade value, so the chart gives neither side an edge.")
        return _both_at_c(reason)
    # Decimal sums keep half-point trade values exact, so a ratio at a band's lower bound stays in that band.
    sum_a = sum((Decimal(str(values[pid])) for pid in a.player_ids), Decimal(0))
    sum_b = sum((Decimal(str(values[pid])) for pid in b.player_ids), Decimal(0))
    # Only one player for two or more is a consolidation. A three-for-two trade gets no discount.
    consolidation = (len(a.player_ids) == 1) != (len(b.player_ids) == 1)
    if consolidation:
        if len(a.player_ids) > 1:
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
    player is unlisted, the trade values of the two sides do not compare, so the lineup value picks him.
    The lineup value is recent points per game, or the projection ahead of a player due back, who has no recent games.
    """
    players = [pid for side in trade.sides for pid in side.player_ids]
    values = _trade_values(snapshot, handcuffs) if snapshot.chart is not None else {}
    if all(pid in values for pid in players):
        worth = {pid: Decimal(str(values[pid])) for pid in players}
    else:
        # A handcuff counts as zero here too, so a handcuff due back with a high projection is never the pick.
        worth = {pid: Decimal(0) if pid in handcuffs else lineup_value(snapshot, pid) for pid in players}
    top = max(worth.values())
    leaders = [pid for pid, w in worth.items() if w == top]
    return leaders[0] if len(leaders) == 1 else None


def _final_letter(start: Letter, adjusters: list[Adjuster]) -> Letter:
    """The start letter moved by the sum of the steps. The sum clamps to CLAMP_STEPS either way,
    the letter to A to F."""
    total = max(-CLAMP_STEPS, min(CLAMP_STEPS, sum(adjuster.step for adjuster in adjusters)))
    return LETTERS[max(0, min(len(LETTERS) - 1, LETTERS.index(start) - total))]


def build_sides(trade: ProposedTrade, snapshot: Snapshot, handcuffs: list[str]) -> tuple[Side, Side]:
    """The reads of each side, in the order of trade.sides: the best lineup, its slots, and the holes.

    The grade and the trade fact sheet both read the sides here, so the facts name the same slots the grade reads.
    """
    a, b = trade.sides
    top = _highest_value_player(trade, snapshot, handcuffs)
    return (build_side(snapshot, a.roster_id, a.player_ids, trade.gets(a.roster_id), top, handcuffs),
            build_side(snapshot, b.roster_id, b.player_ids, trade.gets(b.roster_id), top, handcuffs))


def grade(trade: ProposedTrade, snapshot: Snapshot) -> tuple[Breakdown, Breakdown]:
    """The breakdown of each side, in the order of trade.sides. It raises TradeInputError on a bad trade."""
    check_trade(trade, snapshot)
    # The handcuffs come first, because the start letter sums and the highest-value player count them at zero.
    handcuffs = trade_handcuffs(trade, snapshot)
    sides = build_sides(trade, snapshot, handcuffs)
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
    # The reasons reach the result document, which gives a decision, so they name no letter.
    if _at_or_above(mine, ACCEPT_AT_OR_ABOVE):
        return Verdict(choice="accept", reason="The trade favors the asking side.")
    if _at_or_below(mine, DECLINE_AT_OR_BELOW):
        return Verdict(choice="decline", reason="The trade costs the asking side too much.")
    # The letters between the two bands accept only when the other side does no better than the asker.
    if mine == theirs:
        sides = "The two sides are about even"
    elif _at_or_above(mine, theirs):
        sides = "The asking side does better"
    else:
        sides = "The other side does better"
    if _at_or_above(mine, theirs):
        # Schedule is the tie break between fair and not quite fair. It never turns a clear letter.
        if lean == "against":
            return Verdict(choice="counter",
                           reason=f"{sides}, but the schedule leans against the asking side, so ask for more.")
        return Verdict(choice="accept", reason=f"{sides}, so the trade is fair.")
    if lean == "for":
        return Verdict(choice="accept",
                       reason=f"{sides}, but the schedule leans for the asking side, so the trade is worth it.")
    return Verdict(choice="counter", reason=f"{sides}, so ask for more.")


def _gain_reason(breakdown: Breakdown) -> str:
    """The reason of the first adjuster with a step up, in rubric order, else the reason of the start letter."""
    # A step up is what a side gains past the trade values, so it is the reason the side would take the trade.
    return next((a.reason for a in breakdown.adjusters if a.step > 0), breakdown.reason)


def fairness(letters: tuple[Letter, Letter], breakdowns: tuple[Breakdown, Breakdown]) -> Fairness:
    """Both inputs come in the order of the trade's sides. The letters are the ones that stand after the Claude call."""
    sides = list(zip(letters, breakdowns))
    if all(_at_or_above(letter, WIN_WIN_AT_OR_ABOVE) for letter, _ in sides):
        state, gives_more = "win_win", None
    elif any(_at_or_below(letter, LOPSIDED_AT_OR_BELOW) for letter, _ in sides):
        state = "lopsided"
        # The lower final letter gives more, then the lower start letter. max keeps the first side at a full tie.
        _, giver = max(sides, key=lambda side: (LETTERS.index(side[0]), LETTERS.index(side[1].start_letter)))
        gives_more = giver.roster_id
    else:
        state, gives_more = "fair", None
    return Fairness(state=state, gives_more=gives_more,
                    sides=tuple(FairnessSide(roster_id=b.roster_id, reason=_gain_reason(b)) for _, b in sides))
