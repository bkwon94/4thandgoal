"""
The Finder search: the partner filter, the targets, the offers, and the shortlist, as a manager searches.
Jev judgments narrow each list, in waves under the rate limits. Code builds the offers and keeps only the hard rules.
"""
import logging
from itertools import combinations

from pydantic import BaseModel

from analyzer.adjusters import is_handcuff, trade_handcuffs
from analyzer.jev_waves import JevWaves, WaveRequest
from analyzer.rubric import GivenPlayer, ProposedTrade, TradeSide
from analyzer.trade_facts import shown_ranks
from analyzer.trade_jev import YES_AT, trade_jev_questions, weak_starting_slots
from league.jev_port import Jev, NoulQuestion
from league.lineup import _above_the_line, lineup_slots
from league.ranks import OUT_STATUSES
from league.snapshot import Snapshot

log = logging.getLogger(__name__)

# The positions a Finder offer may hold. A kicker and a defense are never in an offer (a hard rule).
TRADE_POSITIONS = ("QB", "RB", "WR", "TE")

# The four questions of the partner filter, from the glossary entry "Partner filter". Each asks one judgment, and
# the state holds the depth that code counts, because Jev does not count reliably.
PARTNER_FILTER = {
    # The "has" wording that names the weak starters won a live probe on 4 pairs on 2026-11-09: about 0.85 against
    # about 0.6 for "a player at a weak starting slot", which Jev read as unsure.
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
# The target question of prototype 04 (decision 04 notes): one Noul per player of the other side.
TARGET = {
    "text": "Would {team} want {player} from {owner}?",
    "yes": "{name} would start for {team} or fill a weak spot on its roster.",
    "no": "{name} would sit behind better players at his position on {team}."}
TARGET_AT = 0.6      # a player is a target at this probability or more
TARGET_MAX = 4       # at most this many targets per side, by probability
SHORTLIST_KEEP = 10  # the offers that Jev rates highest, by the product of the fair and the need answers


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
    starters = {slot.player for slot in lineup_slots(roster, snapshot) if slot.player is not None}
    players = [pid for pid in roster if snapshot.players[pid].position in TRADE_POSITIONS]
    depth = {pos: sum(1 for pid in players if snapshot.players[pid].position == pos and _above_the_line(snapshot, pid))
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


def _target_questions(snapshot: Snapshot, asker: int, partner: int) -> dict[str, NoulQuestion]:
    """One question per pool player of each side: "<roster id>.<player id>" asks if the other side wants him."""
    questions = {}
    for owner, team in ((partner, asker), (asker, partner)):
        fill = {"team": snapshot.teams[team].name, "owner": snapshot.teams[owner].name}
        for pid in snapshot.rosters[owner]:
            if not in_pool(snapshot, pid, owner):
                continue
            words = {**fill, "player": _described(snapshot, pid), "name": snapshot.players[pid].name}
            questions[f"{owner}.{pid}"] = NoulQuestion(
                TARGET["text"].format(**words), TARGET["yes"].format(**words), TARGET["no"].format(**words))
    return questions


def _pick_targets(nouls: dict[str, float], owner: int) -> list[str]:
    """The players of `owner` at p TARGET_AT or more, the highest first, at most TARGET_MAX. The id breaks a tie."""
    rated = [(p, key.partition(".")[2]) for key, p in nouls.items()
             if key.partition(".")[0] == str(owner) and p >= TARGET_AT]
    return [pid for _, pid in sorted(rated, key=lambda item: (-item[0], item[1]))[:TARGET_MAX]]


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


def search(asker: int, partner: int | None, snapshot: Snapshot, jev: Jev, waves: JevWaves | None = None) -> Shortlist:
    """The Finder search of the asker: with no partner over every other team, else over the picked partner alone.

    1. The partner filter: four Jev questions per partner. Only a partner with four yes answers goes on.
    2. The targets: Jev rates each pool player of each side. A target needs TARGET_AT, at most TARGET_MAX per side.
    3. The offers: code builds them from the targets only, under the hard rules.
    4. The shortlist: Jev asks the fair and the need questions of each offer. The SHORTLIST_KEEP offers with the
       highest product stay.
    A failed Jev request drops what it would judge, and it logs. It never reads as a no and never stops the press.
    """
    waves = waves or JevWaves(jev)
    partners = [partner] if partner is not None else sorted(rid for rid in snapshot.rosters if rid != asker)

    filtered = waves.ask({str(rid): WaveRequest(_pair_state(snapshot, asker, rid),
                                                _filter_questions(snapshot, asker, rid)) for rid in partners},
                         "partner filter")
    reads = []
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

    rated = waves.ask({str(rid): WaveRequest(_pair_state(snapshot, asker, rid), _target_questions(snapshot, asker, rid))
                       for rid in passing}, "targets")
    targets: dict[int, dict[str, list[str]]] = {}
    offers_by_partner: dict[int, list[ProposedTrade]] = {}
    for rid in passing:
        response = rated[str(rid)]
        if response is None:
            continue
        sides = {"asker": _pick_targets(response.nouls, asker), "partner": _pick_targets(response.nouls, rid)}
        targets[rid] = sides
        log.info("Finder targets with %s: the asker gives %s; the partner gives %s", snapshot.teams[rid].name,
                 [snapshot.players[pid].name for pid in sides["asker"]],
                 [snapshot.players[pid].name for pid in sides["partner"]])
        offers_by_partner[rid] = build_offers(asker, rid, sides["asker"], sides["partner"], snapshot)
    offers = [trade for rid in offers_by_partner for trade in offers_by_partner[rid]]
    log.info("Finder offers of %s: %d", snapshot.teams[asker].name, len(offers))
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
    shortlist = sorted(rated_offers, key=lambda offer: (-offer.score, offer.offer_id))[:SHORTLIST_KEEP]
    for offer in shortlist:
        log.info("Finder shortlist %s: score=%.3f fair=%.2f needs=%s", offer.offer_id, offer.score, offer.fair,
                 {rid: round(p, 2) for rid, p in offer.needs.items()})
    return Shortlist(asker=asker, partners=reads, targets=targets, offers=offers, shortlist=shortlist)
