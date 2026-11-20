"""
The backtest of the Finder: the list of Spares tree stops and passes that Brian marks, and the check of each mark.
A mark is a wrong line or a bad trade with Brian's fix. The check asks the live Jev, so `make check-fast` never runs it.
"""
import json
from itertools import combinations
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from analyzer.finder_search import gain_dropped, lineup_line, step_two_answers
from analyzer.jev_waves import JevWaves
from analyzer.spares_tree import Spare, pair_request, pair_spares, stopped_sides
from analyzer.trade import GivenPlayer, ProposedTrade, TradeSide
from league.jev_port import Jev, JevError
from league.snapshot import Snapshot

# The list is about 30 lines, so Brian marks it in about 10 minutes (decision 05).
LIST_LINES = 30


class SideOutcome(BaseModel):
    """One side of the Spares tree: what `giver` can give `receiver`, the Jev answer of each listed player, and the
    result. A failed request is an error, never a stop."""

    giver: int
    receiver: int
    spares: list[Spare]
    answers: dict[str, float]
    stopped: bool
    failed: bool = False


class Mark(BaseModel):
    """One Backtest mark: a trade that the gain check must drop or keep, or a side of the Spares tree that must stop or
    pass. Teams and players go by name, as Brian reads the list."""

    id: int
    kind: Literal["trade", "spares"]
    expect: Literal["drop", "keep", "stop", "pass"]
    # A trade mark: the asker, the partner, and the players by name.
    asker: str | None = None
    partner: str | None = None
    asker_gives: list[str] = []
    asker_gets: list[str] = []
    # A spares mark: the team that gives and the team that gets.
    giver: str | None = None
    receiver: str | None = None
    # Brian's fix in his words.
    note: str = ""


class MarkResult(BaseModel):
    """The check of one mark: what the tree did now, whether that matches the mark, and the answers that decided it."""

    mark: Mark
    got: Literal["drop", "keep", "stop", "pass", "error"]
    right: bool
    why: str


def load_marks(path: Path) -> list[Mark]:
    """The marks of the JSON file at `path`, a list of objects in the shape of Mark."""
    return [Mark.model_validate(item) for item in json.loads(path.read_text(encoding="utf-8"))]


def run_spares(snapshot: Snapshot, jev: Jev) -> list[SideOutcome]:
    """The Spares tree on both sides of every pair of teams, one Jev request per pair, sent in waves."""
    pairs = list(combinations(sorted(snapshot.rosters), 2))
    spares = {pair: pair_spares(snapshot, *pair) for pair in pairs}
    requests = {f"{a}:{b}": pair_request(snapshot, a, b, spares[(a, b)]) for a, b in pairs}
    responses = JevWaves(jev).ask({key: request for key, request in requests.items() if request is not None},
                                  "spares list")
    outcomes = []
    for a, b in pairs:
        key = f"{a}:{b}"
        failed = requests[key] is not None and responses.get(key) is None
        response = responses.get(key)
        answers = {} if response is None else response.nouls
        stopped = [] if failed else stopped_sides(spares[(a, b)], answers)
        # The "partner" side lists what b gives a, and the "asker" side what a gives b.
        for side, giver, receiver in (("asker", a, b), ("partner", b, a)):
            outcomes.append(SideOutcome(giver=giver, receiver=receiver, spares=spares[(a, b)][side], answers=answers,
                                        stopped=side in stopped, failed=failed))
    return outcomes


def _over(snapshot: Snapshot, spare: Spare, answers: dict[str, float]) -> str:
    return f"{snapshot.players[spare.player_id].name} over {spare.starter} ({answers[spare.key]:.2f})"


def _line(snapshot: Snapshot, outcome: SideOutcome) -> str:
    giver, receiver = snapshot.teams[outcome.giver].name, snapshot.teams[outcome.receiver].name
    if outcome.stopped:
        return (f"Stop: {giver} gives {receiver} no one. Jev says no for each listed player: "
                + "; ".join(_over(snapshot, spare, outcome.answers) for spare in outcome.spares) + ".")
    best = max(outcome.spares, key=lambda spare: outcome.answers[spare.key])
    return f"Pass: {giver} can give {receiver} a player. Jev says {_over(snapshot, best, outcome.answers)}."


def _best(outcome: SideOutcome) -> float:
    return max(outcome.answers[spare.key] for spare in outcome.spares)


def _spread(items: list[SideOutcome], count: int) -> list[SideOutcome]:
    """`count` items spread evenly over the list, first and last included, so the sample covers the whole range."""
    if count <= 0:
        return []
    if count >= len(items):
        return items
    if count == 1:
        return items[:1]
    return [items[round(i * (len(items) - 1) / (count - 1))] for i in range(count)]


def list_lines(snapshot: Snapshot, outcomes: list[SideOutcome], limit: int = LIST_LINES) -> list[str]:
    """The numbered list for Brian, at most `limit` lines, then plain count lines.

    Each Jev stop comes first, because a stop removes a partner. The passes fill the rest, spread from the weakest
    deciding answer to the strongest, so the list shows unsure and clear passes. The deciding answer of a pass is its
    highest answer, because one yes or unsure answer passes a side.
    """
    judged = [outcome for outcome in outcomes if outcome.spares and not outcome.failed]
    stops = sorted((o for o in judged if o.stopped), key=lambda o: (max(o.answers[s.key] for s in o.spares),
                                                                     o.giver, o.receiver))
    passes = sorted((o for o in judged if not o.stopped), key=lambda o: (_best(o), o.giver, o.receiver))
    chosen = stops[:limit] + _spread(passes, limit - len(stops[:limit]))
    lines = [f"{n}. {_line(snapshot, outcome)}" for n, outcome in enumerate(chosen, start=1)]
    lines.append(f"{sum(not o.spares for o in outcomes)} sides list no player, so the count rule stops them with "
                 "no Jev answer.")
    lines.append(f"{len(stops)} sides stop on Jev answers, and {len(passes)} sides pass. "
                 f"The list shows {len(chosen)} of them.")
    failed = sum(o.failed for o in outcomes)
    if failed:
        lines.append(f"{failed} sides have no answer, because their Jev request failed.")
    return lines


def _roster_of(snapshot: Snapshot, name: str) -> int:
    return next(rid for rid, team in snapshot.teams.items() if team.name == name)


def _player_of(snapshot: Snapshot, roster_id: int, name: str) -> str:
    return next(pid for pid in snapshot.rosters[roster_id] if snapshot.players[pid].name == name)


def _check_trade(mark: Mark, snapshot: Snapshot, jev: Jev) -> MarkResult:
    asker, partner = _roster_of(snapshot, mark.asker or ""), _roster_of(snapshot, mark.partner or "")
    trade = ProposedTrade(season=snapshot.season, asker=asker, sides=(
        TradeSide(roster_id=asker, gives=[GivenPlayer(player_id=_player_of(snapshot, asker, name), to=partner)
                                          for name in mark.asker_gives]),
        TradeSide(roster_id=partner, gives=[GivenPlayer(player_id=_player_of(snapshot, partner, name), to=asker)
                                            for name in mark.asker_gets])))
    try:
        answers = step_two_answers(snapshot, trade, jev)
    except JevError as error:
        return MarkResult(mark=mark, got="error", right=False, why=f"the Jev request failed: {error}")
    gains = {rid: answers[f"gain.{rid}"] for rid in (asker, partner)}
    got: Literal["drop", "keep"] = "drop" if gain_dropped(gains) else "keep"
    why = "gain " + ", ".join(f"{snapshot.teams[rid].name} {p:.2f}" for rid, p in gains.items())
    why += "; " + " ".join(lineup_line(snapshot, trade, rid) for rid in (asker, partner))
    return MarkResult(mark=mark, got=got, right=got == mark.expect, why=why)


def _check_side(mark: Mark, snapshot: Snapshot, jev: Jev) -> MarkResult:
    giver, receiver = _roster_of(snapshot, mark.giver or ""), _roster_of(snapshot, mark.receiver or "")
    spares = pair_spares(snapshot, giver, receiver)
    request = pair_request(snapshot, giver, receiver, spares)
    try:
        answers = {} if request is None else jev.ask(request.state, request.questions).nouls
    except JevError as error:
        return MarkResult(mark=mark, got="error", right=False, why=f"the Jev request failed: {error}")
    outcome = SideOutcome(giver=giver, receiver=receiver, spares=spares["asker"], answers=answers,
                          stopped="asker" in stopped_sides(spares, answers))
    got: Literal["stop", "pass"] = "stop" if outcome.stopped else "pass"
    why = "no listed player" if not outcome.spares else _line(snapshot, outcome)
    return MarkResult(mark=mark, got=got, right=got == mark.expect, why=why)


def check_marks(marks: list[Mark], snapshot: Snapshot, jev: Jev) -> list[MarkResult]:
    """The check of each mark against the tree now: a trade mark asks the step 2 request of that one offer, and a
    spares mark asks the Spares tree of its pair. A failed call is an error, and an error is never a right mark."""
    return [(_check_trade if mark.kind == "trade" else _check_side)(mark, snapshot, jev) for mark in marks]


def backtest_lines(results: list[MarkResult]) -> list[str]:
    """One line per mark with its result, then the count of right marks."""
    lines = []
    for result in results:
        mark = result.mark
        what = (f"{mark.asker} gives {' and '.join(mark.asker_gives)} for {' and '.join(mark.asker_gets)}"
                if mark.kind == "trade" else f"{mark.giver} spares a player for {mark.receiver}")
        outcome = "RIGHT" if result.right else "WRONG"
        lines.append(f"{mark.id}. {outcome}: {what}. Expect {mark.expect}, got {result.got}. {result.why}")
    lines.append(f"Right marks: {sum(r.right for r in results)} of {len(results)}.")
    return lines
