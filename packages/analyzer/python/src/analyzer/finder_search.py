"""
The Finder search: the partner filter (the Spares tree), the targets, the offers, and the shortlist, as a manager searches.
Jev judgments narrow each list, in waves under the rate limits. Code builds the offers and keeps only the hard rules.
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
from analyzer.trade_jev import NO_AT, TRADE_POSITIONS, YES_AT, trade_jev_questions, weak_slot_rows, weak_starting_slots
from league.history import season_rank
from league.jev_port import Jev, NoulQuestion
from league.lineup import lineup_now, lineup_slots
from league.ranks import OUT_STATUSES
from league.snapshot import Snapshot

log = logging.getLogger(__name__)

# A Finder offer holds only the TRADE_POSITIONS of trade_jev.py. A kicker and a defense are never in an offer.

# The target question, the one the prototype of the Finder tested: one Noul per player of the other side.
TARGET = {
    "text": "Would {team} want {player} from {owner}?",
    "yes": "{name} would start for {team} or fill a weak spot on its roster.",
    "no": "{name} would sit behind better players at his position on {team}."}
# The target question of a search around one player, for each player who would come back to the team that gives the
# anchor. It asks whether he fills the spot that the anchor leaves, so the offers do not aim at the weakest slot.
ANCHOR_TARGET = {
    "text": "Would {team} want {player} from {owner} to take the place of {anchor}?",
    "yes": "{name} would fill the lineup spot that {anchor_name} leaves on {team}.",
    "no": "{name} would not fill the spot of {anchor_name}: he plays another position, or he would sit behind better "
          "players on {team}."}
# The gain question of the shortlist: one Noul per side of each offer. Code puts the lineup points of each side before
# and after the trade in `offers.<n>.lineup_points` as facts, and states the change in words, so Jev compares no
# numbers (decision 09). A clear no, below NO_AT, drops the offer.
GAIN = {
    "text": "Does {team} start a better lineup after this trade, where it gives {gives} and gets {gets}?",
    "yes": "`offers.{n}.lineup_points` says {team} gains points a week, so its best lineup is better after the trade.",
    "no": "`offers.{n}.lineup_points` says {team} loses or keeps its points a week, so its best lineup is no better."}
TARGET_AT = 0.6      # a player is a target at this probability or more
TARGET_MAX = 4       # at most this many targets per side, by probability
SHORTLIST_KEEP = 10  # the offers that Jev rates highest, by the product of the fair and the need answers
# The answer that an offer holds after a failed shortlist request: the middle of the unsure band. A failed call is an
# error, never a no, so the offer goes on as an unsure answer does, and the pick sheet states no Jev answer for it.
UNSURE = (NO_AT + YES_AT) / 2
# The wider pass of a search that built no offer: one 1-for-1 idea per partner, so the pick sheet stays small.
WIDER_MAX = 12


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
    """One offer of the shortlist: the trade, the Jev answers of fair and of the need of each side, and their product."""

    offer_id: str
    trade: ProposedTrade
    fair: float
    # The probability that each side fills a starting need, by roster id.
    needs: dict[int, float]
    # The probability that each side starts a better lineup after the trade, by roster id.
    gains: dict[int, float] = {}
    score: float
    # True after a failed shortlist request: each answer is UNSURE, and the pick sheet states no Jev answer for it.
    failed: bool = False


class Shortlist(BaseModel):
    """What the Finder search gives the Advisor pick: the partner reads, the targets, every offer, and the shortlist.

    The offers list is every trade that code built, so the log and the evidence can list them.
    """

    asker: int
    partners: list[PartnerRead]
    # The targets of each partner that passed, by partner roster id: the players each side would want.
    targets: dict[int, dict[str, list[str]]]
    offers: list[ProposedTrade]
    shortlist: list[ShortlistOffer]
    # True when the targets built no offer and the offers come from the wider pass.
    wider: bool = False
    # The offers that a side's gain answer dropped with a clear no, with their answers, so the log and the evidence
    # can show why.
    dropped: list[ShortlistOffer] = []



def _out_with_no_return(snapshot: Snapshot, player_id: str) -> bool:
    """True when the player is out now and the returns file has no week for him."""
    # The injury Measure uses the same statuses, so a player the Finder skips is one the sheet reads as out.
    return snapshot.players[player_id].injury_status in OUT_STATUSES and player_id not in snapshot.returns

def _player_line(snapshot: Snapshot, pid: str, starters: set[str]) -> dict:
    player = snapshot.players[pid]
    season, _ = shown_ranks(snapshot, pid)
    return {"name": player.name, "position": player.position, "nfl_team": player.nfl_team,
            "season_rank": season, "starter": pid in starters, "status": player.injury_status}


def _team_state(snapshot: Snapshot, roster_id: int) -> dict:
    """One team as the questions read it: the name, the weak starting slots, the depth that code counts, the players."""
    roster = snapshot.rosters[roster_id]
    starters = {slot.player for slot in lineup_now(roster, snapshot) if slot.player is not None}
    players = [pid for pid in roster if snapshot.players[pid].position in TRADE_POSITIONS]
    # A player who is Out is no cover, so he is not in the depth (decision 09).
    depth = {pos: sum(1 for pid in players if snapshot.players[pid].position == pos and can_cover(snapshot, pid))
             for pos in TRADE_POSITIONS}
    return {"roster_id": roster_id, "name": snapshot.teams[roster_id].name,
            "weak_starting_slots": weak_starting_slots(snapshot, roster_id),
            "depth": depth,
            "players": [_player_line(snapshot, pid, starters) for pid in players]}


def _pair_state(snapshot: Snapshot, asker: int, partner: int) -> dict:
    return {"teams": {"asker": _team_state(snapshot, asker), "partner": _team_state(snapshot, partner)}}


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


def _target_questions(snapshot: Snapshot, asker: int, partner: int,
                      anchor: Anchor | None = None, limit: Limit | None = None) -> dict[str, NoulQuestion]:
    """One question per pool player of each side: "<roster id>.<player id>" asks if the other side wants him.

    With an anchor, each player who would go to the team that gives the anchor gets the anchor target question.
    With a limit, a player that the limit does not let move gets no question, so the targets of each side fit it.
    """
    questions = {}
    giver = None if anchor is None else asker if anchor.side == "gives" else partner
    for owner, team in ((partner, asker), (asker, partner)):
        fill = {"team": snapshot.teams[team].name, "owner": snapshot.teams[owner].name}
        wording = TARGET
        if anchor is not None and team == giver:
            wording = ANCHOR_TARGET
            fill |= {"anchor": _described(snapshot, anchor.player_id),
                     "anchor_name": snapshot.players[anchor.player_id].name}
        for pid in snapshot.rosters[owner]:
            if not in_pool(snapshot, pid, owner) or not _allowed(snapshot, pid, owner, asker, limit):
                continue
            words = {**fill, "player": _described(snapshot, pid), "name": snapshot.players[pid].name}
            questions[f"{owner}.{pid}"] = NoulQuestion(
                wording["text"].format(**words), wording["yes"].format(**words), wording["no"].format(**words))
    return questions


def _pick_targets(nouls: dict[str, float], owner: int) -> list[str]:
    """The players of `owner` at p TARGET_AT or more, the highest first, at most TARGET_MAX. The id breaks a tie."""
    rated = [(p, key.partition(".")[2]) for key, p in nouls.items()
             if key.partition(".")[0] == str(owner) and p >= TARGET_AT]
    return [pid for _, pid in sorted(rated, key=lambda item: (-item[0], item[1]))[:TARGET_MAX]]


def _anchored(picked: list[str], anchor: str) -> list[str]:
    """The targets of the side of the anchor: the anchor first, then the top picks of Jev, at most TARGET_MAX in all.

    The manager named the anchor, so he is a target whatever the target answer of Jev says about him.
    """
    return [anchor] + [pid for pid in picked if pid != anchor][:TARGET_MAX - 1]


def _holds(trade: ProposedTrade, anchor: Anchor) -> bool:
    """True when the trade holds the anchor on his side: the first side for "gives", the second side for "gets"."""
    return anchor.player_id in trade.sides[0 if anchor.side == "gives" else 1].player_ids


def build_offers(asker: int, partner: int, asker_targets: list[str], partner_targets: list[str],
                 snapshot: Snapshot) -> list[ProposedTrade]:
    """Every 1-for-1, 2-for-1, and 1-for-2 offer from the targets only, with the asker's side first.

    `asker_targets` are the asker's players that the partner wants, and `partner_targets` the partner's players
    that the asker wants. An offer that makes a player a handcuff on the roster that gets him drops (a hard rule).
    """
    asker_ones = [[pid] for pid in asker_targets]
    asker_twos = [list(pair) for pair in combinations(asker_targets, 2)]
    partner_ones = [[pid] for pid in partner_targets]
    partner_twos = [list(pair) for pair in combinations(partner_targets, 2)]
    offers = []
    for asker_options, partner_options in ((asker_ones, partner_ones), (asker_twos, partner_ones),
                                           (asker_ones, partner_twos)):
        for asker_gives in asker_options:
            for partner_gives in partner_options:
                sides = (TradeSide(roster_id=asker,
                                   gives=[GivenPlayer(player_id=pid, to=partner) for pid in asker_gives]),
                         TradeSide(roster_id=partner,
                                   gives=[GivenPlayer(player_id=pid, to=asker) for pid in partner_gives]))
                trade = ProposedTrade(season=snapshot.season, asker=asker, sides=sides)
                if not trade_handcuffs(trade, snapshot):
                    offers.append(trade)
    return offers


def _season_number(snapshot: Snapshot, pid: str) -> int | None:
    """The Season rank of the player as a number, such as 12 for RB12, or None with no complete stats."""
    ranked = season_rank(snapshot.stats, pid, snapshot.as_of.stats_through)
    return None if ranked is None else ranked[0]


def _weak_positions(snapshot: Snapshot, roster_id: int) -> set[str]:
    """The positions of the weak slots of a team: the position of the weak starter, or of an empty slot. An empty
    flex slot names no one position, so it adds none."""
    positions = {row["position"] or row["slot"].rstrip("0123456789") for row in weak_slot_rows(snapshot, roster_id)}
    return positions & set(TRADE_POSITIONS)


def _wider_candidate(snapshot: Snapshot, owner: int, asker: int, limit: Limit | None, positions: set[str],
                     near: int | None = None) -> str | None:
    """The one player of `owner` that the wider pass puts in an idea, or None.

    He is a pool player that the limit lets move, at one of `positions`. A player off the lineup now comes first,
    because a team gives up a spare more easily. Then, with `near`, the Season rank nearest it, for a like-for-like
    swap. Else the best Season rank. The id breaks a tie.
    """
    starters = {slot.player for slot in lineup_now(snapshot.rosters[owner], snapshot) if slot.player is not None}
    fits = [pid for pid in snapshot.rosters[owner]
            if snapshot.players[pid].position in positions and in_pool(snapshot, pid, owner)
            and _allowed(snapshot, pid, owner, asker, limit)]

    def order(pid: str) -> tuple:
        rank = _season_number(snapshot, pid)
        gap = (abs(rank - near) if near is not None else rank) if rank is not None else 10_000
        return (near is None and pid in starters, gap, pid)

    return min(fits, key=order, default=None)


def wider_offers(asker: int, partners: list[int], snapshot: Snapshot, anchor: Anchor | None = None,
                 limit: Limit | None = None) -> list[ProposedTrade]:
    """The ideas of the wider pass: at most one 1-for-1 offer per partner, picked by a plain rule with no Jev question.

    The pass runs only when the targets built no offer, so an ask always has ideas for the pick to weigh. It is a
    candidate set for the pick to judge, not a filter that decides a trade. The rule of each partner:
    - The asker gets the anchor of a "gets" search. Else a player at the position to get of the limit, or else at the
      position of the anchor of a "gives" search, like for like, nearest his Season rank. Else a player at a weak slot
      of the asker, or at any position when the asker has no weak slot.
    - The asker gives the anchor of a "gives" search. Else his player at a weak slot of the partner, so each side
      fills a need, or his spare at any position when none fits.
    The limit and the anchor stay hard rules, and an offer that makes a handcuff drops, as in the normal search.
    """
    offers = []
    for rid in partners:
        if anchor is not None and anchor.side == "gives":
            mine: str | None = anchor.player_id
        else:
            # With no fit at a weak slot of the partner, any position: an idea is an idea.
            mine = (_wider_candidate(snapshot, asker, asker, limit, _weak_positions(snapshot, rid))
                    or _wider_candidate(snapshot, asker, asker, limit, set(TRADE_POSITIONS)))
        if anchor is not None and anchor.side == "gets":
            theirs: str | None = anchor.player_id
        elif limit is not None and limit.aim_position is not None:
            theirs = _wider_candidate(snapshot, rid, asker, limit, {limit.aim_position})
        elif anchor is not None:
            position = snapshot.players[anchor.player_id].position
            theirs = _wider_candidate(snapshot, rid, asker, limit, {position},
                                      near=_season_number(snapshot, anchor.player_id))
        else:
            theirs = _wider_candidate(snapshot, rid, asker, limit,
                                      _weak_positions(snapshot, asker) or set(TRADE_POSITIONS))
        if mine is None or theirs is None:
            log.info("Finder wider pass with %s: no idea", snapshot.teams[rid].name)
            continue
        # The anchor must be in the pool of his roster, as in the normal search.
        if not (in_pool(snapshot, mine, asker) and in_pool(snapshot, theirs, rid)):
            continue
        offers += [trade for trade in build_offers(asker, rid, [mine], [theirs], snapshot)
                   if (anchor is None or _holds(trade, anchor)) and _within(trade, snapshot, limit)]
    return offers[:WIDER_MAX]


def offer_id(trade: ProposedTrade) -> str:
    """A stable id of an offer: each side's roster id and its given player ids, such as "4:7569-12:10236+8146"."""
    return "-".join(f"{side.roster_id}:{'+'.join(sorted(side.player_ids))}" for side in trade.sides)


def varied(offers: list[ShortlistOffer], keep: int) -> list[ShortlistOffer]:
    """At most `keep` offers, in an order with variety: the best offer for each player that the asker gives and for
    each partner, before more forms of the same trade (decision 01, AT-43).

    The best offers come first, by score, highest first. One offer can be the best for a player and for a partner. Every
    other offer comes after them, by score. It picks what the Advisor reads, and it cuts no offer by a score that the
    list would hold anyway. With more best offers than `keep`, the list holds only best offers.
    """
    # A tie of scores goes to the lower offer id, so the order is the same on each run.
    ranked = sorted(offers, key=lambda offer: (-offer.score, offer.offer_id))
    best: dict[tuple[str, str | int], str] = {}
    for offer in ranked:
        for pid in offer.trade.sides[0].player_ids:
            best.setdefault(("player", pid), offer.offer_id)
        for side in offer.trade.sides[1:]:
            best.setdefault(("partner", side.roster_id), offer.offer_id)
    best_ids = set(best.values())
    firsts = [offer for offer in ranked if offer.offer_id in best_ids]
    rest = [offer for offer in ranked if offer.offer_id not in best_ids]
    return (firsts + rest)[:keep]


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
    """The one shortlist request of a partner: the pair state with the lineup points of each offer, and the fair, the
    need, and the gain questions of each offer. The backtest asks the same request for a marked trade."""
    return WaveRequest(_shortlist_state(snapshot, asker, partner, offers), _shortlist_questions(offers, snapshot))


def shortlist_requests(snapshot: Snapshot, asker: int, partner: int,
                       offers: list[ProposedTrade]) -> list[WaveRequest]:
    """The shortlist requests of a partner, each under REQUEST_TOKENS by the estimate, with the offers in order.

    Each request holds the pair state and a run of the offers, and each offer keeps its number in the whole list, so
    the answers of every request merge by key. One request for a long list fails above the context of the model, and
    each of its offers then passes as unsure (decision 14).
    """
    base = estimated_tokens(WaveRequest(_pair_state(snapshot, asker, partner), {}))
    requests: list[WaveRequest] = []
    start, tokens = 0, base
    for n, trade in enumerate(offers):
        # The sum of the parts is a little over the estimate of the whole request, so each request stays under.
        cost = estimated_tokens(WaveRequest({"offers": _offer_lines(snapshot, [trade], n)},
                                            _shortlist_questions([trade], snapshot, n)))
        if n > start and tokens + cost >= REQUEST_TOKENS:
            requests.append(_shortlist_run(snapshot, asker, partner, offers[start:n], start))
            start, tokens = n, base
        tokens += cost
    if start < len(offers):
        requests.append(_shortlist_run(snapshot, asker, partner, offers[start:], start))
    return requests


def _shortlist_run(snapshot: Snapshot, asker: int, partner: int, offers: list[ProposedTrade],
                   start: int) -> WaveRequest:
    return WaveRequest(_shortlist_state(snapshot, asker, partner, offers, start),
                       _shortlist_questions(offers, snapshot, start))


def shortlist_answers(snapshot: Snapshot, asker: int, offers_by_partner: dict[int, list[ProposedTrade]],
                      waves: JevWaves) -> dict[int, list[dict[str, float] | None]]:
    """The Jev answers of each offer of each partner, in the order of its offers, keyed "fair", "need.<roster id>",
    and "gain.<roster id>". An offer whose request failed gets None, which is never a no.
    """
    requests = {f"{rid}.{part}": request for rid, partner_offers in offers_by_partner.items() if partner_offers
                for part, request in enumerate(shortlist_requests(snapshot, asker, rid, partner_offers))}
    judged = waves.ask(requests, "shortlist")
    by_offer: dict[int, dict[int, dict[str, float]]] = {}
    for key, response in judged.items():
        if response is None:
            continue
        offer_nouls = by_offer.setdefault(int(key.partition(".")[0]), {})
        for question, p in response.nouls.items():
            n, _, name = question.partition("|")
            offer_nouls.setdefault(int(n), {})[name] = p
    return {rid: [by_offer.get(rid, {}).get(n) for n in range(len(partner_offers))]
            for rid, partner_offers in offers_by_partner.items()}


def _shortlist_questions(offers: list[ProposedTrade], snapshot: Snapshot,
                         start: int = 0) -> dict[str, NoulQuestion]:
    """The fair question, the need question of each side, and the gain question of each side of each offer, keyed
    "<offer n>|fair", "<offer n>|need.<roster id>", and "<offer n>|gain.<roster id>".

    The fair and need questions are those of one trade, so the shortlist and the read of one trade ask the same words.
    """
    questions = {}
    for n, trade in enumerate(offers, start):
        for key, question in trade_jev_questions(trade, snapshot).items():
            if key == "fair" or key.startswith("need."):
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


def _log_target_questions(snapshot: Snapshot, partner: int, keys: list[str], nouls: dict[str, float] | None) -> None:
    """One log line of the target step with one partner: every player that Jev is asked about, with his answer.

    The line lists each player, picked or not, so the log shows that a player with no chart row still reaches the
    target step. After a failed request, the line names the players with no answer.
    """
    asked = ", ".join(snapshot.players[key.partition(".")[2]].name
                      + ("" if nouls is None else f"={nouls[key]:.2f}") for key in keys)
    log.info("Finder target questions with %s%s: %s", snapshot.teams[partner].name,
             ", failed request" if nouls is None else "", asked)


def _answer(nouls: dict[str, float] | None, key: str) -> float:
    """The Jev answer of a shortlist question, or UNSURE after a failed request, which is never a no."""
    return UNSURE if nouls is None else nouls[key]


def _no_read(roster_id: int) -> None:
    """The default read callback: it drops the roster id, because a search with no stream has no one to tell."""


def search(asker: int, partner: int | None, snapshot: Snapshot, jev: Jev, waves: JevWaves | None = None,
           stage: Stage = quiet, anchor: Anchor | None = None, limit: Limit | None = None,
           read: Callable[[int], None] = _no_read) -> Shortlist:
    """The Finder search of the asker: with no partner over every other team, else over the picked partner alone.

    1. The partner filter: the Spares tree of `spares_tree.py` on both sides of each pair. A partner goes on unless a
       side lists no player or each listed player of a side gets a clear no. A search with one picked partner or with
       an anchor skips it, and every partner goes on.
    2. The targets: Jev rates each pool player of each side. A target needs TARGET_AT, at most TARGET_MAX per side.
    3. The offers: code builds them from the targets only, under the hard rules.
    4. The shortlist: Jev asks the fair, the need, and the gain questions of each offer. A clear no on the gain of a
       side drops the offer, and an unsure answer stays. `varied` keeps SHORTLIST_KEEP offers:
       the best offer for each player that the asker gives and for each partner, before more forms of one trade.
    A failed Jev request logs, and it never reads as a no and never stops the press. A failed Spares tree request lets
    the partner go on to the targets. A failed shortlist request lets its offers go on, each as an unsure answer. A
    failed target request builds no offer for its partner.
    With an `anchor`, he is a target of his side, and each offer holds him on that side (a hard rule). An anchor that
    the asker gets keeps the search to his roster, because only that roster can give him.
    With a `limit`, no offer sends a player that the manager keeps, and each offer brings back the position that he
    aims at (a hard rule, because the manager set it).
    5. The wider pass: when the targets build no offer, `wider_offers` gives at most one plain idea per partner, so
       the pick has ideas to weigh. It asks no target question. It weighs each partner, one that the filter stopped
       and one whose filter request failed too.
    `stage` gets a live line as each of four steps starts and a done line as it ends: the teams read, the players who
    fit, the offers, and the shortlist. The lines name no inner tool, because the site shows them. The default drops
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
    if anchor is not None or partner is not None:
        # The filter asks about the weakest slots of each team. The anchor names the player the trade turns on, and the
        # anchor target question asks who fills his spot. A manager who picks one partner wants ideas with him, and a
        # stop there left one plain offer (decision 01). So every partner goes on to the targets.
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
            reads.append(PartnerRead(roster_id=rid, team=snapshot.teams[rid].name, answers=tree.answers,
                                     passed=tree.passed, failed=False))
            log.info("Spares tree of %s with %s: %s; %s", snapshot.teams[asker].name, snapshot.teams[rid].name,
                     "passed" if tree.passed else f"stopped on {', '.join(tree.stopped)}",
                     "; ".join(f"{side} gives " + (", ".join(
                         f"{snapshot.players[spare.player_id].name}={tree.answers[spare.key]:.2f}"
                         if spare.key in tree.answers else snapshot.players[spare.player_id].name
                         for spare in tree.spares[side]) or "no one") for side in ("partner", "asker")))
    passing = [read.roster_id for read in reads if read.passed]
    stage(f"Read {len(partners)} teams" if len(partners) > 1 else f"Read {snapshot.teams[partners[0]].name}")
    stage("Looking for players who fit", live=True)

    target_questions = {rid: _target_questions(snapshot, asker, rid, anchor, limit) for rid in passing}
    rated = waves.ask({str(rid): WaveRequest(_pair_state(snapshot, asker, rid), target_questions[rid])
                       for rid in passing}, "targets")
    targets: dict[int, dict[str, list[str]]] = {}
    offers_by_partner: dict[int, list[ProposedTrade]] = {}
    for rid in passing:
        response = rated[str(rid)]
        _log_target_questions(snapshot, rid, list(target_questions[rid]), response.nouls if response else None)
        if response is None:
            continue
        sides = {"asker": _pick_targets(response.nouls, asker), "partner": _pick_targets(response.nouls, rid)}
        if anchor is not None:
            # A player out of the pool, such as a kicker, breaks a hard rule, so no offer can hold him.
            owner, side = (asker, "asker") if anchor.side == "gives" else (rid, "partner")
            if in_pool(snapshot, anchor.player_id, owner):
                sides[side] = _anchored(sides[side], anchor.player_id)
        targets[rid] = sides
        log.info("Finder targets with %s: the asker gives %s; the partner gives %s", snapshot.teams[rid].name,
                 [snapshot.players[pid].name for pid in sides["asker"]],
                 [snapshot.players[pid].name for pid in sides["partner"]])
        built = build_offers(asker, rid, sides["asker"], sides["partner"], snapshot)
        offers_by_partner[rid] = [trade for trade in built
                                  if (anchor is None or _holds(trade, anchor)) and _within(trade, snapshot, limit)]
    fits = len({pid for sides in targets.values() for pids in sides.values() for pid in pids})
    stage({0: "Found no players who fit", 1: "Found one player who fits"}.get(fits, f"Found {fits} players who fit"))
    offers = [trade for rid in offers_by_partner for trade in offers_by_partner[rid]]
    wider = not offers
    # An idea is an idea: a search with no offer looks wider, so the manager sees what was weighed and why.
    stage("Looking wider for ideas" if wider else "Building offers", live=True)
    if wider:
        offers_by_partner = {}
        for trade in wider_offers(asker, [read.roster_id for read in reads], snapshot,
                                  anchor, limit):
            offers_by_partner.setdefault(trade.sides[1].roster_id, []).append(trade)
        offers = [trade for rid in offers_by_partner for trade in offers_by_partner[rid]]
        log.info("Finder wider pass of %s: %d", snapshot.teams[asker].name, len(offers))
    log.info("Finder offers of %s: %d", snapshot.teams[asker].name, len(offers))
    stage(f"Built {len(offers)} offers" if len(offers) != 1 else "Built one offer")
    stage("Making a shortlist", live=True)
    for trade in offers:
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
            fair = _answer(nouls, "fair")
            needs = {side.roster_id: _answer(nouls, f"need.{side.roster_id}") for side in trade.sides}
            gains = {side.roster_id: _answer(nouls, f"gain.{side.roster_id}") for side in trade.sides}
            score = fair
            for p in needs.values():
                score *= p
            offer = ShortlistOffer(offer_id=offer_id(trade), trade=trade, fair=fair, needs=needs, gains=gains,
                                   score=score, failed=nouls is None)
            # A clear no on the gain of any side drops the offer. An unsure answer stays (decision 09).
            if any(p < NO_AT for p in gains.values()):
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
    return Shortlist(asker=asker, partners=reads, targets=targets, offers=offers, shortlist=shortlist, wider=wider,
                     dropped=dropped)
