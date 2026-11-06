"""
The draft steals and busts of the midseason report, the first chapter of Act II: each pick's cost rank at its position
against its points rank, with the injury tag of a bust. Decision ticket 02.
"""
from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from facts.tokens import Nums, fact
from league.history import player_points
from league.models import Fact, History
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


class DraftValue(BaseModel):
    """The facts of the draft steals and busts: the draft type, then the top steals and the top busts."""
    draft_type: DraftType
    steals: list[DraftRow]
    busts: list[DraftRow]


def _season_points(history: History, player_id: str, through: int) -> float:
    # Exact decimals, so a sum of many weeks never drifts. A week with no points for the player adds 0.
    total = sum((Decimal(str(player_points(history.weeks[w], player_id) or 0)) for w in range(1, through + 1)),
                Decimal(0))
    return r2(float(total))


def draft_value(
    picks: Sequence[DraftPick], draft_type: DraftType, history: History, through: int, names: Mapping[int, str],
    injured_games: Mapping[str, int] | None,
) -> DraftValue:
    """The top steals and busts of the draft over weeks 1 to `through` of `history`.

    The cost rank orders the picks of a position by price, high first, in an auction, and by pick number in a snake.
    A tie in price breaks by the order of sale, as a snake breaks by the pick number, so each pick has its own cost
    rank. The points rank counts the drafted players of the position with more points, plus one.
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
    return DraftValue(
        draft_type=draft_type,
        steals=steals,
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
    """The facts of the draft steals and busts: the pick and the points of each row, and its tag.

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
    return facts
