"""
The adjusters of the trade analyzer rubric: roster fit, standing, trend and usage, injury, upside, handcuff, schedule,
and expected gap. It also holds what they read of one side: the best lineup before and after the trade, and the
handcuffs.
"""
from __future__ import annotations

from collections.abc import Callable
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from typing import TYPE_CHECKING, Literal, NamedTuple

from pydantic import BaseModel

from cornerstone.history import (
    SHARE_DIRECTION_WEEKS,
    air_yards_share,
    carry_share,
    player_points,
    red_zone,
    scored_weeks,
    stats_complete,
)
from cornerstone.models import ByePlayer
from cornerstone.names import last_name
from cornerstone.nflverse import SKILL_POSITIONS, TeamSchedule
from cornerstone.nflverse_expected import WINDOW_MIN_GAMES, window_gap
from cornerstone.numbers import round_half_up
from cornerstone.ranks import (
    OUT_STATUSES,
    POSITION_ORDER,
    RANKED_POSITIONS,
    _back_in_a_known_game,
    _played_weeks,
    due_back_week,
    lineup_value,
    projection_ahead,
)
from cornerstone.snapshot import Snapshot
from cornerstone.tunables import (
    EXPECTED_ADJUSTER_ON,
    EXPECTED_GAP,
    FIT_THRESHOLD,
    HANDCUFF_CARRY_SHARE,
    INJURY_WEEKS,
    RETURN_WINDOW_WEEKS,
    SCHEDULE_RANK_GAP,
    SELLER_GAP,
    SHARE_WEEKS,
    WOPR_SWING,
)

if TYPE_CHECKING:
    # The rubric module imports this one, so the trade model is a name for the type checker only.
    from cornerstone.rubric import ProposedTrade

# The adjusters run in this order: roster fit, standing, trend and usage, injury, upside, handcuff, schedule, and
# expected gap when its tunable is on.


Lean = Literal["for", "against", "even"]


class Adjuster(BaseModel):
    """One criterion of the rubric for one side: its name, its step of at most one, and a one-line reason."""

    name: str
    step: Literal[-1, 0, 1]
    reason: str
    # Only the schedule adjuster has a lean. It never moves a letter, so its step is always 0.
    lean: Lean | None = None


# The analyze output and the analysis prompt name an adjuster's step in words.
STEP_WORDS = {1: "one step up", 0: "no step", -1: "one step down"}


def _join(names: list[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def named(snapshot: Snapshot, players: list[str], one: str, many: str) -> str:
    """The joined names of the players, then the phrase `one` for one player or the phrase `many` for more."""
    names = _join([snapshot.players[pid].name for pid in players])
    return f"{names} {one if len(players) == 1 else many}"


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
    # True when a middle team gets the player and he has his bye in the trade week. No cover cancels it.
    bye_now: bool = False

    def is_hole(self, snapshot: Snapshot) -> bool:
        """True when the slot is a hole. GLOSSARY.md, "Hole".

        A hole holds no player or a player below the line for his own position. A starter due back after the trade
        week with no cover is a hole too. A K or DEF slot is never a hole. A player at a ranked position with
        no rank is below the line, because he has no stat line to start on. A starter a middle team gets, who has his
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


def _last_window_week(snapshot: Snapshot) -> int:
    """The last week of the return window, which starts at the trade week."""
    return snapshot.week + RETURN_WINDOW_WEEKS


def _above_the_line(snapshot: Snapshot, player_id: str) -> bool:
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
        if slot.player is None or not _above_the_line(snapshot, slot.player):
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
             and _above_the_line(snapshot, pid)
             and not _out_now(snapshot, pid)), None)
        if cover is not None:
            free.remove(cover)
        marked.append(slot._replace(absence=Absence(week=week, covered=cover is not None)))
    return marked


def _lineup_total(starting: list[StartingSlot], snapshot: Snapshot) -> Decimal:
    return sum((snapshot.lineup_value(slot.player) for slot in starting if slot.player is not None), Decimal(0))


class Side(BaseModel):
    """What the adjusters read of one side: the players it gets and gives, and its lineup before and after."""

    roster_id: int
    gets: list[str]
    gives: list[str]
    starters_after: list[str]
    # The starting slots of the best lineup before and after the trade, each with its player and his position rank.
    slots_before: list[StartingSlot] = []
    slots_after: list[StartingSlot] = []
    # The best lineup's total after the trade minus the total before.
    lineup_change: Decimal
    # True when the side gets the single highest-value player in the trade.
    gets_highest_value: bool
    # True when the side gives that player.
    gives_highest_value: bool
    # Every handcuff in the trade, whichever side gets him.
    handcuffs: list[str] = []

    @property
    def gets_handcuffs(self) -> list[str]:
        return [pid for pid in self.gets if pid in self.handcuffs]

    @property
    def lineup_gains(self) -> bool:
        return self.lineup_change >= FIT_THRESHOLD

    @property
    def lineup_loses(self) -> bool:
        return -self.lineup_change >= FIT_THRESHOLD

    def new_holes(self, snapshot: Snapshot) -> list[StartingSlot]:
        """The holes after the trade in a slot that was no hole before it. GLOSSARY.md, "Hole".

        A hole both before and after is the side's roster, not the trade, so it is not new. The match is by roster
        slot, such as RB or FLEX, and not by slot name: a better flex player can push a hole from FLEX1 to FLEX2, and
        that hole is still the same one. Only the holes past the count before are new. A slot whose player was no
        hole before is named first, because his slot is the one the trade emptied.
        """
        before = [slot for slot in self.slots_before if slot.is_hole(snapshot)]
        after = [slot for slot in self.slots_after if slot.is_hole(snapshot)]
        new: list[StartingSlot] = []
        for kind in dict.fromkeys(slot.roster_slot for slot in after):
            holes_before = [slot for slot in before if slot.roster_slot == kind]
            holes_after = [slot for slot in after if slot.roster_slot == kind]
            players_before = {slot.player for slot in holes_before}
            emptied_first = ([slot for slot in holes_after if slot.player not in players_before]
                             + [slot for slot in holes_after if slot.player in players_before])
            new += emptied_first[:max(0, len(holes_after) - len(holes_before))]
        return [slot for slot in after if slot in new]

    def depth(self, snapshot: Snapshot, position: str) -> tuple[int, int]:
        """The depth at a position before and after the trade. GLOSSARY.md, "Depth".

        Depth counts every player at the position, starters and bench, at or above the line. It is a fact for the
        analysis, never a step, so a bench player above the line counts the same as a starter.
        """
        def count(roster: list[str]) -> int:
            return sum(1 for pid in roster
                       if snapshot.players[pid].position == position and _above_the_line(snapshot, pid))
        return (count(snapshot.rosters[self.roster_id]),
                count(_roster_after(snapshot, self.roster_id, self.gives, self.gets)))

    def strength(self, snapshot: Snapshot) -> tuple[int, int]:
        """The count of RB1, RB2, WR1, and WR2 starters at or better than the strength rank, before and after the trade.

        GLOSSARY.md, "Strength". It is a fact for the analysis, never a step. A starter outside the top 24 but above
        the line is weak, not a hole.
        """
        def count(slots: list[StartingSlot]) -> int:
            return sum(1 for slot in slots
                       if slot.name in STRENGTH_SLOTS and slot.rank is not None
                       and slot.rank <= snapshot.client.settings.strength_rank)
        return count(self.slots_before), count(self.slots_after)


def _roster_after(snapshot: Snapshot, roster_id: int, gives: list[str], gets: list[str]) -> list[str]:
    return [pid for pid in snapshot.rosters[roster_id] if pid not in gives] + gets


def _with_byes_now(snapshot: Snapshot, roster_id: int, gets: list[str],
                   slots: list[StartingSlot]) -> list[StartingSlot]:
    """The slots after the trade, with bye_now set on each starter a middle team gets who has his bye in the trade week.

    ADR 0004. A contender or a seller reads no hole for a bye, and with no schedule map no bye reads.
    """
    if snapshot.schedules is None or team_race(snapshot, roster_id) != "middle":
        return slots
    return [slot._replace(bye_now=True) if slot.player in gets and _bye_week(snapshot, slot.player) == snapshot.week
            else slot for slot in slots]


def _bye_week(snapshot: Snapshot, player_id: str) -> int | None:
    """The bye week of the player's NFL team. None for a defense, a kicker, or a team with no schedule."""
    schedule = _scheduled(snapshot, player_id)
    return None if schedule is None else schedule.bye_week


def _read_before(snapshot: Snapshot, roster: list[str]) -> tuple[list[StartingSlot], Decimal]:
    """The starting slots of the roster before the trade, and their lineup total."""
    before = lineup_slots(roster, snapshot)
    return before, _lineup_total(before, snapshot)


def build_side(snapshot: Snapshot, roster_id: int, gives: list[str], gets: list[str], top: str | None,
          handcuffs: list[str]) -> Side:
    # The read before the trade depends on the roster as it is now only, so it builds once per roster.
    before, total_before = snapshot.roster_read(roster_id, _read_before)
    after = _with_byes_now(snapshot, roster_id, gets,
                           lineup_slots(_roster_after(snapshot, roster_id, gives, gets), snapshot))
    return Side(
        roster_id=roster_id, gets=gets, gives=gives,
        starters_after=[slot.player for slot in after if slot.player is not None],
        slots_before=before, slots_after=after,
        lineup_change=_lineup_total(after, snapshot) - total_before,
        gets_highest_value=top in gets,
        gives_highest_value=top in gives,
        handcuffs=handcuffs,
    )


def _has_depth_chart(snapshot: Snapshot) -> bool:
    # The depth chart lists gsis_ids, so it needs the id map to reach the Sleeper rosters.
    return snapshot.depth_charts is not None and snapshot.id_map is not None


def _has_injury_report(snapshot: Snapshot) -> bool:
    # The injury report lists gsis_ids, so it needs the id map to reach the Sleeper rosters.
    return snapshot.injuries is not None and snapshot.id_map is not None


def _rb_chart(snapshot: Snapshot, team: str | None) -> list[str]:
    """The gsis_ids on the NFL team's RB depth chart, first to last. A team with no chart has an empty list."""
    return snapshot.depth_charts.get(team or "", {}).get("RB", [])


def _not_in_id_map(snapshot: Snapshot, players: list[str]) -> list[str]:
    """The players with no entry in the id map, so no gsis_id joins them to the slow sources."""
    return [pid for pid in players if pid not in snapshot.id_map]


def trade_handcuffs(trade: ProposedTrade, snapshot: Snapshot) -> list[str]:
    """The running backs in the trade who back up a starter on the roster that gets them.

    A handcuff is second or lower on his NFL team's RB depth chart, and the first on that chart is on the
    getting roster after the trade. A backup who takes HANDCUFF_CARRY_SHARE percent or more of his team's
    carries is no handcuff. With no depth chart, no player is a handcuff.
    """
    if not _has_depth_chart(snapshot):
        return []
    # Each given player names the roster that gets him, so the test reads that roster after the trade.
    after = {side.roster_id: _roster_after(snapshot, side.roster_id, side.player_ids, trade.gets(side.roster_id))
             for side in trade.sides}
    return [player.player_id for side in trade.sides for player in side.gives
            if _backs_up_a_starter(snapshot, player.player_id, after[player.to])]


def is_handcuff(snapshot: Snapshot, player_id: str, roster_id: int) -> bool:
    """True when the player backs up a starting running back on the roster as it is now, so he is a handcuff there."""
    return _backs_up_a_starter(snapshot, player_id, snapshot.rosters[roster_id])


def _backs_up_a_starter(snapshot: Snapshot, player_id: str, roster: list[str]) -> bool:
    """The one handcuff test: the player is behind a starter on the roster, and he takes few of the carries."""
    return _behind_a_starter(snapshot, player_id, roster) and not _carries_the_ball(snapshot, player_id)


def _carry_share(snapshot: Snapshot, player_id: str) -> float | None:
    """The exact percent of his team's carries that the player took, through the player stat bound."""
    return carry_share(snapshot.stats, player_id, snapshot.as_of.stats_through)


def _carries_the_ball(snapshot: Snapshot, player_id: str) -> bool:
    """True when the player takes enough of his team's carries to score points of his own.

    With no share to read, this is False, so the depth chart answer stands.
    """
    share = _carry_share(snapshot, player_id)
    return share is not None and share >= HANDCUFF_CARRY_SHARE


def _behind_a_starter(snapshot: Snapshot, player_id: str, roster: list[str]) -> bool:
    """The depth chart part of the handcuff test.

    The player is second or lower on his RB depth chart, and the first is on the roster.
    """
    if not _has_depth_chart(snapshot):
        return False
    id_map = snapshot.id_map
    player = snapshot.players[player_id]
    chart = _rb_chart(snapshot, player.nfl_team)
    if player.position != "RB" or id_map.get(player_id) not in chart[1:]:
        return False
    return chart[0] in {id_map[pid] for pid in roster if pid in id_map}


# The name of each adjuster. The breakdown shows it, so each string lives here only.
ROSTER_FIT = "roster fit"
STANDING = "standing"
TREND = "trend and usage"
INJURY = "injury"
UPSIDE = "upside"
HANDCUFF = "handcuff"
SCHEDULE = "schedule"
EXPECTED = "expected gap"

# The schedule adjuster and roster fit both say this when the schedule map is None.
NO_SCHEDULES = "The schedule sources are not available."


def _fit(snapshot: Snapshot, side: Side) -> Adjuster:
    """Roster fit: the change in the side's best lineup, with a note for each player due back in the trade.

    The note gives the lineup value of a player due back, because his recent points do not show it.
    """
    adjuster = _fit_step(snapshot, side)
    # With no schedule map, no bye read runs, so the reason names the missing schedules next to the step.
    notes = ([NO_SCHEDULES] if snapshot.schedules is None else []) + _due_back_notes(snapshot, side)
    if not notes:
        return adjuster
    return adjuster.model_copy(update={"reason": " ".join([adjuster.reason, *notes])})


def _due_back_notes(snapshot: Snapshot, side: Side) -> list[str]:
    """One sentence per player due back in the trade with the projection he counts for, or one sentence that says
    the projections are not available.
    """
    due_back = [pid for pid in side.gets + side.gives if due_back_week(snapshot, pid) is not None]
    if not due_back:
        return []
    if snapshot.projections_ahead is None:
        return ["The projections ahead are not available, so " + named(
            snapshot, due_back, "counts for his recent points per game.", "count for their recent points per game.")]
    return [_due_back_note(snapshot, pid) for pid in due_back]


def _due_back_note(snapshot: Snapshot, player_id: str) -> str:
    """The sentence that names a player due back, the week he counts as back, and the projection he counts for.

    A player out with no returns row has no known return, so the sentence says he counts as back, not that he is due.
    """
    name, week = snapshot.players[player_id].name, due_back_week(snapshot, player_id)
    # The quantize keeps the Decimal exact. round_half_up goes through a float, which can print a long tail.
    ahead = projection_ahead(snapshot, player_id).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    if player_id not in snapshot.returns:
        return (f"{name} has no return week on file, so he counts as back in week {week} "
                f"for his projection ahead of {ahead} a game.")
    return f"{name} is due back in week {week}, so he counts for his projection ahead of {ahead} a game."


def hole_sentence(snapshot: Snapshot, slot: StartingSlot) -> str:
    """The sentence that names a new hole: the slot, the player, and his position rank.

    A rank that reads a week N game in progress ends with "game in progress", because it can still move.
    A player out with no returns row has no known return, so the sentence names no week, as _due_back_note does.
    """
    lead = f"{slot.name} is a hole after the trade:"
    if slot.player is None:
        return f"{lead} no player fills it."
    player = snapshot.players[slot.player]
    if slot.bye_now:
        return f"{lead} {player.name} has his bye in week {snapshot.week}, and a middle team needs the win."
    if slot.absence is not None and not slot.absence.covered:
        week = slot.absence.week
        if slot.player not in snapshot.returns:
            return f"{lead} {player.name} is out with no return week on file."
        if week > _last_window_week(snapshot):
            return f"{lead} {player.name} is due back in week {week}."
        return f"{lead} {player.name} is due back in week {week}, and no bench player covers him."
    if slot.rank is None:
        return f"{lead} {player.name} has no position rank."
    # A player due back ranks by his projection ahead, so his rank reads no game.
    weeks = [] if due_back_week(snapshot, slot.player) is not None else [
        past.week for past in _played_weeks(snapshot, slot.player)]
    label = IN_PROGRESS_LABEL if _reads_a_game_in_progress(snapshot, slot.player, weeks) else ""
    return f"{lead} {player.name} is {player.position}{slot.rank}{label}."


def _fit_step(snapshot: Snapshot, side: Side) -> Adjuster:
    """The roster fit step and its reason, from the new holes and the change in the side's best lineup."""
    # A new hole costs the side on Sunday, so it blocks every step up, and a handcuff never hides it.
    # A lineup gain or the highest-value player cancels the hole to no step, and the reason names both.
    # With no gain, the hole is one step down. With a lineup loss too, the hole is the reason.
    holes = " ".join(hole_sentence(snapshot, slot) for slot in side.new_holes(snapshot))
    if holes:
        if side.lineup_gains:
            return Adjuster(name=ROSTER_FIT, step=0, reason=f"The best lineup gains after the trade. {holes}")
        if side.gets_highest_value and not side.lineup_loses:
            return Adjuster(name=ROSTER_FIT, step=0,
                            reason="It gets the highest-value player in the trade, and the best lineup does not "
                                   f"lose. {holes}")
        return Adjuster(name=ROSTER_FIT, step=-1, reason=holes)
    if side.lineup_loses:
        # A handcuff is insurance that sits on the bench, so a lineup loss in a trade for him does not count.
        if side.gets_handcuffs:
            handcuffs = named(snapshot, side.gets_handcuffs, "is a handcuff", "are handcuffs")
            return Adjuster(name=ROSTER_FIT, step=0,
                            reason=f"The best lineup loses after the trade, but {handcuffs}, "
                                   "so the loss does not count.")
        return Adjuster(name=ROSTER_FIT, step=-1, reason="The best lineup loses after the trade.")
    # In a one-for-two-or-more trade, the side that gets the depth must start every player it gets.
    # Otherwise it pays for a bench player, so neither the gain nor the highest-value player earns the step up.
    gets_depth = len(side.gets) > 1 and len(side.gives) == 1
    if gets_depth and not all(pid in side.starters_after for pid in side.gets):
        if side.lineup_gains:
            return Adjuster(name=ROSTER_FIT, step=0,
                            reason="The best lineup gains after the trade, but not every player it gets starts.")
        return Adjuster(name=ROSTER_FIT, step=0, reason="Not every player it gets starts.")
    if side.lineup_gains:
        return Adjuster(name=ROSTER_FIT, step=1, reason="The best lineup gains after the trade.")
    # A lineup change smaller than the fit threshold is no lineup loss, so it does not block this step.
    if side.gets_highest_value:
        return Adjuster(name=ROSTER_FIT, step=1,
                        reason="It gets the highest-value player in the trade, and the best lineup does not lose.")
    return Adjuster(name=ROSTER_FIT, step=0, reason="The best lineup stays about the same.")


def team_race(snapshot: Snapshot, roster_id: int) -> Literal["contender", "seller", "middle"]:
    """Where the team stands by record. The standings rank by wins, then by points for."""
    standing = next(s for s in snapshot.standings if s.roster_id == roster_id)
    if standing.in_playoffs:
        return "contender"
    # games_from_cut is the team's wins minus the wins of the team in the last playoff spot.
    if -standing.games_from_cut > SELLER_GAP:
        return "seller"
    return "middle"


def back_inside(week: int | None, after: int, by: int) -> bool:
    """True when a return week falls after week `after` and by week `by`. No return week is never inside."""
    return week is not None and after < week <= by


def _return_bet(snapshot: Snapshot, player_id: str) -> bool:
    """True when the returns file has the player due back after the last completed week and by the return-by week.

    A player who played in the known games of his return week is back, so he is no return bet.
    """
    # A player out for the season is never a return bet, even with a stale returns row. ADR 0005.
    return (player_id not in snapshot.out_for_season
            and back_inside(snapshot.returns.get(player_id), snapshot.as_of.completed_through,
                            snapshot.client.settings.return_by_week)
            and not _back_in_a_known_game(snapshot, player_id))


def _late_return(snapshot: Snapshot, player_id: str) -> str | None:
    """Why the player is not back by the return-by week, or None when he is back by then or is not out."""
    if player_id in snapshot.out_for_season:
        return "is out for the season"
    week = snapshot.returns.get(player_id)
    if week is not None:
        return "is not due back before the playoffs" if week > snapshot.client.settings.return_by_week else None
    if snapshot.players[player_id].injury_status in OUT_STATUSES:
        return "has no return week on file"
    return None


def _credited_return_bets(snapshot: Snapshot, side: Side) -> list[str]:
    """The players the standing adjuster credits as a return bet: a contender with no lineup gain gets them.

    The injury adjuster reads this too, so a player the standing step counts in favor never counts against.
    """
    if team_race(snapshot, side.roster_id) != "contender" or side.lineup_gains:
        return []
    return [pid for pid in side.gets if _return_bet(snapshot, pid)]


def _gain_when(snapshot: Snapshot, side: Side) -> str:
    """The function gives the time of the side's lineup gain.

    The text is "now" when the side gets no starter who is due back.
    A player due back does not play this week, so a gain he makes in the lineup comes after his return, not now.
    The text names each player due back that the side gets and starts. It gives the latest return week of them.
    A player out with no returns row has no known return, so the text says he counts as back, as the fit note does.
    """
    due_back = [pid for pid in side.gets if pid in side.starters_after and due_back_week(snapshot, pid) is not None]
    if not due_back:
        return "now"
    week = max(due_back_week(snapshot, pid) for pid in due_back)
    if any(pid not in snapshot.returns for pid in due_back):
        return f"from week {week}, when " + named(snapshot, due_back, "counts as back", "count as back")
    returns = named(snapshot, due_back, "returns", "return")
    return f"after {returns} in week {week}"


def _standing(snapshot: Snapshot, side: Side) -> Adjuster:
    """Standing: a contender's win-now move or return bet, and a seller's bet on the future."""
    race = team_race(snapshot, side.roster_id)
    if race == "contender":
        lead = "The team holds a playoff spot"
        if side.lineup_gains:
            return Adjuster(name=STANDING, step=1,
                            reason=f"{lead}, and the best lineup gains {_gain_when(snapshot, side)}.")
        bets = _credited_return_bets(snapshot, side)
        if bets:
            due = named(snapshot, bets, "is", "are")
            return Adjuster(name=STANDING, step=1, reason=f"{lead}, and {due} due back before the playoffs.")
        late = [(pid, why) for pid in side.gets if (why := _late_return(snapshot, pid)) is not None]
        if side.lineup_loses and late:
            pid, why = late[0]
            return Adjuster(name=STANDING, step=-1,
                            reason=f"{lead}, but the best lineup loses now for {snapshot.players[pid].name}, "
                                   f"who {why}.")
        return Adjuster(name=STANDING, step=0, reason=f"{lead}, and the trade is no win-now move or return bet.")
    if race == "seller":
        lead = "The team is out of the playoff race"
        if side.gets_highest_value:
            return Adjuster(name=STANDING, step=1,
                            reason=f"{lead}, and it gets the highest-value player in the trade.")
        if side.gives_highest_value and side.lineup_gains:
            return Adjuster(name=STANDING, step=-1,
                            reason=f"{lead}, but it gives the highest-value player in the trade for a lineup gain now.")
        return Adjuster(name=STANDING, step=0, reason=f"{lead}, and the trade is no bet on the future.")
    return Adjuster(name=STANDING, step=0, reason="The team is neither in a playoff spot nor out of the race.")


class _WoprWindow(NamedTuple):
    """The mean WOPR of a player over the last SHARE_WEEKS weeks, and its direction against the weeks before."""
    value: int
    direction: Literal["up", "down", "flat"]
    weeks_used: list[int]


def _wopr(snapshot: Snapshot, player_id: str) -> _WoprWindow | None:
    """The WOPR window of a WR or TE over his last SHARE_DIRECTION_WEEKS played weeks.

    WOPR measures receiver volume, so only a WR or TE has one that counts.
    The file can lack a row for one week, so a window with a week that has no WOPR is None.
    A known game with no row yet is pending, so the window ends at the weeks before it.
    A stats outage leaves a week out of the played weeks, so a window that skips it is None too.
    """
    if snapshot.wopr is None or snapshot.players[player_id].position not in ("WR", "TE"):
        return None
    if not stats_complete(snapshot.stats, snapshot.as_of.stats_through):
        return None
    by_week = snapshot.wopr.get(player_id, {})
    weeks = [week for week in scored_weeks(snapshot.stats, player_id, snapshot.as_of.stats_through)
             if week <= snapshot.as_of.completed_through or week in by_week][-SHARE_DIRECTION_WEEKS:]
    if len(weeks) < SHARE_DIRECTION_WEEKS or any(week not in by_week for week in weeks):
        return None
    recent = sum(by_week[week] for week in weeks[-SHARE_WEEKS:]) / SHARE_WEEKS
    prior = sum(by_week[week] for week in weeks[:-SHARE_WEEKS]) / (SHARE_DIRECTION_WEEKS - SHARE_WEEKS)
    direction = "up" if recent - prior >= WOPR_SWING else "down" if prior - recent >= WOPR_SWING else "flat"
    return _WoprWindow(value=int(round_half_up(recent)), direction=direction, weeks_used=weeks[-SHARE_WEEKS:])


def _directions(snapshot: Snapshot, players: list[str]) -> set[str]:
    """The set of share directions, up or down, of the players.
    A flat share or a player with no usage data adds none."""
    shares = [share for pid in players for share in snapshot.usage_shares(pid)]
    return {share.direction for share in shares if share is not None and share.direction in ("up", "down")}


def _short_names(snapshot: Snapshot, players: list[str]) -> dict[str, str]:
    """The last name of each player, or the full name when the last name is short or not alphabetic, or when two
    players share it.
    """
    full = {pid: snapshot.players[pid].name for pid in players}
    last = {pid: last_name(name) for pid, name in full.items()}
    shared = {name for name in last.values() if list(last.values()).count(name) > 1}
    return {pid: last[pid] if last[pid] is not None and last[pid] not in shared else full[pid] for pid in players}


def _weeks_text(weeks: list[int]) -> str:
    """The weeks as a list, such as "weeks 4 and 5", so a bye between them never reads as a third week."""
    return "week " + str(weeks[0]) if len(weeks) == 1 else "weeks " + _join([str(week) for week in weeks])


# The phrase that ends the sentence of a player whose quoted number reads a week N game in progress.
IN_PROGRESS_LABEL = ", game in progress"


def _share_sentences(snapshot: Snapshot, players: list[str]) -> list[str]:
    """One sentence per player with a snap or target share that moved: the percent and direction of each moved share.

    The reader cannot check a bare direction, so each sentence gives the numbers and the weeks behind each percent.
    When the two moved shares of a player have the same weeks, the weeks come once at the end of his sentence.
    When they differ, the weeks come after each percent.
    A share that reads a week N game in progress ends the sentence with "game in progress", because it can still move.
    """
    names = _short_names(snapshot, players)
    sentences = []
    for pid in players:
        moved = [(kind, share) for kind, share in zip(("snap share", "target share"), snapshot.usage_shares(pid))
                 if share is not None and share.direction in ("up", "down")]
        if not moved:
            continue
        label = IN_PROGRESS_LABEL if _reads_a_game_in_progress(
            snapshot, pid, [week for _, share in moved for week in share.weeks_used]) else ""
        if len({tuple(share.weeks_used) for _, share in moved}) == 1:
            shares = ", ".join(f"{kind} {share.percent}%, {share.direction}" for kind, share in moved)
            sentences.append(f"{names[pid]}: {shares}, over {_weeks_text(moved[0][1].weeks_used)}{label}.")
        else:
            shares = ", ".join(f"{kind} {share.percent}% ({_weeks_text(share.weeks_used)}), {share.direction}"
                               for kind, share in moved)
            sentences.append(f"{names[pid]}: {shares}{label}.")
    return sentences


def _reads_a_game_in_progress(snapshot: Snapshot, player_id: str, weeks: list[int]) -> bool:
    """True when the weeks hold the trade week and the player's NFL team plays its week N game now.

    GLOSSARY.md, "In progress". A saved week has no game in progress, so it is always False there.
    The team on his week N stat row comes first, because a player can change teams after his game.
    """
    known = snapshot.stats.weeks.get(snapshot.week)
    team = (known.nfl_teams.get(player_id) if known is not None else None) or snapshot.players[player_id].nfl_team
    return snapshot.week in weeks and team in snapshot.in_progress_teams


def _red_zone_touches(snapshot: Snapshot, players: list[str]) -> int:
    """The red-zone targets and rushes of the players, summed over the season through the player stat bound."""
    through = snapshot.as_of.stats_through
    return sum(sum(red_zone(snapshot.stats, pid, through) or (0, 0)) for pid in players)


def _due_back(snapshot: Snapshot, player_id: str) -> bool:
    """True when the returns file has the player back after the last completed week, so he is out now."""
    # The trend and the expected gap read only the returns file, so an out player with no row keeps his use.
    # A known game shows his use again, so it ends the exemption, as it ends due back in due_back_week.
    week = snapshot.returns.get(player_id)
    return week is not None and week > snapshot.as_of.completed_through and not _back_in_a_known_game(
        snapshot, player_id)


def _left_out(snapshot: Snapshot, side: Side, what: str) -> tuple[set[str], list[str]]:
    """The handcuffs and the players due back in the trade, and a note for each group that says his `what` does not
    count. The trend and the expected gap both read this, so the two leave out the same players.
    """
    traded = side.gets + side.gives
    handcuffs = [pid for pid in traded if pid in side.handcuffs]
    due_back = [pid for pid in traded if pid not in side.handcuffs and _due_back(snapshot, pid)]
    notes = []
    if handcuffs:
        notes.append(named(snapshot, handcuffs, f"is a handcuff, so his {what} does not count.",
                            f"are handcuffs, so their {what} does not count."))
    if due_back:
        notes.append(named(snapshot, due_back, f"is due back, so his {what} does not count.",
                            f"are due back, so their {what} does not count."))
    return set(handcuffs + due_back), notes


def _trend(snapshot: Snapshot, side: Side) -> Adjuster:
    """Trend and usage: the snap and target share directions of the players it gets against the players it gives.

    When every share is flat, the WOPR direction of a WR or TE breaks the tie first, and red-zone use breaks it next.
    A handcuff's use does not count on either side, so the trend never steps a side down because of him.
    A player due back has no recent use to compare, so his use does not count on either side either.
    """
    left_out, notes = _left_out(snapshot, side, "use")
    adjuster = _trend_step(snapshot, [pid for pid in side.gets if pid not in left_out],
                           [pid for pid in side.gives if pid not in left_out])
    if not notes:
        return adjuster
    return adjuster.model_copy(update={"reason": " ".join([adjuster.reason, *notes])})


def _wopr_step(snapshot: Snapshot, gets: list[str], gives: list[str]) -> Adjuster | None:
    """The trend when every share is flat and the WOPR of the WR and TE points one way.

    None when no WOPR moved or when it points both ways.
    """
    woprs = {pid: wopr for pid in gets + gives
             if (wopr := _wopr(snapshot, pid)) is not None and wopr.direction in ("up", "down")}
    if not woprs:
        return None
    got = {woprs[pid].direction for pid in gets if pid in woprs}
    gave = {woprs[pid].direction for pid in gives if pid in woprs}
    lead = "The snap and target shares are flat."
    if got <= {"up"} and gave <= {"down"}:
        step, lead = 1, f"{lead} The players it gets gain WOPR, and the players it gives lose it."
    elif got <= {"down"} and gave <= {"up"}:
        step, lead = -1, f"{lead} The players it gets lose WOPR, and the players it gives gain it."
    else:
        # WOPR only breaks a tie, so a WOPR that points both ways leaves the tie to red-zone use.
        return None
    names = _short_names(snapshot, gets + gives)
    sentences = [f"{names[pid]}: WOPR {wopr.value}, {wopr.direction}, over {_weeks_text(wopr.weeks_used)}."
                 for pid, wopr in woprs.items()]
    return Adjuster(name=TREND, step=step, reason=" ".join([lead, *sentences]))


def _trend_step(snapshot: Snapshot, gets: list[str], gives: list[str]) -> Adjuster:
    got, gave = _directions(snapshot, gets), _directions(snapshot, gives)
    if not got and not gave:
        # Every share is flat, so the WOPR of a WR or TE decides, and then red-zone use.
        wopr = _wopr_step(snapshot, gets, gives)
        if wopr is not None:
            return wopr
        got_rz, gave_rz = _red_zone_touches(snapshot, gets), _red_zone_touches(snapshot, gives)
        lead = "The snap and target shares are flat"
        if got_rz > gave_rz:
            return Adjuster(name=TREND, step=1, reason=f"{lead}, and the players it gets have more red-zone use.")
        if got_rz < gave_rz:
            return Adjuster(name=TREND, step=-1, reason=f"{lead}, and the players it gives have more red-zone use.")
        return Adjuster(name=TREND, step=0, reason=f"{lead}, and the red-zone use is even.")
    # A player with one share up and one share down puts both in his side's set, so his trade is mixed.
    if got <= {"up"} and gave <= {"down"}:
        step, lead = 1, "The players it gets gain snap or target share, and the players it gives lose it."
    elif got <= {"down"} and gave <= {"up"}:
        step, lead = -1, "The players it gets lose snap or target share, and the players it gives gain it."
    else:
        step, lead = 0, "The snap and target shares point both ways."
    return Adjuster(name=TREND, step=step, reason=" ".join([lead, *_share_sentences(snapshot, gets + gives)]))


def _out_with_no_near_return(snapshot: Snapshot, player_id: str) -> bool:
    """True when the player is out now with no return week on file, or with one later than the trade week
    plus RETURN_WINDOW_WEEKS. A player out for the season is out with no near return, whatever his Sleeper status.
    """
    if player_id in snapshot.out_for_season:
        return True
    if snapshot.players[player_id].injury_status not in OUT_STATUSES:
        return False
    week = snapshot.returns.get(player_id)
    # The PRD's "now" is the trade week N, so the window counts from N, not from the last completed week.
    return week is None or week > snapshot.week + RETURN_WINDOW_WEEKS


def _report_weeks(snapshot: Snapshot, player_id: str) -> int | None:
    """The count of weeks through the last completed week with the player on the injury report.

    None when the injury report or the id map is not in the snapshot, or the id map has no entry for the player.
    """
    if not _has_injury_report(snapshot) or player_id not in snapshot.id_map:
        return None
    weeks = snapshot.injuries.get(snapshot.id_map[player_id], {})
    # GLOSSARY.md, "Before the trade": the injury report ends at N-1, the last completed week.
    # So a report for the trade week itself does not count.
    return sum(1 for week in weeks if week <= snapshot.as_of.completed_through)


def _injury(snapshot: Snapshot, side: Side) -> Adjuster:
    """Injury: a player it gets who is out for the season, out with no near return, or on the report in many weeks."""
    # A star return bet is the upside's credit, so the injury never counts him against the same side. ADR 0005.
    exempt = set(_credited_return_bets(snapshot, side)) | {pid for pid in side.gets if _star_return_bet(snapshot, pid)}
    for pid in side.gets:
        if pid in exempt:
            continue
        name = snapshot.players[pid].name
        # The season mark comes first, so the reason names the plain cause and not the weaker "no near return".
        if pid in snapshot.out_for_season:
            return Adjuster(name=INJURY, step=-1, reason=f"{name} is out for the season.")
        if _out_with_no_near_return(snapshot, pid):
            return Adjuster(name=INJURY, step=-1, reason=f"{name} is out with no near return.")
        if (_report_weeks(snapshot, pid) or 0) >= INJURY_WEEKS:
            return Adjuster(name=INJURY, step=-1, reason=f"{name} was on the injury report in many weeks this season.")
    reason = "No player it gets is out for long or often on the injury report."
    if not _has_injury_report(snapshot):
        reason += " The injury report is not available, so no count of report weeks ran."
    elif unmapped := _not_in_id_map(snapshot, side.gets):
        reason += " " + named(snapshot, unmapped, "is not in the id map, so no report count ran for him.",
                               "are not in the id map, so no report count ran for them.")
    return Adjuster(name=INJURY, step=0, reason=reason)


def _star(snapshot: Snapshot, player_id: str) -> bool:
    """True when the player's chart value is in the top of his position on the league's chart. GLOSSARY.md, "Star".

    The rank is over every player at his position on the chart, not the roster. The star ranks of the client set the
    count per position, and a position not in it has no stars. A tie shares the better rank, so a tie at the edge makes
    every tied player a star. With no chart, or with the player not on it, he is no star.
    """
    if snapshot.chart is None or player_id not in snapshot.chart.values:
        return False
    position = snapshot.players[player_id].position
    star_ranks = snapshot.client.settings.star_rank_by_position
    if position not in star_ranks:
        return False
    value = snapshot.chart.values[player_id]
    above = sum(1 for pid, other in snapshot.chart.values.items()
                if other > value and pid in snapshot.players and snapshot.players[pid].position == position)
    return 1 + above <= star_ranks[position]


def _star_return_bet(snapshot: Snapshot, player_id: str) -> bool:
    """True when the player is a star who is out now and is not out for the season. GLOSSARY.md, "Star return bet".

    A missing return week does not matter: a star with no week on file is still a bet on his return.
    """
    return (player_id not in snapshot.out_for_season
            and snapshot.players[player_id].injury_status in OUT_STATUSES
            and _star(snapshot, player_id))


def _rising_signal(snapshot: Snapshot, player_id: str) -> str | None:
    """The first of the player's use signals that points up, by name, or None when none does.

    The signals are the snap share, target share, and air yards share directions, and the WOPR direction.
    A QB plays nearly every snap, so his snap share says nothing about a role and he reads none.
    """
    snap, target = snapshot.usage_shares(player_id)
    air = air_yards_share(snapshot.stats, player_id, snapshot.as_of.stats_through)
    wopr = _wopr(snapshot, player_id)
    signals = [("target share", target), ("air yards share", air), ("WOPR", wopr)]
    if snapshot.players[player_id].position != "QB":
        signals.insert(0, ("snap share", snap))
    return next((name for name, signal in signals if signal is not None and signal.direction == "up"), None)


def _opportunity_from(snapshot: Snapshot, player_id: str) -> str | None:
    """The same-position teammate on his NFL team who is out for the season or out with no near return, or None."""
    player = snapshot.players[player_id]
    if player.nfl_team is None:
        return None
    return next((pid for pid, other in snapshot.players.items()
                 if pid != player_id and other.nfl_team == player.nfl_team and other.position == player.position
                 and _out_with_no_near_return(snapshot, pid)), None)


def _upside(snapshot: Snapshot, side: Side) -> Adjuster:
    """Upside: a player it gets who is a star return bet or who has an opportunity. GLOSSARY.md, "Upside".

    It steps up or not at all, never down, and it reads the players the side gets only. A player out for the season
    is never a star return bet and never an opportunity, because he buys the side nothing. ADR 0005.
    """
    for pid in side.gets:
        if pid in snapshot.out_for_season:
            continue
        name = snapshot.players[pid].name
        if _star_return_bet(snapshot, pid):
            return Adjuster(name=UPSIDE, step=1, reason=f"{name} is a star out now with a return in play.")
        teammate = _opportunity_from(snapshot, pid)
        if teammate is None:
            continue
        signal = _rising_signal(snapshot, pid)
        if signal is not None:
            # _out_with_no_near_return holds the season mark too, so the reason names the plainer cause first.
            out = ("out for the season" if teammate in snapshot.out_for_season else "out with no near return")
            return Adjuster(name=UPSIDE, step=1,
                            reason=f"{name} gains {signal} with {snapshot.players[teammate].name} {out}.")
    return Adjuster(name=UPSIDE, step=0, reason="No player it gets is a star out now or has an opportunity.")


def _handcuff(snapshot: Snapshot, side: Side) -> Adjuster:
    """Handcuff: a backup to the roster's own starting running back is insurance.

    It never moves the letter itself. A handcuff counts as zero in the sums, and the fit and trend
    adjusters cannot step down because of him. A backup with a real share of the carries is no handcuff,
    and the reason names his share.
    """
    if snapshot.depth_charts is None:
        return Adjuster(name=HANDCUFF, step=0, reason="The depth chart is not available, so no handcuff check ran.")
    if snapshot.id_map is None:
        return Adjuster(name=HANDCUFF, step=0, reason="The id map is not available, so no handcuff check ran.")
    parts = []
    if side.gets_handcuffs:
        parts.append(named(snapshot, side.gets_handcuffs, "backs up the team's own starter, so he counts as insurance.",
                           "back up the team's own starters, so they count as insurance."))
    after = _roster_after(snapshot, side.roster_id, side.gives, side.gets)
    freed = [pid for pid in side.gets if pid not in side.handcuffs and _behind_a_starter(snapshot, pid, after)]
    # The gate compares the exact share. The reason shows it rounded, as every other percent in a reason.
    parts.extend(f"{snapshot.players[pid].name} backs up the team's own starter but takes "
                 f"{int(round_half_up(_carry_share(snapshot, pid)))}% of the carries, so he counts as a running back."
                 for pid in freed)
    reason = " ".join(parts) if parts else "No player it gets is a handcuff."
    # Only a running back can be a handcuff, so only a running back with no gsis_id misses a check.
    unmapped = _not_in_id_map(snapshot, [pid for pid in side.gets if snapshot.players[pid].position == "RB"])
    if unmapped:
        reason += " " + named(snapshot, unmapped, "is not in the id map, so no handcuff check ran for him.",
                               "are not in the id map, so no handcuff check ran for them.")
    return Adjuster(name=HANDCUFF, step=0, reason=reason)


def _scheduled(snapshot: Snapshot, player_id: str) -> TeamSchedule | None:
    """The NFL schedule of the player's team. None for a defense, a kicker, or a player whose team has no schedule.

    A defense or a kicker has no points allowed rank to his position, so the schedule leaves him out on both signals.
    """
    player = snapshot.players[player_id]
    if player.position in ("DEF", "K"):
        return None
    return snapshot.schedules.get(player.nfl_team or "")


def _byes_left(snapshot: Snapshot, players: list[str]) -> int:
    """The count of players whose NFL team still has its bye in the trade week or later."""
    return sum(1 for pid in players
               if (schedule := _scheduled(snapshot, pid)) is not None
               and schedule.bye_week is not None and schedule.bye_week >= snapshot.week)


def _playoff_rank(snapshot: Snapshot, players: list[str]) -> Fraction | None:
    """The mean over the players of the mean rank of each one's week 15 to 17 opponents in points allowed to his
    position.

    Rank 1 allows the most points, so a low mean is a soft schedule. A player with no schedule, no opponent with a
    points allowed row, or a position with no rank counts on neither side. None when no player counts.
    """
    means = []
    for pid in players:
        schedule = _scheduled(snapshot, pid)
        if schedule is None:
            continue
        position = snapshot.players[pid].position
        ranks = [snapshot.points_allowed[opponent][position].rank
                 for opponent in schedule.playoff_opponents.values()
                 if position in snapshot.points_allowed.get(opponent, {})]
        if ranks:
            # Fractions keep the means exact, so a gap right at SCHEDULE_RANK_GAP counts.
            means.append(Fraction(sum(ranks), len(ranks)))
    return sum(means, Fraction(0)) / len(means) if means else None


def _schedule(snapshot: Snapshot, side: Side) -> Adjuster:
    """Schedule: the byes left and the playoff opponents of the players it gets against the players it gives.

    It shows a lean for, against, or even, and never moves the letter.
    """
    if snapshot.schedules is None or snapshot.points_allowed is None:
        return Adjuster(name=SCHEDULE, step=0, lean="even", reason=NO_SCHEDULES)
    byes_got, byes_gave = _byes_left(snapshot, side.gets), _byes_left(snapshot, side.gives)
    bye_lean: Lean = "for" if byes_got < byes_gave else "against" if byes_got > byes_gave else "even"
    rank_got, rank_gave = _playoff_rank(snapshot, side.gets), _playoff_rank(snapshot, side.gives)
    if rank_got is None or rank_gave is None:
        playoff_lean = "even"
        playoffs = "the playoff opponents do not compare"
    elif rank_gave - rank_got >= SCHEDULE_RANK_GAP:
        playoff_lean = "for"
        playoffs = "the players it gets face softer playoff opponents at their positions"
    elif rank_got - rank_gave >= SCHEDULE_RANK_GAP:
        playoff_lean = "against"
        playoffs = "the players it gets face harder playoff opponents at their positions"
    else:
        playoff_lean = "even"
        playoffs = "the playoff opponents are about as hard on both sides"
    byes = {
        "for": "The players it gets have fewer byes left than the players it gives",
        "against": "The players it gets have more byes left than the players it gives",
        "even": "The players it gets and the players it gives have the same count of byes left",
    }[bye_lean]
    # Two signals that agree, or one signal with the other even, give the lean. Two that conflict cancel out.
    leans = {bye_lean, playoff_lean} - {"even"}
    lean: Lean = leans.pop() if len(leans) == 1 else "even"
    verdict = "The schedule is even." if lean == "even" else f"The schedule leans {lean} this side."
    return Adjuster(name=SCHEDULE, step=0, lean=lean, reason=f"{byes}, and {playoffs}. {verdict}")


def _league_points(snapshot: Snapshot, player_id: str) -> dict[int, float]:
    """The league points of the player in each week he played, as recent_points_per_game reads them."""
    # Sleeper leaves out a stat whose value is 0. A game with no points entry is a game of 0 points.
    return {week: player_points(past, player_id) or 0.0 for week, past in snapshot.stats.weeks.items()
            if (past.stats.get(player_id) or {}).get("gp", 0) > 0}


def _mean_gap(gaps: list[Decimal]) -> Decimal | None:
    return sum(gaps, Decimal(0)) / len(gaps) if gaps else None


def _expected_gap(snapshot: Snapshot, side: Side) -> Adjuster:
    """Expected gap: the players it gets against their expected points, and the players it gives against theirs.

    Points under expected tend to rise and points over expected tend to fall. So the side steps up when it buys low
    or sells high, and steps down when it buys high or sells low. A step up and a step down at once give no step.
    Handcuffs and players due back do not count, by the rule the trend reads.
    """
    if snapshot.expected is None:
        return Adjuster(name=EXPECTED, step=0, reason="The expected points are not available, so no gap check ran.")
    left_out, notes = _left_out(snapshot, side, "gap")
    gets = [pid for pid in side.gets if pid not in left_out]
    gives = [pid for pid in side.gives if pid not in left_out]
    gaps: dict[str, Decimal] = {}
    weeks: dict[str, list[int]] = {}
    for pid in gets + gives:
        games, points = snapshot.expected.players.get(pid, []), _league_points(snapshot, pid)
        gap = window_gap(games, points)
        if gap is not None:
            # window_gap rounds the gap to cents, so a Decimal of its text compares with EXPECTED_GAP exactly.
            gaps[pid], weeks[pid] = Decimal(str(gap)), [game.week for game in games if game.week in points]
    got = _mean_gap([gaps[pid] for pid in gets if pid in gaps])
    gave = _mean_gap([gaps[pid] for pid in gives if pid in gaps])
    under = "run under their expected points, so their points can rise."
    over = "run over their expected points, so their points can fall."
    # Each case is a step and its sentence: buy low and sell high step up, buy high and sell low step down.
    cases = []
    if got is not None and got <= -EXPECTED_GAP:
        cases.append((1, f"The players it gets {under}"))
    if got is not None and got >= EXPECTED_GAP:
        cases.append((-1, f"The players it gets {over}"))
    if gave is not None and gave >= EXPECTED_GAP:
        cases.append((1, f"The players it gives {over}"))
    if gave is not None and gave <= -EXPECTED_GAP:
        cases.append((-1, f"The players it gives {under}"))
    steps = {step for step, _ in cases}
    if steps == {1, -1}:
        step, lead = 0, " ".join([text for _, text in cases] + ["The step up and the step down cancel."])
    elif cases:
        step, lead = cases[0][0], " ".join(text for _, text in cases)
    elif gaps:
        step, lead = 0, "The players it gets and the players it gives run near their expected points."
    else:
        step, lead = 0, "No player in the trade has an expected gap."
    names = _short_names(snapshot, list(gaps))
    # The players it gets come before the players it gives, so the reader can tell the two groups apart.
    sentences = [f"{names[pid]}: {gaps[pid]:+.2f} points per game against expected, over {_weeks_text(weeks[pid])}."
                 for pid in gets + gives if pid in gaps]
    # A defense or a kicker has no expected points, so the reason names only a QB, RB, WR, or TE with no gap.
    no_gap = [pid for pid in gets + gives
              if pid not in gaps and snapshot.players[pid].position in SKILL_POSITIONS]
    if no_gap:
        sentences.append(named(
            snapshot, no_gap, f"has fewer than {WINDOW_MIN_GAMES} games in the expected window, so he has no gap.",
            f"have fewer than {WINDOW_MIN_GAMES} games in the expected window, so they have no gap."))
    return Adjuster(name=EXPECTED, step=step, reason=" ".join([lead, *sentences, *notes]))


def rubric_adjusters(expected_on: bool) -> tuple[Callable[[Snapshot, Side], Adjuster], ...]:
    """The adjusters in rubric order. The expected gap comes last, and only when `expected_on` is True."""
    return (_fit, _standing, _trend, _injury, _upside, _handcuff, _schedule) + ((_expected_gap,) if expected_on else ())


# The adjusters in rubric order. Each takes the snapshot and one side, and grade runs them in this order.
ADJUSTERS: tuple[Callable[[Snapshot, Side], Adjuster], ...] = rubric_adjusters(EXPECTED_ADJUSTER_ON)
