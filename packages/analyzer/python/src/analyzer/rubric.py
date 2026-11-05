"""
The trade analyzer rubric in code: the proposed trade, its input check, each side's grade, the verdict, and fairness.
The grade gives each side a start letter, runs the adjusters in ADJUSTERS, and clamps their sum into a final letter.
"""
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, model_validator

from analyzer.adjusters import (
    ADJUSTERS,
    SCHEDULE,
    Adjuster,
    Lean,
    Side,
    build_side,
    named,
    one_for_many,
    trade_handcuffs,
)
from analyzer.tunables import (
    ACCEPT_AT_OR_ABOVE,
    CLAMP_STEPS,
    CONSOLIDATION_MARGIN,
    DECLINE_AT_OR_BELOW,
    LOPSIDED_AT_OR_BELOW,
    START_LETTER_BANDS,
    UNEVEN_MARGIN,
    WIN_WIN_AT_OR_ABOVE,
)
from league.ranks import lineup_value
from league.snapshot import Snapshot

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
UNEVEN_REASON = "The side with more players counts its extra player at a discount before the sides count as even."
NO_CHART_REASON = "The week has no trade values, so the chart gives neither side an edge."
# The end of the reason for a trade with an unlisted player. The result document reads it to pick its deal row.
UNLISTED_REASON_END = " no trade value, so the chart gives neither side an edge."

# The line the site shows when the trade week has no chart, and the deal row of each side then. The grade then reads
# the adjusters alone. It names no source, so a manager reads plain advice and never the inner parts of the grade.
NO_CHART_NOTE = "This week's player values are not out yet, so both sides start even."
# The deal row of a side, from its start letter. Its words name no source of the values, so the row reads as plain
# advice. The result document shows it as the first factor, and the fairness line shows it with no step up.
DEAL_REASONS = {
    "A": "You get far more than you give.",
    "B": "You get more than you give.",
    "C": "What you get and what you give are about even.",
    "D": "You give more than you get.",
    "F": "You give far more than you get.",
}
# Any uneven count divides the sum of the side with more players by a margin before the sides compare.
CONSOLIDATION_DEAL = ", after a discount on the side with more players."
UNLISTED_DEAL = "Not every player in the trade has a value this week, so both sides start even."


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
    # The roster id of the side that asked. The verdict is for this side.
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


def _all_at_c(trade: ProposedTrade, reason: str) -> tuple[tuple[Letter, str], ...]:
    return tuple(("C", reason) for _ in trade.sides)


def _trade_values(snapshot: Snapshot, handcuffs: list[str]) -> dict[str, float]:
    """The trade value of each player on the chart, with every handcuff in the trade at zero, listed or not.

    A player out for the season and off the chart is at zero too. ADR 0005: he counts zero for the side that gets
    him, listed or not, so he is never unlisted. A listed one keeps his chart value for the side that gives him.
    """
    off_chart_season = {pid: 0.0 for pid in snapshot.out_for_season if pid not in snapshot.chart.values}
    return {**snapshot.chart.values, **off_chart_season, **{pid: 0.0 for pid in handcuffs}}


def unlisted_players(snapshot: Snapshot, players: list[str], handcuffs: list[str] | None = None) -> list[str]:
    """The players with no trade value on the week's chart. A handcuff in the trade counts as listed, at zero.

    A player out for the season counts as listed, at zero.
    A trade with an unlisted player starts every side at C. With no chart, every player is unlisted.
    """
    if snapshot.chart is None:
        return list(players)
    values = _trade_values(snapshot, handcuffs or [])
    return [pid for pid in players if pid not in values]


def _start_letters(
    trade: ProposedTrade, snapshot: Snapshot, handcuffs: list[str],
) -> tuple[tuple[Letter, str], ...]:
    """The start letter and its reason for each side, in the order of trade.sides, before any adjuster.
    A handcuff counts as zero in the sums."""
    if snapshot.chart is None:
        return _all_at_c(trade, NO_CHART_REASON)
    values = _trade_values(snapshot, handcuffs)
    unlisted = unlisted_players(snapshot, trade.player_ids, handcuffs)
    if unlisted:
        reason = named(snapshot, unlisted, "has", "have") + UNLISTED_REASON_END
        return _all_at_c(trade, reason)

    def start(side: TradeSide) -> tuple[Letter, str]:
        gives, gets = side.player_ids, trade.gets(side.roster_id)
        # Decimal sums keep half-point trade values exact, so a ratio at a band's lower bound stays in that band.
        gave = sum((Decimal(str(values[pid])) for pid in gives), Decimal(0))
        # ADR 0005: the side that gets a player out for the season buys nothing, so he counts zero in what it gets.
        # The side that gives him still gives his full chart value, so the fairness reads lopsided on its own.
        got = sum((Decimal(str(values[pid])) for pid in gets if pid not in snapshot.out_for_season), Decimal(0))
        # Each side reads its own gives and gets, so in a two-side trade both sides use the same margin or neither does.
        margin, margin_reason = _margin(len(gives), len(gets))
        if margin is not None:
            # The side with more players is the depth, and its sum is the one the margin divides.
            if len(gives) > len(gets):
                gave /= margin
            else:
                got /= margin
        letter = _letter(got, gave)
        return letter, BAND_REASONS[letter] + (" " + margin_reason if margin_reason else "")

    return tuple(start(side) for side in trade.sides)


def _margin(gives: int, gets: int) -> tuple[Decimal | None, str]:
    """The margin that divides the sum of the side with more players, and the start reason that names it.

    One player for two or more uses CONSOLIDATION_MARGIN. Two or more for a larger count uses UNEVEN_MARGIN.
    An even count uses none.
    """
    if gives == gets:
        return None, ""
    if one_for_many(gives, gets):
        return CONSOLIDATION_MARGIN, CONSOLIDATION_REASON
    return UNEVEN_MARGIN, UNEVEN_REASON


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


def _final_letter(start: Letter, adjusters: list[Adjuster]) -> Letter:
    """The start letter moved by the sum of the steps. The sum clamps to CLAMP_STEPS either way,
    the letter to A to F."""
    total = max(-CLAMP_STEPS, min(CLAMP_STEPS, sum(adjuster.step for adjuster in adjusters)))
    return LETTERS[max(0, min(len(LETTERS) - 1, LETTERS.index(start) - total))]


def build_sides(trade: ProposedTrade, snapshot: Snapshot, handcuffs: list[str]) -> tuple[Side, ...]:
    """The reads of each side, in the order of trade.sides: the best lineup, its slots, and the holes.

    The grade and the trade fact sheet both read the sides here, so the facts name the same slots the grade reads.
    """
    top = _highest_value_player(trade, snapshot, handcuffs)
    return tuple(build_side(snapshot, side.roster_id, side.player_ids, trade.gets(side.roster_id), top, handcuffs)
                 for side in trade.sides)


def grade(trade: ProposedTrade, snapshot: Snapshot) -> tuple[Breakdown, ...]:
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
    return tuple(breakdowns)


def _at_or_above(letter: Letter, bound: Letter) -> bool:
    return LETTERS.index(letter) <= LETTERS.index(bound)


def _at_or_below(letter: Letter, bound: Letter) -> bool:
    return LETTERS.index(letter) >= LETTERS.index(bound)


def verdict(trade: ProposedTrade, breakdowns: tuple[Breakdown, ...]) -> Verdict:
    """The code's default verdict for the asker, from the final letters of every side and the asker's schedule lean.

    With three or more sides, the verdict compares the asker's letter with the letter of the best other side.
    When that side does better, the reason reads "Another side does better, so ask for more."
    """
    asker = next(b for b in breakdowns if b.roster_id == trade.asker)
    others = [b for b in breakdowns if b.roster_id != trade.asker]
    # The asker compares with the best other side, so a middle letter accepts only when no other side does better.
    mine = asker.final_letter
    theirs = min((b.final_letter for b in others), key=LETTERS.index)
    lean = asker.lean
    # The reasons reach the result document, which gives a decision, so they name no letter.
    if _at_or_above(mine, ACCEPT_AT_OR_ABOVE):
        return Verdict(choice="accept", reason="The trade favors the asking side.")
    if _at_or_below(mine, DECLINE_AT_OR_BELOW):
        return Verdict(choice="decline", reason="The trade costs the asking side too much.")
    # The letters between the two bands accept only when the other side does no better than the asker.
    # A two-side trade keeps its words. A trade of three or more names the best other side as "another side".
    two_sides = len(others) == 1
    if mine == theirs:
        sides = ("The two sides are about even" if two_sides
                 else "The asking side and the best other side are about even")
    elif _at_or_above(mine, theirs):
        sides = "The asking side does better"
    else:
        sides = "The other side does better" if two_sides else "Another side does better"
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


def deal_reason(breakdown: Breakdown) -> str:
    """The deal row of one side in plain words, from its start letter and the case of its start reason.

    The start reason names the chart for the prompt, so the row reads the case from it and writes its own words.
    """
    if breakdown.reason == NO_CHART_REASON:
        return NO_CHART_NOTE
    if breakdown.reason.endswith(UNLISTED_REASON_END):
        return UNLISTED_DEAL
    if CONSOLIDATION_REASON in breakdown.reason or UNEVEN_REASON in breakdown.reason:
        return DEAL_REASONS[breakdown.start_letter].removesuffix(".") + CONSOLIDATION_DEAL
    return DEAL_REASONS[breakdown.start_letter]


def _gain_reason(breakdown: Breakdown) -> str:
    """The reason of the first adjuster with a step up, in rubric order, else the deal row of the side."""
    # A step up is what a side gains past the trade values, so it is the reason the side would take the trade.
    # The fairness line shows it to a manager, so it reads the plain deal row, not the start reason of the prompt.
    return next((a.reason for a in breakdown.adjusters if a.step > 0), deal_reason(breakdown))


def fairness(letters: tuple[Letter, ...], breakdowns: tuple[Breakdown, ...]) -> Fairness:
    """Both inputs come in the order of the trade's sides. The letters are the ones that stand after the Claude call."""
    sides = list(zip(letters, breakdowns))
    if all(_at_or_above(letter, WIN_WIN_AT_OR_ABOVE) for letter, _ in sides):
        state, gives_more = "win_win", None
    elif any(_at_or_below(letter, LOPSIDED_AT_OR_BELOW) for letter, _ in sides):
        state = "lopsided"
        # The lowest final letter gives more, then the lowest start letter. max keeps the first side at a full tie.
        _, giver = max(sides, key=lambda side: (LETTERS.index(side[0]), LETTERS.index(side[1].start_letter)))
        gives_more = giver.roster_id
    else:
        state, gives_more = "fair", None
    return Fairness(state=state, gives_more=gives_more,
                    sides=tuple(FairnessSide(roster_id=b.roster_id, reason=_gain_reason(b)) for _, b in sides))
