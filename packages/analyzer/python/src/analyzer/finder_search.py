"""
The Finder search: the partner reads (the Spares tree), the Value offers, the fair step, and the shortlist.
Code builds the offers with the Value screen and the hard rules. Jev judgments narrow them, in waves under the rate limits.
"""
import logging
from collections.abc import Callable
from decimal import Decimal
from itertools import combinations
from typing import Literal

from pydantic import BaseModel

from analyzer.jev_waves import REQUEST_TOKENS, JevWaves, WaveRequest, estimated_tokens
from analyzer.measures import is_handcuff, trade_handcuffs
from analyzer.spares_tree import can_cover, pair_request, pair_spares, read_pair
from analyzer.stage import Stage, quiet
from analyzer.trade import GivenPlayer, ProposedTrade, TradeSide
from analyzer.trade_facts import shown_ranks
from analyzer.trade_jev import NO_AT, TRADE_POSITIONS, YES_AT, trade_jev_questions, weak_starting_slots
from league.jev_port import Jev, NoulQuestion
from league.lineup import lineup_now, lineup_slots
from league.ranks import OUT_STATUSES
from league.snapshot import Snapshot

log = logging.getLogger(__name__)

# A Finder offer holds only the TRADE_POSITIONS of trade_jev.py. A kicker and a defense are never in an offer.

# The gain question of the shortlist: one Noul per side of each offer. Code puts the lineup points of each side before
# and after the trade in `offers.<n>.lineup_points` as facts, and states the change in words, so Jev compares no
# numbers (decision 09). A clear no, below NO_AT, drops the offer.
GAIN = {
    "text": "Does {team} start a better lineup after this trade, where it gives {gives} and gets {gets}?",
    "yes": "`offers.{n}.lineup_points` says {team} gains points a week, so its best lineup is better after the trade.",
    "no": "`offers.{n}.lineup_points` says {team} loses or keeps its points a week, so its best lineup is no better."}
# The fair question of step 1, wording B of decision 15: one Noul per offer, in each side order. Code puts the chart
# value of each player and the chart sum of each side in `offers.<n>.sides`, so Jev judges fairness from those facts.
# No question asks about the consolidation premium: the Value screen holds it in code.
FAIR = {
    "text": "Is the trade in `offers.{n}` close to fair by chart value: {gives}?",
    "yes": "Each team gives about as much chart value as it gets, by the sums in `offers.{n}.sides`.",
    "no": "One team gives a clearly larger chart sum in `offers.{n}.sides` than it gets back."}
# The two side orders of step 1. Jev reads an offer as more fair when the team named first gets the larger sum, so
# step 1 asks once with the asker first and once with the partner first, and code takes the mean (decision 15).
ORDERS = ("asker", "partner")
SHORTLIST_KEEP = 10  # the offers that the Advisor reads, spread by `varied` (decision 16)
# The answer that an offer holds after a failed shortlist request: the middle of the unsure band. A failed call is an
# error, never a no, so the offer goes on as an unsure answer does, and the pick sheet states no Jev answer for it.
UNSURE = (NO_AT + YES_AT) / 2

# The Value screen (decision 14, ADR 0038): the one cut of the Finder by math, and the one source of offers.
# Each shape direction is the count of players that the asker gives, then the count that he gets.
SHAPES = ((1, 1), (2, 1), (1, 2), (3, 1), (1, 3), (3, 2), (2, 3))
# The side that gets more players gets 100% to BAND of the trade value sum of the other side: the single player is the
# better one, so the team that gets more players gets more total value.
BAND = 1.25
# A 1-for-1 stays within 10% either way: the larger sum is at most ONE_FOR_ONE_BAND of the smaller sum.
ONE_FOR_ONE_BAND = 1.10
# Each player on a side of two or three players has at least this trade value, so no filler pads a "fair" sum.
FLOOR = 5.0


class Anchor(BaseModel):
    """The one player that a search of trade ideas is built around, and his side: the asker gives him, or gets him."""

    player_id: str
    side: Literal["gives", "gets"]


class Limit(BaseModel):
    """The limit that the manager sets on trade ideas: the positions and the players that his team never sends, and
    one position to get. It is the manager's own hard rule, so code drops each offer that breaks it."""

    keep_positions: list[str] = []
    keep_players: list[str] = []
    aim_position: str | None = None


class PartnerRead(BaseModel):
    """The partner filter of one partner: the Spares tree answer of each listed player by key, and the result."""

    roster_id: int
    team: str
    answers: dict[str, float]
    # True when no side of the Spares tree stops. True after a failed request too, which is an error and never a no.
    passed: bool
    # True after a failed request, so the log and the evidence show the error.
    failed: bool = False


class ShortlistOffer(BaseModel):
    """One offer of the shortlist: the trade, the fair mean of step 1, the step 2 answers of the need and the gain of
    each side, and the score, which is the fair mean alone (decision 16)."""

    offer_id: str
    trade: ProposedTrade
    # The fair mean of step 1, or UNSURE when the fair requests of both side orders failed.
    fair: float
    # The probability that each side fills a starting need, by roster id. Need is a reason, never a gate.
    needs: dict[int, float]
    # The probability that each side starts a better lineup after the trade, by roster id.
    gains: dict[int, float] = {}
    score: float
    # True after a failed step 2 request: each need and gain answer is UNSURE, and the pick sheet states no Jev answer.
    failed: bool = False
    # True when the fair requests of both side orders failed, so the pick sheet states no fair answer.
    fair_failed: bool = False
    # The players that the asker gets with a Spares tree "yes", each with the weak starting slot of the asker that he
    # fills, such as {"4046": "QB"}. They are reasons for the pick sheet, never a gate (decision 16).
    spares: dict[str, str] = {}


class Shortlist(BaseModel):
    """What the Finder search gives the Advisor pick: the partner reads, every Value offer, and the shortlist.

    The offers list is every trade that the Value screen built, so the log and the evidence can list them.
    """

    asker: int
    partners: list[PartnerRead]
    offers: list[ProposedTrade]
    shortlist: list[ShortlistOffer]
    # The fair answer of each Value offer by offer id: the mean of the two side orders. An offer with no answer in
    # either order, after failed requests, has none.
    fair_means: dict[str, float] = {}
    # The ids of the Value offers that step 1 dropped with a clear no on the fair mean, in the order of the offers.
    unfair: list[str] = []
    # The offers that a side's gain answer dropped with a clear no, with their answers, so the log and the evidence
    # can show why.
    dropped: list[ShortlistOffer] = []
    # The ids of the offers that step 2 asked about: the best offer of each partner and shape direction, by the fair
    # mean, in the order of the partners and of their offers.
    step_two: list[str] = []



def _out_with_no_return(snapshot: Snapshot, player_id: str) -> bool:
    """True when the player is out now and the returns file has no week for him."""
    # The injury Measure uses the same statuses, so a player the Finder skips is one the sheet reads as out.
    return snapshot.players[player_id].injury_status in OUT_STATUSES and player_id not in snapshot.returns

def _player_line(snapshot: Snapshot, pid: str, starters: set[str], charts: bool) -> dict:
    player = snapshot.players[pid]
    season, _ = shown_ranks(snapshot, pid)
    line = {"name": player.name, "position": player.position, "nfl_team": player.nfl_team,
            "season_rank": season, "starter": pid in starters, "status": player.injury_status}
    if charts:
        line["chart_value"] = chart_value(snapshot, pid)
    return line


def _team_state(snapshot: Snapshot, roster_id: int, charts: bool = False) -> dict:
    """One team as the questions read it: the name, the weak starting slots, the depth that code counts, the players.
    With `charts`, each player line holds his `chart_value` too, None for a player with no chart value."""
    roster = snapshot.rosters[roster_id]
    starters = {slot.player for slot in lineup_now(roster, snapshot) if slot.player is not None}
    players = [pid for pid in roster if snapshot.players[pid].position in TRADE_POSITIONS]
    # A player who is Out is no cover, so he is not in the depth (decision 09).
    depth = {pos: sum(1 for pid in players if snapshot.players[pid].position == pos and can_cover(snapshot, pid))
             for pos in TRADE_POSITIONS}
    return {"roster_id": roster_id, "name": snapshot.teams[roster_id].name,
            "weak_starting_slots": weak_starting_slots(snapshot, roster_id),
            "depth": depth,
            "players": [_player_line(snapshot, pid, starters, charts) for pid in players]}


def _pair_state(snapshot: Snapshot, asker: int, partner: int, charts: bool = False) -> dict:
    return {"teams": {"asker": _team_state(snapshot, asker, charts), "partner": _team_state(snapshot, partner, charts)}}


def in_pool(snapshot: Snapshot, pid: str, roster_id: int) -> bool:
    """The hard rules of one player on his own roster: a trade position, not out with no return week, no handcuff."""
    return (snapshot.players[pid].position in TRADE_POSITIONS
            and not _out_with_no_return(snapshot, pid)
            and not is_handcuff(snapshot, pid, roster_id))


def _described(snapshot: Snapshot, pid: str) -> str:
    player = snapshot.players[pid]
    return f"{player.name} ({player.position}, {player.nfl_team or 'no team'})"


def _allowed(snapshot: Snapshot, pid: str, owner: int, asker: int, limit: Limit | None) -> bool:
    """True when the limit lets the player move: a player of the asker that the limit keeps stays, and a player of the
    partner must play the position to get, when the limit has one."""
    if limit is None:
        return True
    position = snapshot.players[pid].position
    if owner == asker:
        return pid not in limit.keep_players and position not in limit.keep_positions
    return limit.aim_position is None or position == limit.aim_position


def _within(trade: ProposedTrade, snapshot: Snapshot, limit: Limit | None) -> bool:
    """True when the trade keeps the limit: the asker's side sends no kept player and no player of a kept position,
    and the partner's side sends a player of the position to get, when the limit has one."""
    if limit is None:
        return True
    mine, theirs = trade.sides[0].player_ids, trade.sides[1].player_ids
    if any(pid in limit.keep_players or snapshot.players[pid].position in limit.keep_positions for pid in mine):
        return False
    return limit.aim_position is None or any(snapshot.players[pid].position == limit.aim_position for pid in theirs)


def _holds(trade: ProposedTrade, anchor: Anchor) -> bool:
    """True when the trade holds the anchor on his side: the first side for "gives", the second side for "gets"."""
    return anchor.player_id in trade.sides[0 if anchor.side == "gives" else 1].player_ids


def chart_value(snapshot: Snapshot, pid: str) -> float | None:
    """The week's trade chart value of the player, or None when the chart has no value for him or the week has no
    chart."""
    return None if snapshot.chart is None else snapshot.chart.values.get(pid)


def shape(trade: ProposedTrade) -> str:
    """The shape direction of the trade: the players that the asker gives, then the players he gets, such as "2-for-1"."""
    return f"{len(trade.sides[0].player_ids)}-for-{len(trade.sides[1].player_ids)}"


def in_band(gives: list[float], gets: list[float]) -> bool:
    """True when the trade values of the two sides pass the Value screen (ADR 0038).

    `gives` holds the trade values of one side, and `gets` those of the other. Each player on a side of two or three
    has FLOOR or more. A 1-for-1 keeps the larger sum within ONE_FOR_ONE_BAND of the smaller. Else the side with more
    players sums to 100% to BAND of the other side. The sums are multiplied out, so no float division blurs an edge.
    """
    if any(len(side) > 1 and min(side) < FLOOR for side in (gives, gets)):
        return False
    first, second = sum(gives), sum(gets)
    if len(gives) == len(gets):
        return 100 * max(first, second) <= round(100 * ONE_FOR_ONE_BAND) * min(first, second)
    more, less = (first, second) if len(gives) > len(gets) else (second, first)
    return less <= more and 100 * more <= round(100 * BAND) * less


def _value_pool(snapshot: Snapshot, roster_id: int, asker: int, limit: Limit | None) -> list[str]:
    """The players of the roster who can enter a Value offer: in the pool, with a chart value, and, on the asker's
    roster, let move by the limit. A player with no chart value has no sum, so he never enters a Value offer."""
    return sorted(pid for pid in snapshot.rosters[roster_id]
                  if in_pool(snapshot, pid, roster_id) and chart_value(snapshot, pid) is not None
                  and (roster_id != asker or _allowed(snapshot, pid, roster_id, asker, limit)))


def value_offers(asker: int, partner: int, snapshot: Snapshot, anchor: Anchor | None = None,
                 limit: Limit | None = None) -> list[ProposedTrade]:
    """Every trade of the SHAPES between the asker and the partner that passes the Value screen, with the asker's side
    first, in the order of SHAPES.

    No cap follows the screen (decision 14). The hard rules hold too: an anchor sits on his side of each offer, each
    offer keeps the limit of the manager, and an offer that makes a player a handcuff on the roster that gets him drops.
    """
    values = {pid: chart_value(snapshot, pid) or 0.0 for rid in (asker, partner)
              for pid in _value_pool(snapshot, rid, asker, limit)}
    mine, theirs = _value_pool(snapshot, asker, asker, limit), _value_pool(snapshot, partner, asker, limit)
    offers = []
    for count_gives, count_gets in SHAPES:
        for gives in combinations(mine, count_gives):
            for gets in combinations(theirs, count_gets):
                if not in_band([values[pid] for pid in gives], [values[pid] for pid in gets]):
                    continue
                sides = (TradeSide(roster_id=asker, gives=[GivenPlayer(player_id=pid, to=partner) for pid in gives]),
                         TradeSide(roster_id=partner, gives=[GivenPlayer(player_id=pid, to=asker) for pid in gets]))
                trade = ProposedTrade(season=snapshot.season, asker=asker, sides=sides)
                if ((anchor is None or _holds(trade, anchor)) and _within(trade, snapshot, limit)
                        and not trade_handcuffs(trade, snapshot)):
                    offers.append(trade)
    return offers


def offer_id(trade: ProposedTrade) -> str:
    """A stable id of an offer: each side's roster id and its given player ids, such as "4:7569-12:10236+8146"."""
    return "-".join(f"{side.roster_id}:{'+'.join(sorted(side.player_ids))}" for side in trade.sides)


def _tier_keys(offer: ShortlistOffer) -> list[list[tuple[str, str | int]]]:
    """The keys of the three tiers of `varied` that the offer can be the best of: its shape direction, its partners,
    and the players that the asker gives."""
    return [[("shape", shape(offer.trade))],
            [("partner", side.roster_id) for side in offer.trade.sides[1:]],
            [("player", pid) for pid in offer.trade.sides[0].player_ids]]


def varied(offers: list[ShortlistOffer], keep: int) -> list[ShortlistOffer]:
    """At most `keep` offers, in an order with variety (decision 16, AT-43).

    First come the best offers of each shape direction, by score. Then the best offers of each partner that are not on
    the list yet, then those of each player that the asker gives. The rest follow by score, highest first. One offer
    can be the best of a shape, a partner, and a player, and it shows once, in its first tier. With more best offers
    than `keep`, the list holds only best offers.
    """
    # A tie of scores goes to the lower offer id, so the order is the same on each run.
    ranked = sorted(offers, key=lambda offer: (-offer.score, offer.offer_id))
    tiers: list[dict[tuple[str, str | int], str]] = [{}, {}, {}]
    for offer in ranked:
        for tier, keys in zip(tiers, _tier_keys(offer), strict=True):
            for key in keys:
                tier.setdefault(key, offer.offer_id)
    placed: list[ShortlistOffer] = []
    seen: set[str] = set()
    for tier in tiers:
        best_ids = set(tier.values())
        for offer in ranked:
            if offer.offer_id in best_ids and offer.offer_id not in seen:
                placed.append(offer)
                seen.add(offer.offer_id)
    rest = [offer for offer in ranked if offer.offer_id not in seen]
    return (placed + rest)[:keep]


def group_bests(offers: list[ProposedTrade], fair_by_id: dict[str, float]) -> list[ProposedTrade]:
    """The best offer of each partner and shape direction, by the fair mean, in the order of the offers (decision 16).

    An offer with no fair mean, after failed requests, counts as UNSURE, because a failed call is never a no. A tie
    goes to the lower offer id, so the pick is the same on each run.
    """
    best: dict[tuple[int, str], tuple[float, str]] = {}
    for trade in offers:
        oid = offer_id(trade)
        key = (trade.sides[1].roster_id, shape(trade))
        rank = (-fair_by_id.get(oid, UNSURE), oid)
        if key not in best or rank < best[key]:
            best[key] = rank
    chosen = {oid for _, oid in best.values()}
    return [trade for trade in offers if offer_id(trade) in chosen]


def lineup_points(snapshot: Snapshot, roster: list[str]) -> Decimal:
    """The points a week of the best lineup of `roster` for the rest of the season, as the lineup change Measure reads
    it: `lineup_slots`, where a player due back counts at his projection ahead.

    A trade is for the rest of the season, so a starter who is out this week only still counts. With `lineup_now`, a
    team whose QB misses one week reads any QB it gets as a large gain.
    """
    return sum((snapshot.lineup_value(slot.player) for slot in lineup_slots(roster, snapshot)
                if slot.player is not None), Decimal(0))


def _names(snapshot: Snapshot, pids: list[str]) -> str:
    return " and ".join(snapshot.players[pid].name for pid in pids) or "no one"


def _listed(snapshot: Snapshot, pids: list[str]) -> str:
    """The names as a list, such as "A", "A and B", or "A, B, and C", the way the questions of one trade name them."""
    names = [snapshot.players[pid].name for pid in pids]
    return " and ".join(names) if len(names) <= 2 else ", ".join(names[:-1]) + f", and {names[-1]}"


def lineup_line(snapshot: Snapshot, trade: ProposedTrade, roster_id: int) -> str:
    """The lineup points of one side before and after the trade as one fact, with the change in words, such as
    "Team A starts 110.0 points a week before this trade and 103.8 after, so its lineup loses 6.2 points a week."

    Code counts the points, so Jev reads the change and compares no numbers itself.
    """
    side = next(side for side in trade.sides if side.roster_id == roster_id)
    roster = snapshot.rosters[roster_id]
    after_roster = [pid for pid in roster if pid not in side.player_ids] + trade.gets(roster_id)
    before = round(float(lineup_points(snapshot, roster)), 1)
    after = round(float(lineup_points(snapshot, after_roster)), 1)
    change = round(after - before, 1)
    word = "gains" if change > 0 else "loses" if change < 0 else "keeps"
    return (f"{snapshot.teams[roster_id].name} starts {before:.1f} points a week before this trade and {after:.1f} "
            f"after, so its lineup {word} {abs(change):.1f} points a week.")


def _offer_lines(snapshot: Snapshot, offers: list[ProposedTrade], start: int) -> dict:
    """The trade and the lineup points of each side of each offer, by offer number from `start`."""
    return {str(n): {"trade": "; ".join(f"{snapshot.teams[side.roster_id].name} gives "
                                        f"{_names(snapshot, side.player_ids)}" for side in trade.sides),
                     "lineup_points": [lineup_line(snapshot, trade, side.roster_id) for side in trade.sides]}
            for n, trade in enumerate(offers, start)}


def _shortlist_state(snapshot: Snapshot, asker: int, partner: int, offers: list[ProposedTrade],
                     start: int = 0) -> dict:
    """The pair state with the lineup points of each side of each offer, under `offers.<n>`, from `start`."""
    state = _pair_state(snapshot, asker, partner)
    state["offers"] = _offer_lines(snapshot, offers, start)
    return state


def shortlist_request(snapshot: Snapshot, asker: int, partner: int, offers: list[ProposedTrade]) -> WaveRequest:
    """The one step 2 request of a partner: the pair state with the lineup points of each offer, and the need and the
    gain questions of each side of each offer."""
    return WaveRequest(_shortlist_state(snapshot, asker, partner, offers), _shortlist_questions(offers, snapshot))


def step_two_answers(snapshot: Snapshot, trade: ProposedTrade, jev: Jev) -> dict[str, float]:
    """The step 2 answers of one offer, keyed "need.<roster id>" and "gain.<roster id>", from one Jev request.

    A failed request raises its JevError, because a failed call is an error and never a drop. The backtest asks this
    for a marked trade, so it reads the same words as the Finder.
    """
    request = shortlist_request(snapshot, trade.sides[0].roster_id, trade.sides[1].roster_id, [trade])
    nouls = jev.ask(request.state, request.questions).nouls
    return {key.partition("|")[2]: p for key, p in nouls.items()}


def gain_dropped(gains: dict[int, float]) -> bool:
    """True when a clear no on the gain of any side, below NO_AT, drops the offer. An unsure answer stays (decision
    09). Need answers never reach here, because no need answer drops an offer (decision 15)."""
    return any(p < NO_AT for p in gains.values())


def shortlist_requests(snapshot: Snapshot, asker: int, partner: int,
                       offers: list[ProposedTrade]) -> list[WaveRequest]:
    """The shortlist requests of a partner, each under REQUEST_TOKENS by the estimate, with the offers in order.

    Each request holds the pair state and a run of the offers, and each offer keeps its number in the whole list, so
    the answers of every request merge by key. One request for a long list fails above the context of the model, and
    each of its offers then passes as unsure (decision 14).
    """
    return _split(_pair_state(snapshot, asker, partner), offers,
                  lambda run, start: _offer_lines(snapshot, run, start),
                  lambda run, start: _shortlist_questions(run, snapshot, start))


def _split(base: dict, offers: list[ProposedTrade], lines: Callable[[list[ProposedTrade], int], dict],
           questions: Callable[[list[ProposedTrade], int], dict[str, NoulQuestion]]) -> list[WaveRequest]:
    """The requests of one list of offers, each under REQUEST_TOKENS by the estimate, with the offers in order.

    Each request holds the `base` state with the lines of a run of the offers under `offers`, and the questions of
    that run. `lines` and `questions` take a run and the number of its first offer, so each offer keeps its number in
    the whole list.
    """
    cost_of_base = estimated_tokens(WaveRequest(base, {}))
    requests: list[WaveRequest] = []
    start, tokens = 0, cost_of_base
    for n, trade in enumerate(offers):
        # The sum of the parts is a little over the estimate of the whole request, so each request stays under.
        cost = estimated_tokens(WaveRequest({"offers": lines([trade], n)}, questions([trade], n)))
        if n > start and tokens + cost >= REQUEST_TOKENS:
            requests.append(WaveRequest({**base, "offers": lines(offers[start:n], start)},
                                        questions(offers[start:n], start)))
            start, tokens = n, cost_of_base
        tokens += cost
    if start < len(offers):
        requests.append(WaveRequest({**base, "offers": lines(offers[start:], start)}, questions(offers[start:], start)))
    return requests


def _offer_answers(groups: dict[str, list[WaveRequest]], counts: dict[str, int], waves: JevWaves,
                   label: str) -> dict[str, list[dict[str, float] | None]]:
    """The Jev answers of each offer of each group, in the order of its offers, keyed by the question name after the
    "|" of each key. The requests of every group go in one set of waves. An offer whose request failed gets None,
    which is never a no."""
    requests = {f"{group}.{part}": request for group, group_requests in groups.items()
                for part, request in enumerate(group_requests)}
    judged = waves.ask(requests, label)
    by_offer: dict[str, dict[int, dict[str, float]]] = {}
    for key, response in judged.items():
        if response is None:
            continue
        offer_nouls = by_offer.setdefault(key.rpartition(".")[0], {})
        for question, p in response.nouls.items():
            n, _, name = question.partition("|")
            offer_nouls.setdefault(int(n), {})[name] = p
    return {group: [by_offer.get(group, {}).get(n) for n in range(count)] for group, count in counts.items()}


def shortlist_answers(snapshot: Snapshot, asker: int, offers_by_partner: dict[int, list[ProposedTrade]],
                      waves: JevWaves) -> dict[int, list[dict[str, float] | None]]:
    """The step 2 answers of each offer of each partner, in the order of its offers, keyed "need.<roster id>" and
    "gain.<roster id>". An offer whose request failed gets None, which is never a no.
    """
    groups = {str(rid): shortlist_requests(snapshot, asker, rid, partner_offers)
              for rid, partner_offers in offers_by_partner.items() if partner_offers}
    answers = _offer_answers(groups, {str(rid): len(o) for rid, o in offers_by_partner.items()}, waves, "shortlist")
    return {rid: answers[str(rid)] for rid in offers_by_partner}


def _side_line(snapshot: Snapshot, side: TradeSide) -> dict:
    """One side of an offer for the fair question: the team, each player it gives with his chart value, and the sum."""
    values = {pid: chart_value(snapshot, pid) or 0.0 for pid in side.player_ids}
    return {"team": snapshot.teams[side.roster_id].name,
            "gives": [{"name": snapshot.players[pid].name, "chart_value": values[pid]} for pid in side.player_ids],
            "chart_sum": sum(values.values())}


def _ordered(trade: ProposedTrade, order: str) -> list[TradeSide]:
    """The sides of the trade in the side order: the asker first, or the partner first."""
    return list(trade.sides) if order == "asker" else list(reversed(trade.sides))


def _fair_lines(snapshot: Snapshot, offers: list[ProposedTrade], start: int, order: str) -> dict:
    """The sides of each offer in the side order, by offer number from `start`."""
    return {str(n): {"sides": [_side_line(snapshot, side) for side in _ordered(trade, order)]}
            for n, trade in enumerate(offers, start)}


def _fair_questions(snapshot: Snapshot, offers: list[ProposedTrade], start: int,
                    order: str) -> dict[str, NoulQuestion]:
    """The fair question of each offer, keyed "<offer n>|fair". The trade words name the teams in the side order."""
    questions = {}
    for n, trade in enumerate(offers, start):
        gives = " and ".join(f"{snapshot.teams[side.roster_id].name} gives {_listed(snapshot, side.player_ids)}"
                             for side in _ordered(trade, order))
        questions[f"{n}|fair"] = NoulQuestion(FAIR["text"].format(n=n, gives=gives), FAIR["yes"].format(n=n),
                                              FAIR["no"].format(n=n))
    return questions


def fair_requests(snapshot: Snapshot, asker: int, partner: int, offers: list[ProposedTrade],
                  order: str) -> list[WaveRequest]:
    """The fair requests of step 1 for one partner and one side order, each under REQUEST_TOKENS by the estimate.

    The state is the pair state with the `chart_value` of each player, and the sides of each offer under
    `offers.<n>.sides`, each with its players and its `chart_sum`.
    """
    return _split(_pair_state(snapshot, asker, partner, charts=True), offers,
                  lambda run, start: _fair_lines(snapshot, run, start, order),
                  lambda run, start: _fair_questions(snapshot, run, start, order))


def fair_means(snapshot: Snapshot, asker: int, offers_by_partner: dict[int, list[ProposedTrade]],
               waves: JevWaves) -> dict[int, list[float | None]]:
    """The fair answer of each offer of each partner, the mean of its answers in the two side orders, in the order of
    its offers.

    An order whose request failed adds no answer, because a failed call is an error and never a no. An offer with no
    answer in either order gets None.
    """
    groups = {f"{rid}.{order}": fair_requests(snapshot, asker, rid, partner_offers, order)
              for rid, partner_offers in offers_by_partner.items() if partner_offers for order in ORDERS}
    counts = {f"{rid}.{order}": len(partner_offers) for rid, partner_offers in offers_by_partner.items()
              for order in ORDERS}
    answers = _offer_answers(groups, counts, waves, "fair")
    means: dict[int, list[float | None]] = {}
    for rid, partner_offers in offers_by_partner.items():
        means[rid] = []
        for n in range(len(partner_offers)):
            ps = [nouls["fair"] for order in ORDERS if (nouls := answers[f"{rid}.{order}"][n]) is not None]
            means[rid].append(sum(ps) / len(ps) if ps else None)
    return means


def _shortlist_questions(offers: list[ProposedTrade], snapshot: Snapshot,
                         start: int = 0) -> dict[str, NoulQuestion]:
    """The step 2 questions of each offer: the need and the gain question of each side, keyed
    "<offer n>|need.<roster id>" and "<offer n>|gain.<roster id>". Step 1 already asked the fair question.

    The need questions are those of one trade, so step 2 and the read of one trade ask the same words.
    """
    questions = {}
    for n, trade in enumerate(offers, start):
        for key, question in trade_jev_questions(trade, snapshot).items():
            if key.startswith("need."):
                questions[f"{n}|{key}"] = question
        for side in trade.sides:
            rid = side.roster_id
            words = {"team": snapshot.teams[rid].name, "gives": _names(snapshot, side.player_ids),
                     "gets": _names(snapshot, trade.gets(rid)), "n": n}
            questions[f"{n}|gain.{rid}"] = NoulQuestion(GAIN["text"].format(**words), GAIN["yes"].format(**words),
                                                        GAIN["no"].format(**words))
    return questions


def _log_offer(snapshot: Snapshot, trade: ProposedTrade) -> None:
    sides = "; ".join(f"{snapshot.teams[side.roster_id].name} gives "
                      f"{' and '.join(_described(snapshot, pid) for pid in side.player_ids)}" for side in trade.sides)
    log.info("Finder offer %s: %s", offer_id(trade), sides)


def _trades(count: int) -> str:
    """The count of trades in words for a step line, such as "4,667 trades", "one trade", or "no trades"."""
    return {0: "no trades", 1: "one trade"}.get(count, f"{count:,} trades")


def _log_shapes(snapshot: Snapshot, asker: int, offers: list[ProposedTrade]) -> None:
    """One log line with the count of Value offers of the asker, in all and by shape direction."""
    counts = {f"{gives}-for-{gets}": 0 for gives, gets in SHAPES}
    for trade in offers:
        counts[shape(trade)] += 1
    log.info("Finder Value offers of %s: %d; %s", snapshot.teams[asker].name, len(offers),
             ", ".join(f"{name}={count}" for name, count in counts.items()))


def _answer(nouls: dict[str, float] | None, key: str) -> float:
    """The Jev answer of a shortlist question, or UNSURE after a failed request, which is never a no."""
    return UNSURE if nouls is None else nouls[key]


def _no_read(roster_id: int) -> None:
    """The default read callback: it drops the roster id, because a search with no stream has no one to tell."""


def search(asker: int, partner: int | None, snapshot: Snapshot, jev: Jev, waves: JevWaves | None = None,
           stage: Stage = quiet, anchor: Anchor | None = None, limit: Limit | None = None,
           read: Callable[[int], None] = _no_read) -> Shortlist:
    """The Finder search of the asker: with no partner over every other team, else over the picked partner alone.

    1. The partner reads: the Spares tree of `spares_tree.py` on both sides of each pair. It stops no partner and
       builds no offer, because the Value screen is the one source of offers (decision 15). A "yes" for a player that
       the asker gets becomes a pick sheet fact of each offer that brings him (decision 16). A search with one picked
       partner or with an anchor skips it.
    2. The Value offers: `value_offers` builds every trade of the SHAPES with each partner that passes the Value screen
       and the hard rules (decision 14, ADR 0038). No cap follows the screen.
    3. Step 1, the fair check: Jev asks the fair Noul of each Value offer once in each side order, and code takes the
       mean. A clear no on the mean, below NO_AT, drops the offer (decision 15).
    4. Step 2 and the shortlist: the offers that passed step 1 group by partner and shape direction, and the best of
       each group by the fair mean goes on (decision 16). Jev asks the need and the gain of each side. A clear no on
       the gain of a side drops the offer, and an unsure answer stays. No need answer drops an offer. The score is the
       fair mean alone. `varied` keeps SHORTLIST_KEEP offers: the best of each shape direction, then of each partner,
       then of each player that the asker gives, then the rest by score.
    A failed Jev request logs, and it never reads as a no and never stops the press. A failed Spares tree request marks
    the read failed. A failed fair request adds no answer, so its offers go on. A failed shortlist request lets its
    offers go on, each as an unsure answer.
    With an `anchor`, each offer holds him on his side (a hard rule). An anchor that the asker gets keeps the search to
    his roster, because only that roster can give him.
    With a `limit`, no offer sends a player that the manager keeps, and each offer brings back the position that he
    aims at (a hard rule, because the manager set it).
    `stage` gets a live line as each of four steps starts and a done line as it ends: the teams read, the Value offers,
    the fair check, and the shortlist. The lines of the Value offers and the fair check carry their counts. The lines name no inner tool, because the site shows them. The default drops
    them. `read` gets the roster id of each partner as the first step reads it, so the site can light each team in
    turn. The default drops it.
    """
    waves = waves or JevWaves(jev)
    if anchor is not None and anchor.side == "gets":
        # A player who left each roster since the pick keeps the partner, and no offer can hold him.
        partner = next((rid for rid, roster in snapshot.rosters.items() if anchor.player_id in roster), partner)
    partners = [partner] if partner is not None else sorted(rid for rid in snapshot.rosters if rid != asker)
    stage("Reading every team" if len(partners) > 1 else "Reading their roster", live=True)

    reads: list[PartnerRead] = []
    # The players of each partner with a Spares tree "yes", by player id, each with the weak slot of the asker that he
    # fills. They become pick sheet facts and never stop an offer (decision 16).
    spare_yes: dict[int, dict[str, str]] = {}
    if anchor is not None or partner is not None:
        # The Spares tree asks about the weakest slots of each team. The anchor names the player the trade turns on, and
        # a manager who picks one partner wants ideas with him (decision 01). So neither asks it.
        reads = [PartnerRead(roster_id=rid, team=snapshot.teams[rid].name, answers={}, passed=True, failed=False)
                 for rid in partners]
        for rid in partners:
            read(rid)
        log.info("Spares tree of %s: skipped for %s", snapshot.teams[asker].name,
                 "the anchor" if anchor is not None else "one picked partner")
    else:
        spares = {rid: pair_spares(snapshot, asker, rid) for rid in partners}
        requests = {str(rid): pair_request(snapshot, asker, rid, spares[rid]) for rid in partners}
        # A partner with no request needs no Jev answer, so the stream reports it as read at once.
        for key, request in requests.items():
            if request is None:
                read(int(key))
        filtered = waves.ask({key: request for key, request in requests.items() if request is not None},
                             "spares tree", answered=lambda key: read(int(key)))
        for rid in partners:
            response = filtered.get(str(rid))
            if requests[str(rid)] is not None and response is None:
                # A failed call is an error, never a stop, so the read says failed and the partner goes on.
                reads.append(PartnerRead(roster_id=rid, team=snapshot.teams[rid].name, answers={}, passed=True,
                                         failed=True))
                log.info("Spares tree of %s with %s: failed request", snapshot.teams[asker].name,
                         snapshot.teams[rid].name)
                continue
            tree = read_pair(asker, rid, spares[rid], {} if response is None else response.nouls)
            spare_yes[rid] = {spare.player_id: spare.slot for spare in tree.spares["partner"]
                              if tree.answers.get(spare.key, 0.0) > YES_AT}
            reads.append(PartnerRead(roster_id=rid, team=snapshot.teams[rid].name, answers=tree.answers,
                                     passed=tree.passed, failed=False))
            log.info("Spares tree of %s with %s: %s; %s", snapshot.teams[asker].name, snapshot.teams[rid].name,
                     "passed" if tree.passed else f"stopped on {', '.join(tree.stopped)}",
                     "; ".join(f"{side} gives " + (", ".join(
                         f"{snapshot.players[spare.player_id].name}={tree.answers[spare.key]:.2f}"
                         if spare.key in tree.answers else snapshot.players[spare.player_id].name
                         for spare in tree.spares[side]) or "no one") for side in ("partner", "asker")))
    stage(f"Read {len(partners)} teams" if len(partners) > 1 else f"Read {snapshot.teams[partners[0]].name}")
    stage("Matching trade value", live=True)

    # The Value screen builds the offers of every partner. The Spares tree stops no partner (decision 15).
    offers_by_partner = {rid: value_offers(asker, rid, snapshot, anchor, limit) for rid in partners}
    offers = [trade for rid in offers_by_partner for trade in offers_by_partner[rid]]
    _log_shapes(snapshot, asker, offers)
    stage(f"Matched {_trades(len(offers))} by trade value")

    # Step 1: the fair Noul of each Value offer in both side orders. A clear no on the mean drops the offer.
    stage(f"Checking {_trades(len(offers))} for fairness", live=True)
    means = fair_means(snapshot, asker, offers_by_partner, waves)
    fair_by_id: dict[str, float] = {}
    unfair: list[str] = []
    for rid, partner_offers in offers_by_partner.items():
        kept = []
        for trade, mean in zip(partner_offers, means[rid], strict=True):
            if mean is not None:
                fair_by_id[offer_id(trade)] = mean
            # A failed call is an error, never a no, so an offer with no answer goes on.
            if mean is not None and mean < NO_AT:
                unfair.append(offer_id(trade))
                continue
            kept.append(trade)
        offers_by_partner[rid] = kept
    log.info("Finder fair step of %s: checked %d, dropped %d, no answer %d", snapshot.teams[asker].name, len(offers),
             len(unfair), len(offers) - len(fair_by_id))
    stage(f"Checked {_trades(len(offers))} for fairness")
    stage("Making a shortlist", live=True)

    # Step 2 reads the best offer of each partner and shape direction, by the fair mean, so no shape and no partner
    # disappears before the gain drop, and the request count stays small (decision 16).
    offers_by_partner = {rid: group_bests(partner_offers, fair_by_id)
                         for rid, partner_offers in offers_by_partner.items()}
    step_two = [offer_id(trade) for partner_offers in offers_by_partner.values() for trade in partner_offers]
    log.info("Finder step 2 of %s: %d offers, the best of each partner and shape direction",
             snapshot.teams[asker].name, len(step_two))
    for trade in (trade for partner_offers in offers_by_partner.values() for trade in partner_offers):
        _log_offer(snapshot, trade)

    judged = shortlist_answers(snapshot, asker, offers_by_partner, waves)
    rated_offers = []
    dropped = []
    for rid, partner_offers in offers_by_partner.items():
        failed = sum(nouls is None for nouls in judged[rid])
        if failed:
            # A failed call is an error, never a no, so each offer goes on as an unsure answer does.
            log.info("Finder shortlist with %s: failed request, %d offers go on as unsure", snapshot.teams[rid].name,
                     failed)
        for trade, nouls in zip(partner_offers, judged[rid], strict=True):
            oid = offer_id(trade)
            fair = fair_by_id.get(oid, UNSURE)
            needs = {side.roster_id: _answer(nouls, f"need.{side.roster_id}") for side in trade.sides}
            gains = {side.roster_id: _answer(nouls, f"gain.{side.roster_id}") for side in trade.sides}
            # The score is the fair mean alone. Need is a reason for the pick, so a product with need would bring back
            # the need-first order (decision 16).
            offer = ShortlistOffer(offer_id=oid, trade=trade, fair=fair, needs=needs, gains=gains, score=fair,
                                   failed=nouls is None, fair_failed=oid not in fair_by_id,
                                   spares={pid: spare_yes[rid][pid] for pid in trade.sides[1].player_ids
                                           if pid in spare_yes.get(rid, {})})
            # A clear no on the gain of any side drops the offer. An unsure answer stays (decision 09).
            if gain_dropped(gains):
                dropped.append(offer)
                log.info("Finder gain drop %s: gains=%s", offer.offer_id, {r: round(p, 2) for r, p in gains.items()})
                continue
            rated_offers.append(offer)
    shortlist = varied(rated_offers, SHORTLIST_KEEP)
    stage(f"Made a shortlist of {len(shortlist)}" if len(shortlist) != 1 else "Made a shortlist of one")
    for offer in shortlist:
        log.info("Finder shortlist %s: score=%.3f fair=%.2f needs=%s gains=%s", offer.offer_id, offer.score,
                 offer.fair, {rid: round(p, 2) for rid, p in offer.needs.items()},
                 {rid: round(p, 2) for rid, p in offer.gains.items()})
    return Shortlist(asker=asker, partners=reads, offers=offers, shortlist=shortlist, dropped=dropped,
                     fair_means=fair_by_id, unfair=unfair, step_two=step_two)
