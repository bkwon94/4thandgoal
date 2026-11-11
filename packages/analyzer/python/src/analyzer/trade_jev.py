"""
The Jev answers of one trade: is it fair, does each side need it, and would each other manager accept it.
Code builds the state and asks one request, and each answer joins the fact sheet of the Advisor as a JEV fact.
"""
import logging
import re

from analyzer.trade import ProposedTrade
from analyzer.trade_facts import shown_ranks
from facts.tokens import Nums, fact
from league.jev_port import Jev, JevError, NoulQuestion
from league.league_settings import LeagueSettings
from league.lineup import FLEX_SLOTS, lineup_now
from league.models import Fact
from league.snapshot import Snapshot

log = logging.getLogger(__name__)

# This wording of the fairness and the need questions won a live probe against other wordings of the same questions.
FAIR = {
    "text": "Is this trade close to fair for {who}: {gives}?",
    "yes": "Each team gives about as much as it gets, by points, rank, and trade value.",
    "no": "One team gives clearly more than it gets."}
NEED = {
    "text": "Does {team} fill a starting need in this trade, where it gets {gets}?",
    "yes": "A player {team} gets would start over a weak starter in `teams.{path}.weak_starting_slots`.",
    "no": "Each player {team} gets would sit behind the current starters of {team}."}
ACCEPT = {
    "text": "Would the manager of {other} accept this trade?",
    "yes": "The manager of {other}, who looks a lot at recent points, sees the trade as good for his team.",
    "no": "The manager of {other} sees the trade as a loss for his team."}

# The positions a trade may hold. A kicker and a defense are never in a Finder offer (a hard rule), and no question
# of a trade reads their slots.
TRADE_POSITIONS = ("QB", "RB", "WR", "TE")
# The TypeSafe default thresholds of a Noul: above 0.7 reads as yes, below 0.3 as no, and the band between as unsure.
YES_AT, NO_AT = 0.7, 0.3
FACT_PREFIX = "JEV."


def _word(p: float) -> str:
    return "yes" if p > YES_AT else "no" if p < NO_AT else "unsure"


def _player(snapshot: Snapshot, pid: str) -> str:
    """A player as a person reads him: the name, the position, the NFL team, and his Season rank when he has one."""
    player = snapshot.players[pid]
    season, _ = shown_ranks(snapshot, pid)
    rank = f", Season rank {season}" if season else ""
    return f"{player.name} ({player.position}, {player.nfl_team or 'no team'}{rank})"


def _weak_limit(settings: LeagueSettings, slot_name: str, roster_slot: str, position: str) -> int:
    """The last rank a starter of the slot may hold before he is weak, from the size and the lines of the league.

    A numbered slot such as RB2 reads the team count times its number, so each team starts one player of each tier.
    A FLEX slot reads the line of the position of its player. GLOSSARY.md, "The line".
    """
    if roster_slot in FLEX_SLOTS:
        return settings.lines[position]
    number = re.search(r"\d+$", slot_name)
    return settings.team_count * (int(number.group()) if number else 1)


def weak_slot_rows(snapshot: Snapshot, roster_id: int) -> list[dict]:
    """The starting slots of the best lineup with no player or a starter past the weak rank, one row each: the slot, the
    player, his position, his projected rank at his position, and whether he can play now.

    A K or DEF slot is never weak, because no question of the trade reads it. A player who cannot play now, such as
    a player on IR, fills no slot, so his slot is empty or holds the player behind him, and each row can play now.
    """
    rows = []
    for slot in lineup_now(snapshot.rosters[roster_id], snapshot):
        if slot.roster_slot not in FLEX_SLOTS and slot.roster_slot not in TRADE_POSITIONS:
            continue
        player = None if slot.player is None else snapshot.players[slot.player]
        if player is not None and slot.rank is not None and slot.rank <= _weak_limit(
                snapshot.client.settings, slot.name, slot.roster_slot, player.position):
            continue
        rows.append({"slot": slot.name, "player": player and player.name, "position": player and player.position,
                     "projected_rank_at_position": player and slot.rank, "can_play_now": True})
    return rows


def weak_starting_slots(snapshot: Snapshot, roster_id: int) -> list[str]:
    """The weak slot rows as lines, such as "RB2: X (RB31)" or "QB: empty", as the questions of a trade read them."""
    lines = []
    for row in weak_slot_rows(snapshot, roster_id):
        if row["player"] is None:
            lines.append(f"{row['slot']}: empty")
            continue
        rank = row["projected_rank_at_position"]
        shown = f"{row['position']}{rank}" if rank is not None else "no rank"
        lines.append(f"{row['slot']}: {row['player']} ({shown})")
    return lines


def _paths(trade: ProposedTrade) -> dict[int, str]:
    """The key of each side under `teams` in the state: the asker, then "partner" or "partner_1", "partner_2", ..."""
    others = [side.roster_id for side in trade.sides if side.roster_id != trade.asker]
    if len(others) == 1:
        return {trade.asker: "asker", others[0]: "partner"}
    return {trade.asker: "asker", **{rid: f"partner_{n}" for n, rid in enumerate(others, start=1)}}


def _joined(items: list[str]) -> str:
    if len(items) <= 2:
        return " and ".join(items)
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def trade_jev_state(trade: ProposedTrade, snapshot: Snapshot) -> dict:
    """The state of the request: each team of the trade by its path, with what it gives, gets, and lacks."""
    paths = _paths(trade)
    return {"teams": {
        paths[side.roster_id]: {
            "name": snapshot.teams[side.roster_id].name,
            "gives": [_player(snapshot, pid) for pid in side.player_ids],
            "gets": [_player(snapshot, pid) for pid in trade.gets(side.roster_id)],
            "weak_starting_slots": weak_starting_slots(snapshot, side.roster_id),
        }
        for side in trade.sides
    }}


def trade_jev_questions(trade: ProposedTrade, snapshot: Snapshot) -> dict[str, NoulQuestion]:
    """The questions by key: "fair", "need.<roster id>" for every side, and "accept.<roster id>" for each other side."""
    paths = _paths(trade)
    name = {side.roster_id: snapshot.teams[side.roster_id].name for side in trade.sides}
    players = {pid: snapshot.players[pid].name for pid in trade.player_ids}
    gives = _joined([f"{name[side.roster_id]} gives {_joined([players[p] for p in side.player_ids])}"
                     for side in trade.sides])
    who = "both teams" if len(trade.sides) == 2 else "every team"
    questions = {"fair": NoulQuestion(FAIR["text"].format(who=who, gives=gives), FAIR["yes"], FAIR["no"])}
    for side in trade.sides:
        rid = side.roster_id
        fill = {"team": name[rid], "path": paths[rid], "gets": _joined([players[p] for p in trade.gets(rid)])}
        questions[f"need.{rid}"] = NoulQuestion(NEED["text"].format(**fill), NEED["yes"].format(**fill),
                                                NEED["no"].format(**fill))
    for side in trade.sides:
        if side.roster_id != trade.asker:
            other = name[side.roster_id]
            questions[f"accept.{side.roster_id}"] = NoulQuestion(
                ACCEPT["text"].format(other=other), ACCEPT["yes"].format(other=other),
                ACCEPT["no"].format(other=other))
    return questions


def trade_jev_facts(trade: ProposedTrade, snapshot: Snapshot, jev: Jev) -> dict[str, Fact]:
    """The Jev answers of the trade as facts by id, such as JEV.fair and JEV.need.4. Empty after a failed call.

    A Jev answer is an input of the Advisor, not the call, so a failed request logs and the read goes on with no answer.
    A fact holds the answer as a word and never the probability, so no probability reaches the prose.
    """
    questions = trade_jev_questions(trade, snapshot)
    try:
        response = jev.ask(trade_jev_state(trade, snapshot), questions)
    except JevError as error:
        log.warning("The Jev request of the trade failed, so the sheet has no Jev answer: %s", error)
        return {}
    log.info("The Jev request of the trade: model=%s input_tokens=%s", response.model, response.input_tokens)
    return jev_answer_facts(trade, snapshot, questions, response.nouls)


def jev_answer_facts(trade: ProposedTrade, snapshot: Snapshot, questions: dict[str, NoulQuestion],
                     nouls: dict[str, float]) -> dict[str, Fact]:
    """The Jev answers by question key as facts by id, such as JEV.fair. The Finder pick passes the answers of its
    shortlist here, so a pick sheet holds the same words as the sheet of one trade, with no new Jev call."""
    facts = {}
    for key, p in nouls.items():
        _, _, rid = key.partition(".")
        teams = [snapshot.teams[int(rid)].name] if rid else []
        asked = str(questions[key].instructions)
        # The question names players, so the fact lists them, and a Bullet that cites it may name them.
        named = [snapshot.players[pid].name for pid in trade.player_ids if snapshot.players[pid].name in asked]
        text = f"A quick yes or no read of a small model on \"{asked}\": {_word(p)}."
        facts[f"{FACT_PREFIX}{key}"] = fact(f"{FACT_PREFIX}{key}", text, Nums(), teams, named)
    return facts
