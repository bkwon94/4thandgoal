"""
The lineup of a roster: the slots each position fills, the best lineup by lineup value, its starting slots with the
holes and the absences, and the bye covers. The week, the managers, the waiver board, and the analyzer all read it.
"""
from __future__ import annotations

from decimal import Decimal
from typing import NamedTuple

from league.models import ByePlayer
from league.ranks import POSITION_ORDER, RANKED_POSITIONS, due_back_week, lineup_value
from league.snapshot import Snapshot
from league.tunables import RETURN_WINDOW_WEEKS

# The positions each flex slot takes. Any other slot takes its own position only.
FLEX_SLOTS: dict[str, frozenset[str]] = {
    "FLEX": frozenset({"RB", "WR", "TE"}),
    "WRRB_FLEX": frozenset({"RB", "WR"}),
    "REC_FLEX": frozenset({"WR", "TE"}),
    "SUPER_FLEX": frozenset({"QB", "RB", "WR", "TE"}),
}


def allowed_positions(roster_slot: str) -> frozenset[str]:
    """The positions a roster slot takes: the set of a flex slot, or its own position for any other slot."""
    return FLEX_SLOTS.get(roster_slot, frozenset({roster_slot}))


# Slots that hold players who do not start.
BENCH_SLOTS = frozenset({"BN", "IR", "TAXI"})


def bye_covers(open_slots: dict[str, str], bench: dict[str, str], values: dict[str, Decimal]) -> dict[str, str | None]:
    """The bye cover of each key starter on bye, by his player id, or None when no bench player can fill his slot.

    GLOSSARY.md, "Bye cover". `open_slots` maps each key starter on bye to the roster slot he leaves open, such as
    "QB" or "FLEX". `bench` maps each bench player who can play next week to his position. `values` holds the lineup
    value of each of them. The starter with the most lineup value picks first, and each bench player covers one slot.
    """
    free = sorted(bench, key=lambda pid: (-values[pid], pid))
    covers: dict[str, str | None] = {}
    for starter in sorted(open_slots, key=lambda pid: (-values[pid], pid)):
        allowed = allowed_positions(open_slots[starter])
        cover = next((pid for pid in free if bench[pid] in allowed), None)
        if cover is not None:
            free.remove(cover)
        covers[starter] = cover
    return covers


def bye_covers_for_roster(snapshot: Snapshot, roster_id: int, byes: list[ByePlayer]) -> dict[str, str | None]:
    """The bye cover of each key starter on bye of the roster, from the slots of its best lineup.

    A key starter outside the best lineup leaves the slot of his own position open. A bench player on bye cannot
    cover, because he does not play next week either. A bench player out next week or out for the season cannot
    cover either. The trade week of the week snapshot is next week, so `_out_now` reads "out next week".
    """
    roster = snapshot.rosters.get(roster_id, [])
    slot_of = {s.player: s.roster_slot for s in lineup_slots(roster, snapshot) if s.player is not None}
    on_bye = {p.player_id for p in byes}
    open_slots = {p.player_id: slot_of.get(p.player_id, p.position) for p in byes if p.key}
    bench = {
        pid: snapshot.players[pid].position for pid in roster
        if pid not in slot_of and pid not in on_bye
        and not _out_now(snapshot, pid) and pid not in snapshot.out_for_season
    }
    return bye_covers(open_slots, bench, {pid: snapshot.lineup_value(pid) for pid in [*open_slots, *bench]})


def best_lineup(roster: list[str], slots: list[str], snapshot: Snapshot) -> list[str]:
    """The starters of the roster's best lineup, by lineup value, with the position order as the tie rule.

    The fixed slots fill first, so a flex slot takes the player with the most points per game that no fixed slot took.
    """
    positions = {pid: snapshot.players[pid].position for pid in roster}
    return pick_lineup(roster, slots, positions, {pid: lineup_value(snapshot, pid) for pid in roster})


def pick_lineup(
        roster: list[str], slots: list[str], positions: dict[str, str], points: dict[str, Decimal | float]
    ) -> list[str]:
    """The starters of the roster's best lineup by `points`, with the position order as the tie rule.

    The fixed slots fill first, so a flex slot takes the player with the most points that no fixed slot took.
    It reads plain dicts, so a caller with no Snapshot, such as the odds inputs, can rank by projections.
    """
    return [pid for _, pid in fill_slots(roster, slots, positions, points) if pid is not None]


def fill_slots(
        roster: list[str], slots: list[str], positions: dict[str, str], points: dict[str, Decimal | float]
    ) -> list[tuple[str, str | None]]:
    """Each starting slot with the player of the best lineup in it, or None when no player can fill it.

    The slots come in fill order: the fixed slots first, then the flex slots. pick_lineup reads this, so the two
    always agree on the lineup.
    """
    def position(pid: str) -> str:
        return positions[pid]

    def rank(pid: str) -> tuple[Decimal | float, int, str]:
        order = POSITION_ORDER.index(position(pid)) if position(pid) in POSITION_ORDER else len(POSITION_ORDER)
        # The player id breaks the last tie, so the same roster always gives the same lineup.
        return (-points[pid], order, pid)

    pool = sorted(roster, key=rank)
    filled: list[tuple[str, str | None]] = []
    fixed = [slot for slot in slots if slot not in BENCH_SLOTS and slot not in FLEX_SLOTS]
    flex = [slot for slot in slots if slot in FLEX_SLOTS]
    for slot in fixed + flex:
        allowed = allowed_positions(slot)
        taken = {pid for _, pid in filled}
        filled.append((slot, next((pid for pid in pool if pid not in taken and position(pid) in allowed), None)))
    return filled


# The starting slots that strength reads. GLOSSARY.md, "Strength". The flex slots and QB and TE stay out of it.
STRENGTH_SLOTS = ("RB1", "RB2", "WR1", "WR2")


class Absence(NamedTuple):
    """The week a starter is due back after the trade week, and whether a bench player covers him."""

    week: int
    covered: bool


class StartingSlot(NamedTuple):
    """One starting slot of a best lineup: its name, such as "RB2", its player or None, and his position rank."""

    name: str
    player: str | None
    rank: int | None
    # The roster slot it fills, such as "RB" or "FLEX". A FLEX slot reads the line of its player's position.
    roster_slot: str
    # His return after the trade week. None when he is not out after the trade week. A bye is never an absence.
    absence: Absence | None = None
    # True when a team in the race gets the player and he has his bye in the trade week. No cover cancels it.
    bye_now: bool = False

    def is_hole(self, snapshot: Snapshot) -> bool:
        """True when the slot is a hole. GLOSSARY.md, "Hole".

        A hole holds no player or a player below the line for his own position. A starter due back after the trade
        week with no cover is a hole too. A K or DEF slot is never a hole. A player at a ranked position with
        no rank is below the line, because he has no stat line to start on. A starter a team in the race gets, who has his
        bye in the trade week, is a hole too.
        """
        if self.roster_slot not in FLEX_SLOTS and self.roster_slot not in RANKED_POSITIONS:
            return False
        if self.player is None:
            return True
        if self.bye_now or (self.absence is not None and not self.absence.covered):
            return True
        line = snapshot.client.settings.lines.get(snapshot.players[self.player].position)
        return line is not None and (self.rank is None or self.rank > line)


def lineup_slots(roster: list[str], snapshot: Snapshot) -> list[StartingSlot]:
    """The starting slots of the roster's best lineup, each with its player and his position rank, in fill order.

    A slot that appears more than once gets a number, such as RB1 and RB2, so the reason can name it.
    RB1 holds the back with the most points per game, because the fixed slots fill in that order.
    """
    positions = {pid: snapshot.players[pid].position for pid in roster}
    filled = fill_slots(roster, snapshot.roster_positions, positions,
                        {pid: snapshot.lineup_value(pid) for pid in roster})
    counts = {slot: sum(1 for each, _ in filled if each == slot) for slot, _ in filled}
    seen: dict[str, int] = {}
    starting = []
    for slot, pid in filled:
        seen[slot] = seen.get(slot, 0) + 1
        name = f"{slot}{seen[slot]}" if counts[slot] > 1 else slot
        starting.append(StartingSlot(name=name, player=pid, rank=None if pid is None else snapshot.position_rank(pid),
                                     roster_slot=slot))
    return _with_absences(starting, [pid for pid in roster if pid not in {slot.player for slot in starting}],
                          snapshot)


def lineup_now(roster: list[str], snapshot: Snapshot) -> list[StartingSlot]:
    """The starting slots of the best lineup of the players who can play in the trade week, as lineup_slots gives.

    A player out after the trade week, such as a player on IR with no return week, or a player out for the season,
    cannot start now, so he fills no slot. A slot with no player who can play is empty. The trade code reads this, so
    a team whose only QB is on IR has an empty QB slot. The hole read keeps lineup_slots, which marks his absence.
    """
    return lineup_slots([pid for pid in roster if not cannot_play_now(snapshot, pid)], snapshot)


def cannot_play_now(snapshot: Snapshot, player_id: str) -> bool:
    """True when the player is out after the trade week or out for the season."""
    return _out_now(snapshot, player_id) or player_id in snapshot.out_for_season


def _last_window_week(snapshot: Snapshot) -> int:
    """The last week of the return window, which starts at the trade week."""
    return snapshot.week + RETURN_WINDOW_WEEKS


def above_the_line(snapshot: Snapshot, player_id: str) -> bool:
    """True when the player holds a position rank at or above the line of his position. K and DEF have no line."""
    line = snapshot.client.settings.lines.get(snapshot.players[player_id].position)
    rank = snapshot.position_rank(player_id)
    return line is not None and rank is not None and rank <= line


def _out_now(snapshot: Snapshot, player_id: str) -> bool:
    """True when the player counts as back after the trade week, so he cannot play in place of a starter now.

    It reads due_back_week, so a player out with no return week counts as out too.
    """
    week = due_back_week(snapshot, player_id)
    return week is not None and week > snapshot.week


def _with_absences(starting: list[StartingSlot], bench: list[str], snapshot: Snapshot) -> list[StartingSlot]:
    """The starting slots with the return week of each starter above the line who is out, and whether a bench player
    covers him.

    GLOSSARY.md, "Hole". A bye is never an absence. A starter due back after the trade week and inside the window
    needs a cover. A starter due back after the window is a hole whatever his rank, so no cover can fix it. A cover
    is a bench player at a position the slot allows, above the line, and not out after the trade week. Each bench
    player covers one slot only, and the covers go out in slot fill order, as the best lineup fills. The best bench
    player covers first.
    """
    free = sorted(bench, key=lambda pid: (-lineup_value(snapshot, pid), pid))
    marked = []
    for slot in starting:
        # A slot with no player or a player below the line is a hole already. K and DEF have no line, so never a hole.
        if slot.player is None or not above_the_line(snapshot, slot.player):
            marked.append(slot)
            continue
        # The hole read and the lineup value read the same return week, so a player out with no return week counts
        # as back at the return-by week, past the window, and his slot is a hole.
        if not _out_now(snapshot, slot.player):
            marked.append(slot)
            continue
        week = due_back_week(snapshot, slot.player)
        allowed = allowed_positions(slot.roster_slot)
        cover = None if week > _last_window_week(snapshot) else next(
            (pid for pid in free
             if snapshot.players[pid].position in allowed
             and above_the_line(snapshot, pid)
             and not _out_now(snapshot, pid)), None)
        if cover is not None:
            free.remove(cover)
        marked.append(slot._replace(absence=Absence(week=week, covered=cover is not None)))
    return marked


def _lineup_total(starting: list[StartingSlot], snapshot: Snapshot) -> Decimal:
    return sum((snapshot.lineup_value(slot.player) for slot in starting if slot.player is not None), Decimal(0))
