"""
The finder: the top win-win trades between the asker's roster and one partner roster, all in code.
It grades every one-for-one and two-for-one trade with the grade function and ranks the ones that are good for both.
"""
from itertools import combinations

from pydantic import BaseModel

from cornerstone.adjusters import OUT_STATUSES, is_handcuff, trade_handcuffs
from cornerstone.rubric import (
    LETTERS, Breakdown, Fairness, ProposedTrade, TradeSide, fairness, grade, unlisted_players,
)
from cornerstone.snapshot import Snapshot
from cornerstone.tunables import FINDER_TOP

# The finder sits one level above the grade function and the fairness rule. It never grades a side itself,
# so the finder and the analyzer never disagree on a trade.


class FinderTrade(BaseModel):
    """One win-win trade the finder found: the proposed trade, the breakdown of each side, and the fairness."""

    trade: ProposedTrade
    # In the order of trade.sides, so the asker's breakdown is first.
    breakdowns: tuple[Breakdown, Breakdown]
    fairness: Fairness


def _out_with_no_return(snapshot: Snapshot, player_id: str) -> bool:
    """True when the player is out now and the returns file has no week for him."""
    # The injury adjuster uses the same statuses, so a player the finder skips is one the grade counts as out.
    return snapshot.players[player_id].injury_status in OUT_STATUSES and player_id not in snapshot.returns


def _pool(snapshot: Snapshot, roster_id: int) -> list[str]:
    """The players of the roster the finder may trade: no unlisted player, no player out with no return, and
    no handcuff on this roster.
    """
    # An unlisted player starts both sides at C by rule, not by the chart, so a trade with him is never a real
    # win-win. The chart lists only RB, WR, TE, and QB, so this rule also keeps out every kicker and defense.
    unlisted = set(unlisted_players(snapshot, snapshot.rosters[roster_id]))
    return [pid for pid in snapshot.rosters[roster_id]
            if pid not in unlisted
            and not _out_with_no_return(snapshot, pid)
            and not is_handcuff(snapshot, pid, roster_id)]


def candidates(asker: int, partner: int, snapshot: Snapshot) -> list[ProposedTrade]:
    """Every one-for-one trade and every two-for-one trade in both directions, with the asker's side first.

    A trade that makes a player a handcuff on the roster that gets him is left out, so a handcuff on either
    roster never appears.
    """
    asker_pool, partner_pool = _pool(snapshot, asker), _pool(snapshot, partner)
    # The finder looks at small trades only. A three-player side is out of scope.
    asker_ones = [[pid] for pid in asker_pool]
    asker_twos = [list(pair) for pair in combinations(asker_pool, 2)]
    partner_ones = [[pid] for pid in partner_pool]
    partner_twos = [list(pair) for pair in combinations(partner_pool, 2)]
    trades = []
    for asker_options, partner_options in ((asker_ones, partner_ones), (asker_twos, partner_ones),
                                           (asker_ones, partner_twos)):
        for asker_gives in asker_options:
            for partner_gives in partner_options:
                trade = ProposedTrade(season=snapshot.season, asker=asker,
                                      sides=(TradeSide(roster_id=asker, gives=asker_gives),
                                             TradeSide(roster_id=partner, gives=partner_gives)))
                if not trade_handcuffs(trade, snapshot):
                    trades.append(trade)
    return trades


def _rank_key(item: FinderTrade) -> tuple:
    """The sort key: the net steps on both sides, the lower letter, the gap between the letters, the asker's letter,
    ids.
    """
    places = [LETTERS.index(breakdown.final_letter) for breakdown in item.breakdowns]
    # The net sum counts a step down against a step up, so a trade that costs a side on one adjuster ranks lower.
    steps = sum(adjuster.step for breakdown in item.breakdowns for adjuster in breakdown.adjusters)
    asker_place = next(LETTERS.index(b.final_letter) for b in item.breakdowns if b.roster_id == item.trade.asker)
    # A lower place on LETTERS is a better letter, so each letter key sorts ascending.
    # The sorted player ids break the last tie, so the same snapshot always gives the same list.
    ids = tuple(tuple(sorted(side.gives)) for side in item.trade.sides)
    return (-steps, max(places), abs(places[0] - places[1]), asker_place, ids)


def rank(items: list[FinderTrade]) -> list[FinderTrade]:
    """The items from the most both sides gain down to the least."""
    return sorted(items, key=_rank_key)


def _players(item: FinderTrade) -> set[str]:
    return {pid for side in item.trade.sides for pid in side.gives}


def _no_shared_player(ranked: list[FinderTrade]) -> list[FinderTrade]:
    """The first FINDER_TOP items of the ranked list that share no player with an item kept before them."""
    # Three trades on the same player are one choice, not three, and only one of them can go through.
    kept, used = [], set()
    for item in ranked:
        players = _players(item)
        if players & used:
            continue
        kept.append(item)
        used |= players
        if len(kept) == FINDER_TOP:
            break
    return kept


def find_win_wins(asker: int, partner: int, snapshot: Snapshot) -> list[FinderTrade]:
    """The top FINDER_TOP win-win trades between the two rosters, best first, with no player in two of them.
    An empty list when there is none.
    """
    found = []
    for trade in candidates(asker, partner, snapshot):
        breakdowns = grade(trade, snapshot)
        # No Claude call runs here, so the letters that stand are the rubric's final letters.
        result = fairness((breakdowns[0].final_letter, breakdowns[1].final_letter), breakdowns)
        if result.state == "win_win":
            found.append(FinderTrade(trade=trade, breakdowns=breakdowns, fairness=result))
    return _no_shared_player(rank(found))
