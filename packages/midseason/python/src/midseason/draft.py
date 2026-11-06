"""
The draft steals, busts, and letdowns of the midseason report, the first chapter of Act II: each pick's cost rank at its
position against its points rank, with the injury tag of a bust, and the dear picks with no recent top week. Ticket 20.
"""
from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from facts.tokens import Nums, fact
from league.history import player_points
from league.models import Fact, History, PastWeek
from league.numbers import r2
from league.provider.raw import DraftType

InjuryTag = Literal["hurt", "just bad"]
# A bust was drafted as a starter, and a steal plays like a starter now: the top 12 at QB and TE, the top 24 at RB
# and WR. Kickers and defenses are out. Decision ticket 02.
STARTER_RANK: dict[str, int] = {"QB": 12, "TE": 12, "RB": 24, "WR": 24}
# The page shows the top 5 steals and the top 5 busts per league.
LIST_SIZE = 5
# A bust who missed this many games with an injury is "hurt". The tag changes the roast, not the rank.
HURT_GAMES = 2
# A letdown has a price in the top 10 of the whole draft, and no week in the top 17 of his position in his last 4 weeks
# played. Ticket 20.
LETDOWN_PRICE_RANK = 10
LETDOWN_WEEK_RANK = 17
LETDOWN_WEEKS = 4


class DraftPick(BaseModel):
    """One pick of the league's own draft, as the app maps it from the provider."""
    player_id: str
    name: str
    position: str
    # The drafter. The drafter owns the label of the pick, after a trade or a drop too.
    roster_id: int
    pick_no: int
    # The auction price in dollars. None in a snake or a linear draft.
    price: int | None


class DraftRow(BaseModel):
    """One steal or bust: the cost and the points of the pick, and their ranks among the drafted players of the
    position."""
    player_id: str
    name: str
    position: str
    roster_id: int
    # The name of the drafter's team.
    team: str
    # The price in dollars in an auction, the pick number in a snake.
    cost: int
    cost_rank: int
    # The player's points of weeks 1 to the report week, on any roster or none.
    points: float
    points_rank: int
    # The cost rank minus the points rank. A steal has a high swing, and a bust has a low one.
    swing: int
    # The injury tag of a bust. None on a steal, and None on a bust when the build has no injury report.
    tag: InjuryTag | None = None


class Letdown(DraftRow):
    """A dear pick that is not a bust, with no top week of late. `points_rank` is his season rank at the position."""
    # The rank of the price among all picks of the draft, the top price first. In a snake it is the pick number.
    price_rank: int
    # The last week of weeks 1 to the report week in the top 17 of his position. None when he has no such week.
    last_top_week: int | None


class DraftValue(BaseModel):
    """The facts of the draft: the draft type, then the top steals, the top busts, and the letdowns."""
    draft_type: DraftType
    steals: list[DraftRow]
    busts: list[DraftRow]
    letdowns: list[Letdown]


def _season_points(history: History, player_id: str, through: int) -> float:
    # Exact decimals, so a sum of many weeks never drifts. A week with no points for the player adds 0.
    total = sum((Decimal(str(player_points(history.weeks[w], player_id) or 0)) for w in range(1, through + 1)),
                Decimal(0))
    return r2(float(total))


def _week_rank(past: PastWeek, player_id: str) -> int | None:
    """The rank of the player's points in `past` among all players of his position with a stat line, or None when he
    did not play that week. A player with no stat line or with no active game did not play."""
    if (past.stats.get(player_id) or {}).get("gms_active", 0) < 1:
        return None
    position = past.positions.get(player_id)
    mine = player_points(past, player_id) or 0
    return 1 + sum((player_points(past, other) or 0) > mine
                   for other, other_position in past.positions.items() if other_position == position)


def _letdown(row: DraftRow, price_rank: int, history: History, through: int) -> Letdown | None:
    """The letdown of `row`, or None when he has a top week in his last weeks played."""
    played = [(week, rank) for week in range(1, through + 1) if week in history.weeks
              for rank in [_week_rank(history.weeks[week], row.player_id)] if rank is not None]
    if any(rank <= LETDOWN_WEEK_RANK for _, rank in played[-LETDOWN_WEEKS:]):
        return None
    top_weeks = [week for week, rank in played if rank <= LETDOWN_WEEK_RANK]
    return Letdown(**row.model_dump(), price_rank=price_rank, last_top_week=top_weeks[-1] if top_weeks else None)


def draft_value(
    picks: Sequence[DraftPick], draft_type: DraftType, history: History, through: int, names: Mapping[int, str],
    injured_games: Mapping[str, int] | None,
) -> DraftValue:
    """The top steals, the top busts, and the letdowns of the draft over weeks 1 to `through` of `history`.

    The cost rank orders the picks of a position by price, high first, in an auction, and by pick number in a snake.
    A tie in price breaks by the order of sale, as a snake breaks by the pick number, so each pick has its own cost
    rank. The points rank counts the drafted players of the position with more points, plus one.
    A letdown is a pick of a top 10 price of the whole draft, not a bust, with no week in the top 17 of his position
    in his last 4 weeks played. The weekly rank reads the points of the league scoring.
    `injured_games` is the count of games each player missed with an injury. None means the build has no injury report.
    """
    rows: list[DraftRow] = []
    for position in STARTER_RANK:
        group = [pick for pick in picks if pick.position == position]
        by_cost = sorted(group, key=lambda pick: (-(pick.price or 0) if draft_type == "auction" else 0, pick.pick_no))
        points = {pick.player_id: _season_points(history, pick.player_id, through) for pick in group}
        for cost_rank, pick in enumerate(by_cost, start=1):
            points_rank = 1 + sum(other > points[pick.player_id] for other in points.values())
            rows.append(DraftRow(
                player_id=pick.player_id, name=pick.name, position=position, roster_id=pick.roster_id,
                team=names[pick.roster_id],
                cost=pick.price if draft_type == "auction" and pick.price is not None else pick.pick_no,
                cost_rank=cost_rank, points=points[pick.player_id], points_rank=points_rank,
                swing=cost_rank - points_rank))
    # A tie in swing goes to the cheaper pick for a steal and to the dearer pick for a bust.
    steals = sorted((row for row in rows if row.swing > 0 and row.points_rank <= STARTER_RANK[row.position]),
                    key=lambda row: (-row.swing, -row.cost_rank))[:LIST_SIZE]
    busts = sorted((row for row in rows if row.swing < 0 and row.cost_rank <= STARTER_RANK[row.position]),
                   key=lambda row: (row.swing, row.cost_rank))[:LIST_SIZE]
    # The price rank counts every pick of the draft, kickers and defenses too, by the order of the cost rank.
    by_price = sorted(picks, key=lambda pick: (-(pick.price or 0) if draft_type == "auction" else 0, pick.pick_no))
    price_ranks = {pick.player_id: rank for rank, pick in enumerate(by_price, start=1)}
    bust_ids = {row.player_id for row in busts}
    letdowns = [letdown for row in sorted(rows, key=lambda row: price_ranks[row.player_id])
                if price_ranks[row.player_id] <= LETDOWN_PRICE_RANK and row.player_id not in bust_ids
                for letdown in [_letdown(row, price_ranks[row.player_id], history, through)] if letdown is not None]
    return DraftValue(
        draft_type=draft_type,
        steals=steals,
        letdowns=letdowns,
        busts=[row.model_copy(update={"tag": None if injured_games is None else
                                      "hurt" if injured_games.get(row.player_id, 0) >= HURT_GAMES else "just bad"})
               for row in busts],
    )


def _cost_text(draft: DraftValue, row: DraftRow, n: Nums) -> str:
    """The price of an auction pick, or the pick number of a snake pick. A snake pick never shows a dollar sign."""
    if draft.draft_type == "auction":
        return f"for ${n(row.cost)}"
    return f"with pick {n(row.cost)}"


def draft_facts(draft: DraftValue) -> list[Fact]:
    """The facts of the draft steals, busts, and letdowns: the pick and the points of each row, the tag of a bust, and
    the last top week of a letdown.

    Each fact holds two numbers at most, so its text fits one sentence of a blurb.
    """
    facts = []
    for kind, rows in (("steal", draft.steals), ("bust", draft.busts)):
        for row in rows:
            prefix = f"DV.{kind}.{row.player_id}"
            n = Nums()
            facts.append(fact(prefix, f"{row.team} drafted {row.name} {_cost_text(draft, row, n)}.", n, [row.team],
                              [row.name]))
            n = Nums()
            facts.append(fact(f"{prefix}.points",
                              f"{row.name} is the {n.ord(row.points_rank)} drafted {row.position} by points, with "
                              f"{n(row.points)} points.", n, [], [row.name]))
            if row.tag is not None:
                facts.append(fact(f"{prefix}.tag", f"The bust of {row.name} is tagged {row.tag}.", Nums(), [row.team],
                                  [row.name]))
    for row in draft.letdowns:
        prefix = f"DV.letdown.{row.player_id}"
        n = Nums()
        cost = _cost_text(draft, row, n)
        # A snake pick number is its price rank already, so only an auction names the rank.
        rank = f", the {n.ord(row.price_rank)} price of the draft" if draft.draft_type == "auction" else ""
        facts.append(fact(prefix, f"{row.team} drafted {row.name} {cost}{rank}.", n, [row.team],
                          [row.name]))
        n = Nums()
        facts.append(fact(f"{prefix}.points", f"{row.name} is the {n.ord(row.points_rank)} drafted {row.position} by "
                          f"points.", n, [], [row.name]))
        n = Nums()
        top = f"the top {n(LETDOWN_WEEK_RANK)} {row.position}s"
        week = (f"was last in {top} in week {n(row.last_top_week)}" if row.last_top_week is not None
                else f"has no week in {top}")
        facts.append(fact(f"{prefix}.week", f"{row.name} {week}.", n, [], [row.name]))
    return facts
