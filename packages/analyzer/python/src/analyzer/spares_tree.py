"""
The Spares tree: code lists the players a team can spare at a weak starting slot of another team, Jev asks one Noul
per listed player, and code decides if each side of a pair goes on. It runs for one pair, so a backtest can run it.
"""
from typing import Literal

from pydantic import BaseModel

from analyzer.jev_waves import WaveRequest
from analyzer.trade_jev import NO_AT, TRADE_POSITIONS, weak_slot_rows, weak_starting_slots
from league.jev_port import Jev, NoulQuestion
from league.lineup import above_the_line, cannot_play_now
from league.ranks import OUT_STATUSES
from league.snapshot import Snapshot

# The one Noul of each listed player. Decision 05 sets the words. The chart values sit in the state as facts, so Jev
# compares no numbers.
SPARE = {
    "text": "Would {player} start over {starter} of {team} for the rest of the season?",
    "yes": "{name} would score more than {starter} for the rest of the season, so {team} would start him.",
    "no": "{starter} would still start for {team} over {name}."}

Side = Literal["partner", "asker"]


class Spare(BaseModel):
    """One listed player: the team that gives him, the team that gets him, and the weak starter he would replace."""

    player_id: str
    giver: int
    receiver: int
    # The weak starter as the question names him, such as "Joe Back (RB2)", or "the empty RB2 slot".
    starter: str
    starter_id: str | None
    # The weak starting slot of the receiver that the listed player would fill, such as "QB" or "RB2".
    slot: str = ""

    @property
    def key(self) -> str:
        return f"spare:{self.giver}:{self.player_id}"


class SparesRead(BaseModel):
    """The Spares tree of one pair: the listed players of each side, the Jev answers by question key, and the sides
    that stop. The pair passes only when no side stops."""

    asker: int
    partner: int
    # The listed players by side: "partner" lists what the partner can give, "asker" what the asker can give.
    spares: dict[str, list[Spare]]
    answers: dict[str, float]
    stopped: list[str]

    @property
    def passed(self) -> bool:
        return not self.stopped


def can_cover(snapshot: Snapshot, player_id: str) -> bool:
    """True when the player is cover: above the line, able to play now as `lineup_now` reads it, and not listed Out.

    A player who is Out is never cover, so a team never spares a starter whose only backup is hurt (decision 09).
    """
    return (above_the_line(snapshot, player_id) and not cannot_play_now(snapshot, player_id)
            and snapshot.players[player_id].injury_status not in OUT_STATUSES)


def _weak_starters(snapshot: Snapshot, roster_id: int) -> dict[str, tuple[str, str | None, str]]:
    """The weakest starter at each trade position of the weak slots: the words of the question, his player id, and
    the slot.

    An empty slot comes first, then the starter with the worst projected rank. An empty flex slot names no position.
    """
    names = {snapshot.players[pid].name: pid for pid in snapshot.rosters[roster_id]}
    worst: dict[str, tuple[tuple, str, str | None, str]] = {}
    for row in weak_slot_rows(snapshot, roster_id):
        position = row["position"] or row["slot"].rstrip("0123456789")
        if position not in TRADE_POSITIONS:
            continue
        if row["player"] is None:
            order: tuple = (0, 0)
            words, pid = f"the empty {row['slot']} slot", None
        else:
            rank = row["projected_rank_at_position"]
            order = (1, -(rank if rank is not None else 10_000))
            words, pid = f"{row['player']} ({row['slot']})", names.get(row["player"])
        if position not in worst or order < worst[position][0]:
            worst[position] = (order, words, pid, row["slot"])
    return {position: (words, pid, slot) for position, (_, words, pid, slot) in worst.items()}


def spare_list(snapshot: Snapshot, giver: int, receiver: int) -> list[Spare]:
    """Each player of `giver` at the position of a weak starting slot of `receiver`, when `giver` has another player at
    that position as cover. This is the count rule of the tree, the literal reading of decision 12.

    A listed player is at a trade position and not out with no return week. Jev judges each one, so code cuts no more.
    """
    # Imported here: finder_search imports this module for its partner filter.
    from analyzer.finder_search import in_pool

    starters = _weak_starters(snapshot, receiver)
    roster = snapshot.rosters[giver]
    spares = []
    for pid in roster:
        position = snapshot.players[pid].position
        if position not in starters or not in_pool(snapshot, pid, giver):
            continue
        if not any(other != pid and snapshot.players[other].position == position and can_cover(snapshot, other)
                   for other in roster):
            continue
        words, starter_id, slot = starters[position]
        spares.append(Spare(player_id=pid, giver=giver, receiver=receiver, starter=words, starter_id=starter_id,
                            slot=slot))
    return spares


def pair_spares(snapshot: Snapshot, asker: int, partner: int) -> dict[str, list[Spare]]:
    """The listed players of both sides of a pair: what the partner can give the asker, and the reverse."""
    return {"partner": spare_list(snapshot, partner, asker), "asker": spare_list(snapshot, asker, partner)}


def _described(snapshot: Snapshot, pid: str) -> str:
    player = snapshot.players[pid]
    return f"{player.name} ({player.position}, {player.nfl_team or 'no team'})"


def _chart_line(snapshot: Snapshot, spare: Spare) -> str:
    """The chart values of the listed player and his weak starter as one fact, such as "The chart has X at 31 and
    Y at 22." A player off the chart is named as such. Code knows the numbers, so Jev only reads them."""
    if snapshot.chart is None:
        return f"The chart of week {snapshot.week} is missing, so no player has a chart value."
    values = snapshot.chart.values

    def value(pid: str) -> str:
        name = snapshot.players[pid].name
        return f"{name} at {values[pid]}" if pid in values else f"{name} off the chart"

    team = snapshot.teams[spare.receiver].name
    if spare.starter_id is None:
        return f"The chart has {value(spare.player_id)}. {team} has {spare.starter}."
    return f"The chart has {value(spare.player_id)} and {value(spare.starter_id)}, the weak starter of {team}."


def pair_request(snapshot: Snapshot, asker: int, partner: int,
                 spares: dict[str, list[Spare]]) -> WaveRequest | None:
    """The one Jev request of a pair: one Noul per listed player of both sides, keyed "spare:<giver>:<player id>".
    None when neither side lists a player, because then no question needs an answer."""
    listed = spares["partner"] + spares["asker"]
    if not listed:
        return None
    questions = {}
    for spare in listed:
        team = snapshot.teams[spare.receiver].name
        words = {"player": _described(snapshot, spare.player_id), "name": snapshot.players[spare.player_id].name,
                 "starter": spare.starter, "team": team}
        questions[spare.key] = NoulQuestion(SPARE["text"].format(**words), SPARE["yes"].format(**words),
                                            SPARE["no"].format(**words))
    state = {"teams": {side: {"roster_id": rid, "name": snapshot.teams[rid].name,
                              "weak_starting_slots": weak_starting_slots(snapshot, rid)}
                       for side, rid in (("asker", asker), ("partner", partner))},
             "chart": [_chart_line(snapshot, spare) for spare in listed]}
    return WaveRequest(state, questions)


def stopped_sides(spares: dict[str, list[Spare]], answers: dict[str, float]) -> list[str]:
    """The sides that stop. A side stops only if it lists no player, or if each listed player gets a clear no, below
    NO_AT. A yes or an unsure answer passes. A failed call never reaches here, because it is an error, not a stop."""
    return [side for side in ("partner", "asker")
            if not spares[side] or all(answers[spare.key] < NO_AT for spare in spares[side])]


def read_pair(asker: int, partner: int, spares: dict[str, list[Spare]], answers: dict[str, float]) -> SparesRead:
    """The read of one pair from its listed players and the Jev answers of its request."""
    return SparesRead(asker=asker, partner=partner, spares=spares, answers=answers,
                      stopped=stopped_sides(spares, answers))


def spares_tree(snapshot: Snapshot, asker: int, partner: int, jev: Jev) -> SparesRead:
    """The Spares tree of one pair, on both sides, with one Jev request. A failed request raises its JevError, because
    a failed call is an error and never a stop."""
    spares = pair_spares(snapshot, asker, partner)
    request = pair_request(snapshot, asker, partner, spares)
    answers = {} if request is None else jev.ask(request.state, request.questions).nouls
    return read_pair(asker, partner, spares, answers)
