"""
The adjusters of the trade analyzer rubric: roster fit, standing, trend and usage, injury, handcuff, schedule, and
expected gap. It also holds what they read of one side: the best lineup before and after the trade, and the handcuffs.
"""
from __future__ import annotations

from collections.abc import Callable
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from typing import TYPE_CHECKING, Literal, NamedTuple

from pydantic import BaseModel

from cornerstone.history import (
    SHARE_DIRECTION_WEEKS, _round_half_up, carry_share, player_points, red_zone, scored_weeks, snap_share,
    stats_complete, target_share,
)
from cornerstone.names import last_name
from cornerstone.nflverse import SKILL_POSITIONS, TeamSchedule
from cornerstone.nflverse_expected import WINDOW_MIN_GAMES, window_gap
from cornerstone.models import PastWeek
from cornerstone.snapshot import Snapshot
from cornerstone.tunables import (
    BYE_WINDOW,
    EXPECTED_ADJUSTER_ON,
    EXPECTED_GAP,
    FIT_THRESHOLD,
    HANDCUFF_CARRY_SHARE,
    INJURY_WEEKS,
    LAST_REGULAR_WEEK,
    LINE_QB_TE,
    LINE_RB_WR,
    LINEUP_WEEKS,
    RETURN_BY_WEEK,
    RETURN_WINDOW_WEEKS,
    SCHEDULE_RANK_GAP,
    SELLER_GAP,
    SHARE_WEEKS,
    WOPR_SWING,
)

if TYPE_CHECKING:
    # The rubric module imports this one, so the trade model is a name for the type checker only.
    from cornerstone.rubric import ProposedTrade

# The adjusters run in this order: roster fit, standing, trend and usage, injury, handcuff, schedule, and expected gap
# when its tunable is on.


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


# The tie rule at equal points per game. A position not in the order ranks last.
POSITION_ORDER = ("RB", "WR", "TE", "QB", "K", "DEF")
# The positions each flex slot takes. Any other slot takes its own position only.
FLEX_SLOTS: dict[str, frozenset[str]] = {
    "FLEX": frozenset({"RB", "WR", "TE"}),
    "WRRB_FLEX": frozenset({"RB", "WR"}),
    "REC_FLEX": frozenset({"WR", "TE"}),
    "SUPER_FLEX": frozenset({"QB", "RB", "WR", "TE"}),
}
# Slots that hold players who do not start.
BENCH_SLOTS = frozenset({"BN", "IR", "TAXI"})


def recent_points_per_game(snapshot: Snapshot, player_id: str) -> Decimal:
    """The points per game over the last weeks through the player stat bound, LINEUP_WEEKS at most.

    The window ends at the known games for a player who played in week N, and at the last completed week otherwise.
    So a player's points per game move only when he plays. A player with no game in the window has 0.
    """
    played = _played_weeks(snapshot, player_id)
    if not played:
        return Decimal(0)
    # Sleeper leaves out a stat whose value is 0. A game with no points entry is a game of 0 points.
    total = sum((Decimal(str(player_points(past, player_id) or 0)) for past in played), Decimal(0))
    return total / len(played)


def _played_weeks(snapshot: Snapshot, player_id: str) -> list[PastWeek]:
    """The weeks the player played in the window of his recent points per game, LINEUP_WEEKS at most."""
    last = snapshot.as_of.stats_through
    if last > snapshot.as_of.completed_through and not _has_known_game(snapshot, player_id):
        last = snapshot.as_of.completed_through
    return [
        snapshot.stats.weeks[week] for week in range(max(1, last - LINEUP_WEEKS + 1), last + 1)
        if week in snapshot.stats.weeks
        and (snapshot.stats.weeks[week].stats.get(player_id) or {}).get("gp", 0) > 0
    ]


def projection_ahead(snapshot: Snapshot, player_id: str) -> Decimal:
    """The mean of the player's weekly projections from his due-back week through LAST_REGULAR_WEEK.

    A week with no projection row, such as a bye, is no game. With no row in those weeks, he counts for 0.
    """
    rows = snapshot.projections_ahead.get(player_id, {})
    weeks = [rows[week] for week in range(due_back_week(snapshot, player_id), LAST_REGULAR_WEEK + 1) if week in rows]
    if not weeks:
        return Decimal(0)
    return sum((Decimal(str(points)) for points in weeks), Decimal(0)) / len(weeks)


def lineup_value(snapshot: Snapshot, player_id: str) -> Decimal:
    """The points per game the player counts for in a best lineup.

    A player due back has no recent games, so his projection ahead gives his lineup value.
    Recent points show current play, so every other player keeps them. With no projections file, all players keep them.
    """
    if snapshot.projections_ahead is not None and due_back_week(snapshot, player_id) is not None:
        return projection_ahead(snapshot, player_id)
    return recent_points_per_game(snapshot, player_id)


# The positions with a position rank. K and DEF have none. GLOSSARY.md, "Position rank".
RANKED_POSITIONS = ("QB", "RB", "WR", "TE")


def rank_table(snapshot: Snapshot) -> dict[str, list[str]]:
    """The player ids at each of QB, RB, WR, and TE in position rank order, first to last.

    GLOSSARY.md, "Position rank". The index in the list plus one is the rank.

    The pool is every player with a stat line in the known games, rostered or not, plus every rostered player.
    A rostered player due back can have no stat line, and his projection ahead still gives him a lineup value.
    The order is lineup value, then the position order, then the player id. A player with no game in the window
    ranks last. His lineup value is 0, but so is the value of a player who scored 0, so the value alone cannot
    put him last. A due-back player ranks by his projection ahead, so he never counts as a player with no game.
    Snapshot.position_rank reads this table, so it builds once per snapshot. The finder grades about a thousand
    trades per call and must not rank the league per side.
    """
    # The known games end at the player stat bound, and a player is in the pool only with a stat line there.
    positions = {pid: past.positions[pid] for week, past in snapshot.stats.weeks.items()
                 if week <= snapshot.as_of.stats_through for pid in past.stats if pid in past.positions}
    # The players file is the source for a rostered player, as best_lineup reads it. A stat line gives the rest.
    positions.update({pid: player.position for pid, player in snapshot.players.items()})
    pool = [pid for pid, position in positions.items() if position in RANKED_POSITIONS]

    def due_back(pid: str) -> bool:
        return snapshot.projections_ahead is not None and due_back_week(snapshot, pid) is not None

    def order(pid: str) -> tuple[bool, Decimal, int, str]:
        no_game = not due_back(pid) and not _played_weeks(snapshot, pid)
        return (no_game, -lineup_value(snapshot, pid), POSITION_ORDER.index(positions[pid]), pid)

    return {position: sorted((pid for pid in pool if positions[pid] == position), key=order)
            for position in RANKED_POSITIONS}


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
        allowed = FLEX_SLOTS.get(slot, frozenset({slot}))
        taken = {pid for _, pid in filled}
        filled.append((slot, next((pid for pid in pool if pid not in taken and position(pid) in allowed), None)))
    return filled


# The line at each ranked position. GLOSSARY.md, "The line". K and DEF have no line, so their slots are never holes.
LINES = {"QB": LINE_QB_TE, "RB": LINE_RB_WR, "WR": LINE_RB_WR, "TE": LINE_QB_TE}


class Absence(NamedTuple):
    """A week that a starter misses: his bye or his return, the week, and whether a bench player covers him."""

    kind: Literal["bye", "due back"]
    week: int
    covered: bool


class StartingSlot(NamedTuple):
    """One starting slot of a best lineup: its name, such as "RB2", its player or None, and his position rank."""

    name: str
    player: str | None
    rank: int | None
    # The roster slot it fills, such as "RB" or "FLEX". A FLEX slot reads the line of its player's position.
    slot: str
    # His bye in the bye window, or his return after the trade week. None when he misses no week of the window.
    absence: Absence | None = None

    def is_hole(self, snapshot: Snapshot) -> bool:
        """True when the slot holds a player below the line for his own position, holds no player, or holds a
        player who misses a week of the bye window with no cover.

        GLOSSARY.md, "Hole". A K or DEF slot is never a hole. A player at a ranked position with no rank is below
        the line, because he has no stat line to start on.
        """
        if self.slot not in FLEX_SLOTS and self.slot not in LINES:
            return False
        if self.player is None:
            return True
        if self.absence is not None and not self.absence.covered:
            return True
        line = LINES.get(snapshot.players[self.player].position)
        return line is not None and (self.rank is None or self.rank > line)


def lineup_slots(roster: list[str], snapshot: Snapshot) -> list[StartingSlot]:
    """The starting slots of the roster's best lineup, each with its player and his position rank, in fill order.

    A slot that appears more than once gets a number, such as RB1 and RB2, so the reason can name it.
    RB1 holds the back with the most points per game, because the fixed slots fill in that order.
    """
    positions = {pid: snapshot.players[pid].position for pid in roster}
    filled = fill_slots(roster, snapshot.roster_positions, positions,
                        {pid: lineup_value(snapshot, pid) for pid in roster})
    counts = {slot: sum(1 for each, _ in filled if each == slot) for slot, _ in filled}
    seen: dict[str, int] = {}
    starting = []
    for slot, pid in filled:
        seen[slot] = seen.get(slot, 0) + 1
        name = f"{slot}{seen[slot]}" if counts[slot] > 1 else slot
        starting.append(StartingSlot(name=name, player=pid, rank=None if pid is None else snapshot.position_rank(pid),
                                     slot=slot))
    return _with_absences(starting, [pid for pid in roster if pid not in {slot.player for slot in starting}],
                          snapshot)


def _last_window_week(snapshot: Snapshot) -> int:
    """The last week of the bye window, which starts at the trade week."""
    return snapshot.week + BYE_WINDOW - 1


def _bye_in_window(snapshot: Snapshot, player_id: str) -> int | None:
    """The week of the player's bye when it falls in the bye window. None with no schedule map, as no bye reads."""
    if snapshot.schedules is None:
        return None
    schedule = _scheduled(snapshot, player_id)
    week = schedule.bye_week if schedule is not None else None
    return week if week is not None and snapshot.week <= week <= _last_window_week(snapshot) else None


def _above_the_line(snapshot: Snapshot, player_id: str) -> bool:
    """True when the player holds a position rank at or above the line of his position. K and DEF have no line."""
    line = LINES.get(snapshot.players[player_id].position)
    rank = snapshot.position_rank(player_id)
    return line is not None and rank is not None and rank <= line


def _out_now(snapshot: Snapshot, player_id: str) -> bool:
    """True when the player counts as back after the trade week, so he cannot play in place of a starter now.

    It reads due_back_week, so a player out with no return week counts as out too.
    """
    week = due_back_week(snapshot, player_id)
    return week is not None and week > snapshot.week


def _with_absences(starting: list[StartingSlot], bench: list[str], snapshot: Snapshot) -> list[StartingSlot]:
    """The starting slots with the week each starter above the line misses, and whether a bench player covers him.

    GLOSSARY.md, "Hole". A starter due back after the trade week and inside the window reads as a bye. A starter due
    back after the window is a hole whatever his rank, so no cover can fix it. A cover is a bench player at a
    position the slot allows, above the line, and not out after the trade week. A bench player whose own bye falls
    in the starter's bye week cannot cover him. Each bench player covers one slot only, and the covers go out in
    slot fill order, as the best lineup fills. The best bench player covers first.
    """
    free = sorted(bench, key=lambda pid: (-lineup_value(snapshot, pid), pid))
    marked = []
    for slot in starting:
        # A slot with no player or a player below the line is a hole already. K and DEF have no line, so never a hole.
        if slot.player is None or not _above_the_line(snapshot, slot.player):
            marked.append(slot)
            continue
        # The hole read takes the return week from the returns file only. GLOSSARY.md, "Due back".
        back = snapshot.returns.get(slot.player) if _due_back(snapshot, slot.player) else None
        if back is not None and back > snapshot.week:
            kind: Literal["bye", "due back"] = "due back"
            week: int | None = back
        else:
            kind, week = "bye", _bye_in_window(snapshot, slot.player)
        if week is None:
            marked.append(slot)
            continue
        allowed = FLEX_SLOTS.get(slot.slot, frozenset({slot.slot}))
        cover = None if week > _last_window_week(snapshot) else next(
            (pid for pid in free
             if snapshot.players[pid].position in allowed
             and _above_the_line(snapshot, pid)
             and not _out_now(snapshot, pid)
             and not (kind == "bye" and _bye_in_window(snapshot, pid) == week)), None)
        if cover is not None:
            free.remove(cover)
        marked.append(slot._replace(absence=Absence(kind=kind, week=week, covered=cover is not None)))
    return marked


def _lineup_total(starting: list[StartingSlot], snapshot: Snapshot) -> Decimal:
    return sum((lineup_value(snapshot, slot.player) for slot in starting if slot.player is not None), Decimal(0))


class _Side(BaseModel):
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
        for kind in dict.fromkeys(slot.slot for slot in after):
            was = [slot for slot in before if slot.slot == kind]
            now = [slot for slot in after if slot.slot == kind]
            held = {slot.player for slot in was}
            fresh = [slot for slot in now if slot.player not in held] + [slot for slot in now if slot.player in held]
            new += fresh[:max(0, len(now) - len(was))]
        return [slot for slot in after if slot in new]


def _roster_after(snapshot: Snapshot, roster_id: int, gives: list[str], gets: list[str]) -> list[str]:
    return [pid for pid in snapshot.rosters[roster_id] if pid not in gives] + gets


def build_side(snapshot: Snapshot, roster_id: int, gives: list[str], gets: list[str], top: str | None,
          handcuffs: list[str]) -> _Side:
    before = lineup_slots(snapshot.rosters[roster_id], snapshot)
    after = lineup_slots(_roster_after(snapshot, roster_id, gives, gets), snapshot)
    return _Side(
        roster_id=roster_id, gets=gets, gives=gives,
        starters_after=[slot.player for slot in after if slot.player is not None],
        slots_before=before, slots_after=after,
        lineup_change=_lineup_total(after, snapshot) - _lineup_total(before, snapshot),
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
    found = []
    for giver, getter in (trade.sides, trade.sides[::-1]):
        after = _roster_after(snapshot, getter.roster_id, getter.gives, giver.gives)
        found.extend(pid for pid in giver.gives if _backs_up_a_starter(snapshot, pid, after))
    return found


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
HANDCUFF = "handcuff"
SCHEDULE = "schedule"
EXPECTED = "expected gap"

# The schedule adjuster and roster fit both say this when the schedule map is None.
NO_SCHEDULES = "The schedule sources are not available."


def _fit(snapshot: Snapshot, side: _Side) -> Adjuster:
    """Roster fit: the change in the side's best lineup, with a note for each player due back in the trade.

    The note gives the lineup value of a player due back, because his recent points do not show it.
    """
    adjuster = _fit_step(snapshot, side)
    # With no schedule map, no bye hole reads, so the reason says so next to the step it qualifies.
    notes = ([NO_SCHEDULES] if snapshot.schedules is None else []) + _due_back_notes(snapshot, side)
    if not notes:
        return adjuster
    return adjuster.model_copy(update={"reason": " ".join([adjuster.reason, *notes])})


def _due_back_notes(snapshot: Snapshot, side: _Side) -> list[str]:
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
    # The quantize keeps the Decimal exact. _round_half_up goes through a float, which can print a long tail.
    ahead = projection_ahead(snapshot, player_id).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    if player_id not in snapshot.returns:
        return (f"{name} has no return week on file, so he counts as back in week {week} "
                f"for his projection ahead of {ahead} a game.")
    return f"{name} is due back in week {week}, so he counts for his projection ahead of {ahead} a game."


def _hole_sentence(snapshot: Snapshot, slot: StartingSlot) -> str:
    """The sentence that names a new hole: the slot, the player, and his position rank.

    A rank that reads a week N game in progress ends with "game in progress", because it can still move.
    """
    lead = f"{slot.name} is a hole after the trade:"
    if slot.player is None:
        return f"{lead} no player fills it."
    player = snapshot.players[slot.player]
    if slot.absence is not None and not slot.absence.covered:
        week = slot.absence.week
        if week > _last_window_week(snapshot):
            return f"{lead} {player.name} is due back in week {week}."
        if slot.absence.kind == "due back":
            return f"{lead} {player.name} is due back in week {week} and no cover."
        return f"{lead} {player.name} has his bye in week {week} and no cover."
    if slot.rank is None:
        return f"{lead} {player.name} has no position rank."
    # A player due back ranks by his projection ahead, so his rank reads no game.
    weeks = [] if due_back_week(snapshot, slot.player) is not None else [
        past.week for past in _played_weeks(snapshot, slot.player)]
    label = IN_PROGRESS_LABEL if _reads_a_game_in_progress(snapshot, slot.player, weeks) else ""
    return f"{lead} {player.name} is {player.position}{slot.rank}{label}."


def _fit_step(snapshot: Snapshot, side: _Side) -> Adjuster:
    """The roster fit step and its reason, from the new holes and the change in the side's best lineup."""
    # A new hole costs the side on Sunday, so it blocks every step up, and a handcuff never hides it.
    # A lineup gain or the highest-value player cancels the hole to no step, and the reason names both.
    # With no gain, the hole is one step down. With a lineup loss too, the hole is the reason.
    holes = " ".join(_hole_sentence(snapshot, slot) for slot in side.new_holes(snapshot))
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


# Injury report statuses that keep a player out of games. A player with one of them and no row in the
# returns file has no known return, so the standing adjuster counts him as back after RETURN_BY_WEEK.
# The lineup value counts him as due back at RETURN_BY_WEEK, so his projection ahead gives his value.
OUT_STATUSES = frozenset({"Out", "IR", "NA", "Sus", "PUP"})


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
    """True when the returns file has the player due back after the last completed week and by RETURN_BY_WEEK.

    A player who played in the known games of his return week is back, so he is no return bet.
    """
    return (back_inside(snapshot.returns.get(player_id), snapshot.as_of.completed_through, RETURN_BY_WEEK)
            and not _back_in_a_known_game(snapshot, player_id))


def _late_return(snapshot: Snapshot, player_id: str) -> str | None:
    """Why the player is not back by RETURN_BY_WEEK, or None when he is back by then or is not out."""
    week = snapshot.returns.get(player_id)
    if week is not None:
        return "is not due back before the playoffs" if week > RETURN_BY_WEEK else None
    if snapshot.players[player_id].injury_status in OUT_STATUSES:
        return "has no return week on file"
    return None


def _credited_return_bets(snapshot: Snapshot, side: _Side) -> list[str]:
    """The players the standing adjuster credits as a return bet: a contender with no lineup gain gets them.

    The injury adjuster reads this too, so a player the standing step counts in favor never counts against.
    """
    if team_race(snapshot, side.roster_id) != "contender" or side.lineup_gains:
        return []
    return [pid for pid in side.gets if _return_bet(snapshot, pid)]


def _gain_when(snapshot: Snapshot, side: _Side) -> str:
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


def _standing(snapshot: Snapshot, side: _Side) -> Adjuster:
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
    return _WoprWindow(value=int(_round_half_up(recent)), direction=direction, weeks_used=weeks[-SHARE_WEEKS:])


def _directions(snapshot: Snapshot, players: list[str]) -> set[str]:
    """The set of share directions, up or down, of the players.
    A flat share or a player with no usage data adds none."""
    through = snapshot.as_of.stats_through
    shares = [share(snapshot.stats, pid, through) for pid in players for share in (snap_share, target_share)]
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
    through = snapshot.as_of.stats_through
    names = _short_names(snapshot, players)
    sentences = []
    for pid in players:
        moved = [(kind, share) for kind, share in (("snap share", snap_share(snapshot.stats, pid, through)),
                                                   ("target share", target_share(snapshot.stats, pid, through)))
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


def _has_known_game(snapshot: Snapshot, player_id: str) -> bool:
    """True when the player has a game played in the known games of the trade week."""
    if snapshot.as_of.stats_through <= snapshot.as_of.completed_through:
        return False
    known = snapshot.stats.weeks.get(snapshot.as_of.stats_through)
    return known is not None and (known.stats.get(player_id) or {}).get("gp", 0) > 0


def _back_in_a_known_game(snapshot: Snapshot, player_id: str) -> bool:
    """True when the returns file has the player back by the trade week and he played in its known games.

    A player out with no row who played is the player hurt in his game, so his known game does not end his absence.
    """
    week = snapshot.returns.get(player_id)
    return week is not None and week <= snapshot.as_of.stats_through and _has_known_game(snapshot, player_id)


def due_back_week(snapshot: Snapshot, player_id: str) -> int | None:
    """The week the player counts as back, or None when he is not due back.

    The returns file gives the week. A player out with no row counts as back at RETURN_BY_WEEK, the week the standing
    adjuster reads too. Sleeper projects 0 for the weeks he is out, so his projection ahead must start at that week.
    A week through the last completed week is no return ahead, so he is not due back.
    A player with a returns row by the trade week who played in its known games is back, so he is not due back.
    """
    if _back_in_a_known_game(snapshot, player_id):
        return None
    week = snapshot.returns.get(player_id)
    # The position rank reads players on no roster, and the snapshot holds no injury status for them.
    player = snapshot.players.get(player_id)
    if week is None and player is not None and player.injury_status in OUT_STATUSES:
        week = RETURN_BY_WEEK
    return week if week is not None and week > snapshot.as_of.completed_through else None


def _due_back(snapshot: Snapshot, player_id: str) -> bool:
    """True when the returns file has the player back after the last completed week, so he is out now."""
    # The trend and the expected gap read only the returns file, so an out player with no row keeps his use.
    # A known game shows his use again, so it ends the exemption, as it ends due back in due_back_week.
    week = snapshot.returns.get(player_id)
    return week is not None and week > snapshot.as_of.completed_through and not _back_in_a_known_game(
        snapshot, player_id)


def _left_out(snapshot: Snapshot, side: _Side, what: str) -> tuple[set[str], list[str]]:
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


def _trend(snapshot: Snapshot, side: _Side) -> Adjuster:
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
    plus RETURN_WINDOW_WEEKS.
    """
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


def _injury(snapshot: Snapshot, side: _Side) -> Adjuster:
    """Injury: a player it gets who is out with no near return, or who was on the report in many weeks."""
    exempt = set(_credited_return_bets(snapshot, side))
    for pid in side.gets:
        if pid in exempt:
            continue
        name = snapshot.players[pid].name
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


def _handcuff(snapshot: Snapshot, side: _Side) -> Adjuster:
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
                 f"{int(_round_half_up(_carry_share(snapshot, pid)))}% of the carries, so he counts as a running back."
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


def _schedule(snapshot: Snapshot, side: _Side) -> Adjuster:
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


def _expected_gap(snapshot: Snapshot, side: _Side) -> Adjuster:
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


def rubric_adjusters(expected_on: bool) -> tuple[Callable[[Snapshot, _Side], Adjuster], ...]:
    """The adjusters in rubric order. The expected gap comes last, and only when `expected_on` is True."""
    return (_fit, _standing, _trend, _injury, _handcuff, _schedule) + ((_expected_gap,) if expected_on else ())


# The adjusters in rubric order. Each takes the snapshot and one side, and grade runs them in this order.
ADJUSTERS: tuple[Callable[[Snapshot, _Side], Adjuster], ...] = rubric_adjusters(EXPECTED_ADJUSTER_ON)
