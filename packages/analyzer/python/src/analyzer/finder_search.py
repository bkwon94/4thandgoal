"""
The Finder search: the partner filter, the targets, the offers, and the shortlist, as a manager searches.
Jev judgments narrow each list, in waves under the rate limits. Code builds the offers and keeps only the hard rules.
"""
import logging
from itertools import combinations
from typing import Literal

from pydantic import BaseModel

from analyzer.jev_waves import JevWaves, WaveRequest
from analyzer.measures import is_handcuff, trade_handcuffs
from analyzer.stage import Stage, quiet
from analyzer.trade import GivenPlayer, ProposedTrade, TradeSide
from analyzer.trade_facts import shown_ranks
from analyzer.trade_jev import TRADE_POSITIONS, YES_AT, trade_jev_questions, weak_starting_slots
from league.jev_port import Jev, NoulQuestion
from league.lineup import above_the_line, lineup_now
from league.ranks import OUT_STATUSES
from league.snapshot import Snapshot

log = logging.getLogger(__name__)

# A Finder offer holds only the TRADE_POSITIONS of trade_jev.py. A kicker and a defense are never in an offer.

# The four questions of the partner filter, from the glossary entry "Partner filter". Each asks one judgment, and
# the state holds the depth that code counts, because Jev does not count reliably.
PARTNER_FILTER = {
    # The "has" wording that names the weak starters won a live probe on 4 pairs: about 0.85 against about 0.6 for
    # "a player at a weak starting slot", which Jev read as unsure.
    "partner_has": {
        "text": "Would a player of {partner} start over one of the weak starters of {asker} in "
                "`teams.asker.weak_starting_slots`?",
        "yes": "A player in `teams.partner.players` plays the position of a weak starter of {asker} and would score more "
               "than him.",
        "no": "Each player of {partner} at the positions of those weak starters would score less than them."},
    "partner_spares": {
        "text": "Can {partner} give up a player who would start at a weak slot of {asker}, with no hole in its own "
                "lineup?",
        "yes": "{partner} has a player who fits a weak slot of {asker}, and `teams.partner.depth` shows another player "
               "above the line at his position, so the lineup of {partner} stays full.",
        "no": "Each player of {partner} who fits a weak slot of {asker} is a starter with no one above the line behind "
              "him."},
    "asker_has": {
        "text": "Would a player of {asker} start over one of the weak starters of {partner} in "
                "`teams.partner.weak_starting_slots`?",
        "yes": "A player in `teams.asker.players` plays the position of a weak starter of {partner} and would score more "
               "than him.",
        "no": "Each player of {asker} at the positions of those weak starters would score less than them."},
    "asker_spares": {
        "text": "Can {asker} give up a player who would start at a weak slot of {partner}, with no hole in its own "
                "lineup?",
        "yes": "{asker} has a player who fits a weak slot of {partner}, and `teams.asker.depth` shows another player "
               "above the line at his position, so the lineup of {asker} stays full.",
        "no": "Each player of {asker} who fits a weak slot of {partner} is a starter with no one above the line behind "
              "him."},
}
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
TARGET_AT = 0.6      # a player is a target at this probability or more
TARGET_MAX = 4       # at most this many targets per side, by probability
SHORTLIST_KEEP = 10  # the offers that Jev rates highest, by the product of the fair and the need answers


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
    """The partner filter of one partner: the probability of yes of each of the four questions, and the result."""

    roster_id: int
    team: str
    answers: dict[str, float]
    # True when each of the four answers reads yes. False after a failed request, which is never a no.
    passed: bool
    failed: bool = False


class ShortlistOffer(BaseModel):
    """One offer of the shortlist: the trade, the Jev answers of fair and of the need of each side, and their product."""

    offer_id: str
    trade: ProposedTrade
    fair: float
    # The probability that each side fills a starting need, by roster id.
    needs: dict[int, float]
    score: float


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
    depth = {pos: sum(1 for pid in players if snapshot.players[pid].position == pos and above_the_line(snapshot, pid))
             for pos in TRADE_POSITIONS}
    return {"roster_id": roster_id, "name": snapshot.teams[roster_id].name,
            "weak_starting_slots": weak_starting_slots(snapshot, roster_id),
            "depth": depth,
            "players": [_player_line(snapshot, pid, starters) for pid in players]}


def _pair_state(snapshot: Snapshot, asker: int, partner: int) -> dict:
    return {"teams": {"asker": _team_state(snapshot, asker), "partner": _team_state(snapshot, partner)}}


def _filter_questions(snapshot: Snapshot, asker: int, partner: int) -> dict[str, NoulQuestion]:
    names = {"asker": snapshot.teams[asker].name, "partner": snapshot.teams[partner].name}
    return {key: NoulQuestion(q["text"].format(**names), q["yes"].format(**names), q["no"].format(**names))
            for key, q in PARTNER_FILTER.items()}


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


def offer_id(trade: ProposedTrade) -> str:
    """A stable id of an offer: each side's roster id and its given player ids, such as "4:7569-12:10236+8146"."""
    return "-".join(f"{side.roster_id}:{'+'.join(sorted(side.player_ids))}" for side in trade.sides)


def _shortlist_questions(offers: list[ProposedTrade], snapshot: Snapshot) -> dict[str, NoulQuestion]:
    """The fair question and the need question of each side of each offer, keyed "<offer n>|fair" and so on.

    The questions are those of one trade, so the shortlist and the read of one trade ask the same words.
    """
    questions = {}
    for n, trade in enumerate(offers):
        for key, question in trade_jev_questions(trade, snapshot).items():
            if key == "fair" or key.startswith("need."):
                questions[f"{n}|{key}"] = question
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


def search(asker: int, partner: int | None, snapshot: Snapshot, jev: Jev, waves: JevWaves | None = None,
           stage: Stage = quiet, anchor: Anchor | None = None, limit: Limit | None = None) -> Shortlist:
    """The Finder search of the asker: with no partner over every other team, else over the picked partner alone.

    1. The partner filter: four Jev questions per partner. Only a partner with four yes answers goes on. A search with
       an anchor skips it, and every partner goes on.
    2. The targets: Jev rates each pool player of each side. A target needs TARGET_AT, at most TARGET_MAX per side.
    3. The offers: code builds them from the targets only, under the hard rules.
    4. The shortlist: Jev asks the fair and the need questions of each offer. The SHORTLIST_KEEP offers with the
       highest product stay.
    A failed Jev request drops what it would judge, and it logs. It never reads as a no and never stops the press.
    With an `anchor`, he is a target of his side, and each offer holds him on that side (a hard rule). An anchor that
    the asker gets keeps the search to his roster, because only that roster can give him.
    With a `limit`, no offer sends a player that the manager keeps, and each offer brings back the position that he
    aims at (a hard rule, because the manager set it).
    `stage` gets one plain line after the partner filter, the offers, and the shortlist. The default drops them.
    """
    waves = waves or JevWaves(jev)
    if anchor is not None and anchor.side == "gets":
        # A player who left each roster since the pick keeps the partner, and no offer can hold him.
        partner = next((rid for rid, roster in snapshot.rosters.items() if anchor.player_id in roster), partner)
    partners = [partner] if partner is not None else sorted(rid for rid in snapshot.rosters if rid != asker)
    stage(f"Checking {len(partners)} teams for a fit" if len(partners) > 1 else "Checking the other team for a fit",
          live=True)

    reads: list[PartnerRead] = []
    if anchor is not None:
        # The filter asks about the weakest slots of each team. The anchor names the player the trade turns on, and the
        # anchor target question asks who fills his spot, so every partner goes on to the targets.
        reads = [PartnerRead(roster_id=rid, team=snapshot.teams[rid].name, answers={}, passed=True, failed=False)
                 for rid in partners]
        log.info("Partner filter of %s: skipped for the anchor", snapshot.teams[asker].name)
    else:
        filtered = waves.ask({str(rid): WaveRequest(_pair_state(snapshot, asker, rid),
                                                    _filter_questions(snapshot, asker, rid)) for rid in partners},
                             "partner filter")
        for rid in partners:
            response = filtered[str(rid)]
            answers = response.nouls if response is not None else {}
            passed = response is not None and all(answers[key] > YES_AT for key in PARTNER_FILTER)
            reads.append(PartnerRead(roster_id=rid, team=snapshot.teams[rid].name, answers=answers, passed=passed,
                                     failed=response is None))
            log.info("Partner filter of %s with %s: %s, %s", snapshot.teams[asker].name, snapshot.teams[rid].name,
                     "passed" if passed else "failed request" if response is None else "stopped",
                     ", ".join(f"{key}={p:.2f}" for key, p in answers.items()))
    passing = [read.roster_id for read in reads if read.passed]
    stage(f"Checked {len(partners)} teams for a fit" if len(partners) > 1 else "Checked the other team for a fit")
    stage("Building offers", live=True)

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
    offers = [trade for rid in offers_by_partner for trade in offers_by_partner[rid]]
    log.info("Finder offers of %s: %d", snapshot.teams[asker].name, len(offers))
    stage(f"Built {len(offers)} offers" if len(offers) != 1 else "Built one offer")
    stage("Weighing the offers", live=True)
    for trade in offers:
        _log_offer(snapshot, trade)

    judged = waves.ask({str(rid): WaveRequest(_pair_state(snapshot, asker, rid),
                                              _shortlist_questions(offers_by_partner[rid], snapshot))
                        for rid in offers_by_partner if offers_by_partner[rid]}, "shortlist")
    rated_offers = []
    for rid, partner_offers in offers_by_partner.items():
        response = judged.get(str(rid))
        if response is None:
            continue
        for n, trade in enumerate(partner_offers):
            fair = response.nouls[f"{n}|fair"]
            needs = {side.roster_id: response.nouls[f"{n}|need.{side.roster_id}"] for side in trade.sides}
            score = fair
            for p in needs.values():
                score *= p
            rated_offers.append(ShortlistOffer(offer_id=offer_id(trade), trade=trade, fair=fair, needs=needs,
                                               score=score))
    stage(f"Weighed {len(rated_offers)} offers" if len(rated_offers) != 1 else "Weighed one offer")
    shortlist = sorted(rated_offers, key=lambda offer: (-offer.score, offer.offer_id))[:SHORTLIST_KEEP]
    for offer in shortlist:
        log.info("Finder shortlist %s: score=%.3f fair=%.2f needs=%s", offer.offer_id, offer.score, offer.fair,
                 {rid: round(p, 2) for rid, p in offer.needs.items()})
    return Shortlist(asker=asker, partners=reads, targets=targets, offers=offers, shortlist=shortlist)
