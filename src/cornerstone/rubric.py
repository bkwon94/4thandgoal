"""
The trade analyzer rubric in code: the proposed trade, its input check, and the grade of each side.
The grade gives each side a start letter, then runs the adjusters in ADJUSTERS, roster fit and standing, in rubric order.
The breakdown per side holds no trade value, sum, or ratio.
"""
from collections.abc import Callable
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, model_validator

from cornerstone.history import player_points
from cornerstone.snapshot import Snapshot
from cornerstone.tunables import (
    CONSOLIDATION_MARGIN,
    FIT_THRESHOLD,
    LINEUP_WEEKS,
    RETURN_BY_WEEK,
    SELLER_GAP,
    START_LETTER_BANDS,
)

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


class Adjuster(BaseModel):
    """One criterion of the rubric for one side: its name, its step of at most one, and a one-line reason."""

    name: str
    step: Literal[-1, 0, 1]
    reason: str


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


def _join(names: list[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def _both_at_c(a: TradeSide, b: TradeSide, reason: str) -> tuple[Breakdown, Breakdown]:
    return (Breakdown(roster_id=a.roster_id, start_letter="C", reason=reason),
            Breakdown(roster_id=b.roster_id, start_letter="C", reason=reason))


def _start_letters(trade: ProposedTrade, snapshot: Snapshot) -> tuple[Breakdown, Breakdown]:
    """The start letter and its reason for each side, before any adjuster."""
    a, b = trade.sides
    if snapshot.chart is None:
        return _both_at_c(a, b, NO_CHART_REASON)
    values = snapshot.chart.values
    unlisted = [pid for side in trade.sides for pid in side.gives if pid not in values]
    if unlisted:
        names = [snapshot.players[pid].name for pid in unlisted]
        verb = "has" if len(names) == 1 else "have"
        reason = f"{_join(names)} {verb} no trade value, so neither side gets a start letter and both start at C."
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


# The tie rule at equal points per game. A position not in the order ranks last.
POSITION_ORDER = ("RB", "WR", "TE", "QB", "K", "DEF")
# The positions each flex slot takes. Any other slot takes its own position only.
FLEX_SLOTS: dict[str, frozenset[str]] = {
    "FLEX": frozenset({"RB", "WR", "TE"}),
    "WRRB_FLEX": frozenset({"RB", "WR"}),
    "REC_FLEX": frozenset({"WR", "TE"}),
    "SUPER_FLEX": frozenset({"QB", "RB", "WR", "TE"}),
}
# Slots that hold players who do not start.
BENCH_SLOTS = frozenset({"BN", "IR", "TAXI"})


def recent_points_per_game(snapshot: Snapshot, player_id: str) -> Decimal:
    """The points per game over the last completed weeks, LINEUP_WEEKS at most. A player with no game has 0."""
    last = snapshot.as_of.stats_through
    played = [
        snapshot.stats.weeks[week] for week in range(max(1, last - LINEUP_WEEKS + 1), last + 1)
        if week in snapshot.stats.weeks
        and (snapshot.stats.weeks[week].stats.get(player_id) or {}).get("gp", 0) > 0
    ]
    if not played:
        return Decimal(0)
    # Sleeper leaves out a stat whose value is 0. A game with no points entry is a game of 0 points.
    total = sum((Decimal(str(player_points(past, player_id) or 0)) for past in played), Decimal(0))
    return total / len(played)


def best_lineup(roster: list[str], slots: list[str], snapshot: Snapshot) -> list[str]:
    """The starters of the roster's best lineup, by recent points per game, with the position order as the tie rule.

    The fixed slots fill first, so a flex slot takes the player with the most points per game that no fixed slot took.
    """
    def position(pid: str) -> str:
        return snapshot.players[pid].position

    def rank(pid: str) -> tuple[Decimal, int, str]:
        order = POSITION_ORDER.index(position(pid)) if position(pid) in POSITION_ORDER else len(POSITION_ORDER)
        # The player id breaks the last tie, so the same roster always gives the same lineup.
        return (-recent_points_per_game(snapshot, pid), order, pid)

    pool = sorted(roster, key=rank)
    starters: list[str] = []
    fixed = [slot for slot in slots if slot not in BENCH_SLOTS and slot not in FLEX_SLOTS]
    flex = [slot for slot in slots if slot in FLEX_SLOTS]
    for slot in fixed + flex:
        allowed = FLEX_SLOTS.get(slot, frozenset({slot}))
        pick = next((pid for pid in pool if pid not in starters and position(pid) in allowed), None)
        if pick is not None:
            starters.append(pick)
    return starters


def _lineup_total(roster: list[str], snapshot: Snapshot) -> Decimal:
    return sum((recent_points_per_game(snapshot, pid)
                for pid in best_lineup(roster, snapshot.roster_positions, snapshot)), Decimal(0))


class _Side(BaseModel):
    """What the adjusters read of one side: the players it gets and gives, and its lineup before and after."""

    roster_id: int
    gets: list[str]
    gives: list[str]
    starters_after: list[str]
    # The best lineup's total after the trade minus the total before.
    lineup_change: Decimal
    # True when the side gets the single highest-value player in the trade.
    gets_highest_value: bool
    # True when the side gives that player.
    gives_highest_value: bool

    @property
    def lineup_gains(self) -> bool:
        return self.lineup_change >= FIT_THRESHOLD

    @property
    def lineup_loses(self) -> bool:
        return -self.lineup_change >= FIT_THRESHOLD


def _highest_value_player(trade: ProposedTrade, snapshot: Snapshot) -> str | None:
    """The single highest-value player in the trade, or None when two or more tie at the top.

    Trade value picks him. When the week has no chart or a traded player is unlisted, the trade values
    of the two sides do not compare, so recent points per game pick him.
    """
    players = [pid for side in trade.sides for pid in side.gives]
    values = snapshot.chart.values if snapshot.chart is not None else {}
    if all(pid in values for pid in players):
        worth = {pid: Decimal(str(values[pid])) for pid in players}
    else:
        worth = {pid: recent_points_per_game(snapshot, pid) for pid in players}
    top = max(worth.values())
    leaders = [pid for pid, w in worth.items() if w == top]
    return leaders[0] if len(leaders) == 1 else None


def _side(snapshot: Snapshot, roster_id: int, gives: list[str], gets: list[str], top: str | None) -> _Side:
    before = snapshot.rosters[roster_id]
    after = [pid for pid in before if pid not in gives] + gets
    return _Side(
        roster_id=roster_id, gets=gets, gives=gives,
        starters_after=best_lineup(after, snapshot.roster_positions, snapshot),
        lineup_change=_lineup_total(after, snapshot) - _lineup_total(before, snapshot),
        gets_highest_value=top in gets,
        gives_highest_value=top in gives,
    )


# The name of each adjuster. The breakdown shows it, so each string lives here only.
ROSTER_FIT = "roster fit"
STANDING = "standing"


def _fit(snapshot: Snapshot, side: _Side) -> Adjuster:
    """Roster fit: the change in the side's best lineup."""
    if side.lineup_loses:
        return Adjuster(name=ROSTER_FIT, step=-1, reason="The best lineup loses after the trade.")
    # In a one-for-two-or-more trade, the side that gets the depth must start every player it gets.
    # Otherwise it pays for a bench player, so neither the gain nor the highest-value player earns the step up.
    gets_depth = len(side.gets) > 1 and len(side.gives) == 1
    if gets_depth and not all(pid in side.starters_after for pid in side.gets):
        if side.lineup_gains:
            return Adjuster(name=ROSTER_FIT, step=0,
                            reason="The best lineup gains after the trade, but not every player it gets starts.")
        return Adjuster(name=ROSTER_FIT, step=0, reason="Not every player it gets starts.")
    if side.lineup_gains:
        return Adjuster(name=ROSTER_FIT, step=1, reason="The best lineup gains after the trade.")
    # A lineup change smaller than the fit threshold is no lineup loss, so it does not block this step.
    if side.gets_highest_value:
        return Adjuster(name=ROSTER_FIT, step=1,
                        reason="It gets the highest-value player in the trade, and the best lineup does not lose.")
    return Adjuster(name=ROSTER_FIT, step=0, reason="The best lineup stays about the same.")


# Injury report statuses that keep a player out of games. A player with one of them and no row in the
# returns file has no known return, so the standing adjuster counts him as back after RETURN_BY_WEEK.
OUT_STATUSES = frozenset({"Out", "IR", "NA", "Sus", "PUP"})


def _race(snapshot: Snapshot, roster_id: int) -> Literal["contender", "seller", "middle"]:
    """Where the team stands by record. The standings rank by wins, then by points for."""
    standing = next(s for s in snapshot.standings if s.roster_id == roster_id)
    if standing.in_playoffs:
        return "contender"
    # games_from_cut is the team's wins minus the wins of the team in the last playoff spot.
    if -standing.games_from_cut > SELLER_GAP:
        return "seller"
    return "middle"


def _return_bet(snapshot: Snapshot, player_id: str) -> bool:
    """True when the returns file has the player due back after the last completed week and by RETURN_BY_WEEK."""
    week = snapshot.returns.get(player_id)
    return week is not None and snapshot.as_of.stats_through < week <= RETURN_BY_WEEK


def _late_return(snapshot: Snapshot, player_id: str) -> str | None:
    """Why the player is not back by RETURN_BY_WEEK, or None when he is back by then or is not out."""
    week = snapshot.returns.get(player_id)
    if week is not None:
        return "is not due back before the playoffs" if week > RETURN_BY_WEEK else None
    if snapshot.players[player_id].injury_status in OUT_STATUSES:
        return "has no return week on file"
    return None


def _standing(snapshot: Snapshot, side: _Side) -> Adjuster:
    """Standing: a contender's win-now move or return bet, and a seller's bet on the future."""
    race = _race(snapshot, side.roster_id)
    if race == "contender":
        lead = "The team holds a playoff spot"
        if side.lineup_gains:
            return Adjuster(name=STANDING, step=1, reason=f"{lead}, and the best lineup gains now.")
        bets = [pid for pid in side.gets if _return_bet(snapshot, pid)]
        if bets:
            names = _join([snapshot.players[pid].name for pid in bets])
            verb = "is" if len(bets) == 1 else "are"
            return Adjuster(name=STANDING, step=1, reason=f"{lead}, and {names} {verb} due back before the playoffs.")
        late = [(pid, why) for pid in side.gets if (why := _late_return(snapshot, pid)) is not None]
        if side.lineup_loses and late:
            pid, why = late[0]
            return Adjuster(name=STANDING, step=-1,
                            reason=f"{lead}, but the best lineup loses now for {snapshot.players[pid].name}, who {why}.")
        return Adjuster(name=STANDING, step=0, reason=f"{lead}, and the trade is no win-now move or return bet.")
    if race == "seller":
        lead = "The team is out of the playoff race"
        if side.gets_highest_value:
            return Adjuster(name=STANDING, step=1,
                            reason=f"{lead}, and it gets the highest-value player in the trade.")
        if side.gives_highest_value and side.lineup_gains:
            return Adjuster(name=STANDING, step=-1,
                            reason=f"{lead}, but it gives the highest-value player in the trade for a lineup gain now.")
        return Adjuster(name=STANDING, step=0, reason=f"{lead}, and the trade is no bet on the future.")
    return Adjuster(name=STANDING, step=0, reason="The team is neither in a playoff spot nor out of the race.")


# The adjusters in rubric order. Each takes the snapshot and one side, and grade runs them in this order.
ADJUSTERS: tuple[Callable[[Snapshot, _Side], Adjuster], ...] = (_fit, _standing)


def grade(trade: ProposedTrade, snapshot: Snapshot) -> tuple[Breakdown, Breakdown]:
    """The breakdown of each side, in the order of trade.sides. It raises TradeInputError on a bad trade."""
    check_trade(trade, snapshot)
    a, b = trade.sides
    top = _highest_value_player(trade, snapshot)
    sides = (_side(snapshot, a.roster_id, a.gives, b.gives, top),
             _side(snapshot, b.roster_id, b.gives, a.gives, top))
    starts = _start_letters(trade, snapshot)
    return tuple(  # type: ignore[return-value]
        start.model_copy(update={"adjusters": [adjuster(snapshot, side) for adjuster in ADJUSTERS]})
        for start, side in zip(starts, sides)
    )
