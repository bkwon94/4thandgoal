"""
The adjusters of the trade analyzer rubric: roster fit, standing, trend and usage, injury, upside, handcuff, schedule,
and expected gap. It also holds what they read of one side: the best lineup before and after the trade, and the
handcuffs.
"""
from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal
from fractions import Fraction
from typing import TYPE_CHECKING, Literal, NamedTuple

from pydantic import BaseModel

from analyzer.tunables import (
    EXPECTED_ADJUSTER_ON,
    EXPECTED_GAP,
    FIT_THRESHOLD,
    HANDCUFF_CARRY_SHARE,
    INJURY_WEEKS,
    SCHEDULE_RANK_GAP,
    SELLER_GAP_WEEKS,
    WOPR_SWING,
)
from facts.names import last_name
from league.history import (
    SHARE_DIRECTION_WEEKS,
    air_yards_per_target,
    air_yards_share,
    carry_share,
    player_points,
    recent_carry_share,
    red_zone,
    scored_weeks,
    stats_complete,
)
from league.lineup import STRENGTH_SLOTS, StartingSlot, _above_the_line, _last_window_week, _lineup_total, lineup_slots
from league.models import UsageShare
from league.nfl_teams import team_name
from league.nflverse import SKILL_POSITIONS, TeamSchedule
from league.nflverse_expected import WINDOW_MIN_GAMES, window_gap
from league.numbers import one_decimal_text, ordinal, round_half_up
from league.points_allowed import most_points_text, opponent_rank
from league.ranks import (
    OUT_STATUSES,
    RANKED_POSITIONS,
    _back_in_a_known_game,
    _played_weeks,
    back_inside,
    due_back_week,
)
from league.snapshot import Snapshot
from league.standings_table import wins_per_week
from league.tunables import RETURN_WINDOW_WEEKS, SHARE_WEEKS

if TYPE_CHECKING:
    # The rubric module imports this one, so the trade model is a name for the type checker only.
    from analyzer.rubric import ProposedTrade

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
    # True when the row says nothing: a step of 0 and no new fact, such as "No player it gets is a handcuff."
    # The result document drops a silent row. GLOSSARY.md, "Silent row".
    silent: bool = False


# The analyze output and the analysis prompt name an adjuster's step in words.
STEP_WORDS = {1: "one step up", 0: "no step", -1: "one step down"}


def _join(names: list[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def named(snapshot: Snapshot, players: list[str], one: str, many: str) -> str:
    """The joined names of the players, then the phrase `one` for one player or the phrase `many` for more."""
    names = _join([snapshot.players[pid].name for pid in players])
    return f"{names} {one if len(players) == 1 else many}"


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

# The schedule adjuster says this when the schedule map is None.
NO_SCHEDULES = "The schedule sources are not available."


def _fit(snapshot: Snapshot, side: Side) -> Adjuster:
    """Roster fit: the change in the side's best lineup, in one sentence that counts the players in the top N.

    The sentence opens with the count at each position the trade touches, then names the cause of the step.
    """
    adjuster = _fit_step(snapshot, side)
    counts = _counts(snapshot, side)
    if counts:
        return adjuster.model_copy(update={"reason": f"{counts}{adjuster.reason}."})
    # A trade of kickers and defenses has no count, so the tail stands alone, and with no tail the row says nothing.
    tail = adjuster.reason.removeprefix(", and ").removeprefix(", but ")
    if not tail:
        return adjuster.model_copy(update={"reason": "No player in the trade has a line at his position.",
                                           "silent": adjuster.step == 0})
    return adjuster.model_copy(update={"reason": f"{tail[0].upper()}{tail[1:]}."})


def _plural(count: int, position: str) -> str:
    return f"{count} {position}" if count == 1 else f"{count} {position}s"


def _counts(snapshot: Snapshot, side: Side) -> str:
    """The count of the side's players in the top N at each position the trade touches, before and after.

    N is the line of the position, as a plain rank. GLOSSARY.md, "Depth". K and DEF have no line, so no count.
    """
    lines = snapshot.client.settings.lines
    touched = {snapshot.players[pid].position for pid in side.gets + side.gives}
    clauses = []
    for position in (pos for pos in RANKED_POSITIONS if pos in touched and pos in lines):
        before, after = side.depth(snapshot, position)
        top = f"in the top {lines[position]}"
        if before != after:
            clauses.append(f"go from {_plural(before, position)} {top} to {after}")
        elif before == 0:
            clauses.append(f"have no {position} {top}")
        else:
            clauses.append(f"keep {_plural(before, position)} {top}")
    return "You " + _join(clauses) if clauses else ""


def hole_sentence(snapshot: Snapshot, slot: StartingSlot) -> str:
    """The sentence that names a new hole: the slot, the player, and his position rank. The hole fact reads it.

    The sentence says "leaves the slot short", because "hole" is an inner word of the grade that no bullet may use.

    A rank that reads a week N game in progress ends with "game in progress", because it can still move.
    A player out with no returns row has no known return, so the sentence names no week, as the roster row does.
    """
    # The hole fact puts the team name first, as in "For Team, the trade leaves RB2 short:", so the lead is lowercase.
    lead = f"the trade leaves {slot.name} short:"
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


def _short_name(snapshot: Snapshot, player_id: str) -> str:
    return _short_names(snapshot, [player_id])[player_id]


def _cause(snapshot: Snapshot, slot: StartingSlot) -> str | None:
    """Why a new hole is a hole, when the count of the roster row does not show it, or None when it does.

    A slot with no player, or with a player below the line, shows in the count. A bye, an absence with no cover,
    and a player with no rank do not.
    """
    if slot.player is None:
        return None
    name = _short_name(snapshot, slot.player)
    if slot.bye_now:
        return f"{name} has his bye in week {snapshot.week}, and you need the win"
    if slot.absence is not None and not slot.absence.covered:
        week = slot.absence.week
        if slot.player not in snapshot.returns:
            return f"{name} is out with no return week on file"
        if week > _last_window_week(snapshot):
            return f"{name} is due back in week {week}"
        return f"{name} is due back in week {week}, and no other player covers him"
    if slot.rank is None:
        return f"{name} has no rank this season"
    return None


def _fit_step(snapshot: Snapshot, side: Side) -> Adjuster:
    """The roster fit step, and the tail of its reason after the counts, from the new holes and the lineup change.

    The tail starts with a comma, or is empty when the counts say it all. _fit puts the counts in front.
    """
    # A new hole costs the side on Sunday, so it blocks every step up, and a handcuff never hides it.
    # A lineup gain or the better player cancels the hole to no step, and the reason names both.
    # With no gain, the hole is one step down. With a lineup loss too, the hole is the reason.
    holes = side.new_holes(snapshot)
    if holes:
        causes = [cause for slot in holes if (cause := _cause(snapshot, slot)) is not None]
        but = "".join(f", but {cause}" if index == 0 else f", and {cause}" for index, cause in enumerate(causes))
        if side.lineup_gains:
            return Adjuster(name=ROSTER_FIT, step=0, reason=f", and your lineup scores more{but}")
        if side.gets_highest_value and not side.lineup_loses:
            return Adjuster(name=ROSTER_FIT, step=0, reason=f", and you get the better player{but}")
        return Adjuster(name=ROSTER_FIT, step=-1, reason="".join(f", and {cause}" for cause in causes))
    if side.lineup_loses:
        # A handcuff is insurance that sits on the bench, so a lineup loss in a trade for him does not count.
        if side.gets_handcuffs:
            handcuffs = _join([_short_name(snapshot, pid) for pid in side.gets_handcuffs])
            are = "is a handcuff" if len(side.gets_handcuffs) == 1 else "are handcuffs"
            return Adjuster(name=ROSTER_FIT, step=0,
                            reason=f", and your lineup scores less, but {handcuffs} {are}, so the loss does not count")
        return Adjuster(name=ROSTER_FIT, step=-1, reason=", and your lineup scores less")
    # In a one-for-two-or-more trade, the side that gets the depth must start every player it gets.
    # Otherwise it pays for a bench player, so neither the gain nor the better player earns the step up.
    gets_depth = len(side.gets) > 1 and len(side.gives) == 1
    if gets_depth and not all(pid in side.starters_after for pid in side.gets):
        if side.lineup_gains:
            return Adjuster(name=ROSTER_FIT, step=0,
                            reason=", and your lineup scores more, but you get more players than you can start")
        return Adjuster(name=ROSTER_FIT, step=0, reason=", but you get more players than you can start")
    if side.lineup_gains:
        return Adjuster(name=ROSTER_FIT, step=1, reason=", and your lineup scores more")
    # A lineup change smaller than the fit threshold is no lineup loss, so it does not block this step.
    if side.gets_highest_value:
        return Adjuster(name=ROSTER_FIT, step=1, reason=", and you get the better player")
    return Adjuster(name=ROSTER_FIT, step=0, reason="")


def team_race(snapshot: Snapshot, roster_id: int) -> Literal["contender", "seller", "middle"]:
    """Where the team stands by record. The standings rank by wins, then by points for."""
    standing = next(s for s in snapshot.standings if s.roster_id == roster_id)
    if standing.in_playoffs:
        return "contender"
    # games_from_cut is the team's wins minus the wins of the team in the last playoff spot. It counts games, so the
    # gap in weeks turns into games: two a week with the median game, else one.
    seller_gap = SELLER_GAP_WEEKS * wins_per_week(snapshot.client.settings.median_game)
    if -standing.games_from_cut > seller_gap:
        return "seller"
    return "middle"


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
    """The function gives the time of the side's lineup gain, as a tail of the standing row.

    The text is empty when the side gets no starter who is due back, because the gain is now.
    A player due back does not play this week, so a gain he makes in the lineup comes after his return, not now.
    The text names each player due back that the side gets and starts. It gives the latest return week of them.
    A player out with no returns row has no known return, so the text says he counts as back, as the fit note does.
    """
    due_back = [pid for pid in side.gets if pid in side.starters_after and due_back_week(snapshot, pid) is not None]
    if not due_back:
        return ""
    week = max(due_back_week(snapshot, pid) for pid in due_back)
    names = _join([_short_name(snapshot, pid) for pid in due_back])
    if any(pid not in snapshot.returns for pid in due_back):
        back = "counts as back" if len(due_back) == 1 else "count as back"
        return f" from week {week}, when {names} {back}"
    returns = "returns" if len(due_back) == 1 else "return"
    return f" after {names} {returns} in week {week}"


# The race and the need of each race, the lead of every standing row.
CONTENDER_NEED = "In a playoff spot, so you need points now"
SELLER_NEED = "Out of the playoff race, so you want the better player for the rest of the season"
MIDDLE_NEED = "Outside a playoff spot but still in the race, so you need points now"


def _points_now(snapshot: Snapshot, side: Side) -> str:
    """Whether the trade meets the need for points now, from the change in the side's best lineup."""
    if side.lineup_gains:
        return f"this trade adds some{_gain_when(snapshot, side)}"
    if side.lineup_loses:
        return "this trade gives some up"
    return "this trade keeps your points about the same"


def _standing(snapshot: Snapshot, side: Side) -> Adjuster:
    """Standing: the race of the team, its need, and whether the trade meets it, in one sentence.

    A contender steps up for points now or for a return before the playoffs. A seller steps up for the better player.
    """
    race = team_race(snapshot, side.roster_id)
    if race == "contender":
        if side.lineup_gains:
            return Adjuster(name=STANDING, step=1, reason=f"{CONTENDER_NEED}, and {_points_now(snapshot, side)}.")
        bets = _credited_return_bets(snapshot, side)
        if bets:
            names = _join([_short_name(snapshot, pid) for pid in bets])
            due = "is" if len(bets) == 1 else "are"
            return Adjuster(name=STANDING, step=1,
                            reason=f"In a playoff spot, so you need points by the playoffs, and {names} {due} "
                                   "due back before them.")
        late = [(pid, why) for pid in side.gets if (why := _late_return(snapshot, pid)) is not None]
        if side.lineup_loses and late:
            pid, why = late[0]
            return Adjuster(name=STANDING, step=-1,
                            reason=f"{CONTENDER_NEED}, and this trade gives some up for "
                                   f"{_short_name(snapshot, pid)}, who {why}.")
        return Adjuster(name=STANDING, step=0, reason=f"{CONTENDER_NEED}, and {_points_now(snapshot, side)}.")
    if race == "seller":
        if side.gets_highest_value:
            return Adjuster(name=STANDING, step=1, reason=f"{SELLER_NEED}, and you get him.")
        if side.gives_highest_value and side.lineup_gains:
            return Adjuster(name=STANDING, step=-1, reason=f"{SELLER_NEED}, but you give him up for points now.")
        if side.gives_highest_value:
            return Adjuster(name=STANDING, step=0, reason=f"{SELLER_NEED}, but you give him up.")
        return Adjuster(name=STANDING, step=0, reason=f"{SELLER_NEED}, and no player in the trade is clearly better.")
    return Adjuster(name=STANDING, step=0, reason=f"{MIDDLE_NEED}, and {_points_now(snapshot, side)}.")


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


def _share_mark(share: UsageShare) -> str:
    """The direction of a share as a mark after its percent, such as " (up)". A flat share has no mark."""
    return f" ({share.direction})" if share.direction in ("up", "down") else ""


def _usage_clause(snapshot: Snapshot, player_id: str, name: str) -> str | None:
    """One clause of the usage row for one player, with the numbers of his position and no weeks.

    A WR or a TE gives the snap share, the target share, and the air yards per target. An RB gives the snap share,
    the carry share, and the target share. A QB plays nearly every snap, so he has no clause, unless his snap share
    or his target share moved: the step reads that move, so the row names it. A kicker and a defense have no clause.
    The snap share and the target share carry their direction, because the step reads them.
    A number that reads a week N game in progress ends the clause with "game in progress", because it can still move.
    None when the player has no clause or no number to give.
    """
    position = snapshot.players[player_id].position
    snap, target = snapshot.usage_shares(player_id)
    if position == "QB":
        snap, target = (share if share is not None and share.direction in ("up", "down") else None
                        for share in (snap, target))
    elif position not in ("WR", "TE", "RB"):
        return None
    through = snapshot.as_of.stats_through
    parts = []
    if snap is not None:
        parts.append(f"plays {snap.percent}% of the snaps{_share_mark(snap)}")
    if position == "RB" and (carries := recent_carry_share(snapshot.stats, player_id, through)) is not None:
        parts.append(f"takes {carries.percent}% of the carries")
    if target is not None:
        parts.append(f"sees {target.percent}% of the targets{_share_mark(target)}")
    if position != "RB" and (air := air_yards_per_target(snapshot.stats, player_id, through)) is not None:
        parts.append(f"averages {one_decimal_text(air)} air yards per target")
    if not parts:
        return None
    weeks = [week for share in (snap, target) if share is not None for week in share.weeks_used]
    label = IN_PROGRESS_LABEL if _reads_a_game_in_progress(snapshot, player_id, weeks) else ""
    return f"{name} {_series(parts)}{label}"


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
    The row gives one clause per player, the players it gets first, then a clause for each player left out, then the
    tie break that made a step. The mark shows the step, so the row names no direction of its own.
    """
    left_out, notes = _left_out(snapshot, side, "use")
    gets = [pid for pid in side.gets if pid not in left_out]
    gives = [pid for pid in side.gives if pid not in left_out]
    step, tail = _trend_step(snapshot, gets, gives)
    names = _short_names(snapshot, side.gets + side.gives)
    clauses = [clause for pid in gets + gives if (clause := _usage_clause(snapshot, pid, names[pid])) is not None]
    clauses += [note.removesuffix(".") for note in notes]
    if tail is not None:
        clauses.append(tail)
    if not clauses:
        if step == 0:
            # A trade of quarterbacks, kickers, and defenses has no usage line, so the row says nothing.
            return Adjuster(name=TREND, step=0, reason="No player in the trade has a usage line.", silent=True)
        clauses.append("the players you get gain snap or target share, and the players you give lose it" if step > 0
                       else "the players you get lose snap or target share, and the players you give gain it")
    reason = "; ".join(clauses)
    return Adjuster(name=TREND, step=step, reason=f"{reason[0].upper()}{reason[1:]}.")


def _wopr_step(snapshot: Snapshot, gets: list[str], gives: list[str]) -> int | None:
    """The trend step when every share is flat and the WOPR of the WR and TE points one way.

    None when no WOPR moved or when it points both ways.
    """
    woprs = {pid: wopr for pid in gets + gives
             if (wopr := _wopr(snapshot, pid)) is not None and wopr.direction in ("up", "down")}
    if not woprs:
        return None
    got = {woprs[pid].direction for pid in gets if pid in woprs}
    gave = {woprs[pid].direction for pid in gives if pid in woprs}
    if got <= {"up"} and gave <= {"down"}:
        return 1
    if got <= {"down"} and gave <= {"up"}:
        return -1
    # WOPR only breaks a tie, so a WOPR that points both ways leaves the tie to red-zone use.
    return None


# The tail of the usage row when every share is flat and a tie break makes the step.
FLAT = "the shares are flat"
WOPR_TAILS = {1: f"{FLAT}, and the receivers you get gain WOPR, a mix of target share and air yards share",
              -1: f"{FLAT}, and the receivers you give gain WOPR, a mix of target share and air yards share"}
RED_ZONE_TAILS = {1: f"{FLAT}, and the players you get have more red-zone use",
                  -1: f"{FLAT}, and the players you give have more red-zone use"}


def _trend_step(snapshot: Snapshot, gets: list[str], gives: list[str]) -> tuple[int, str | None]:
    """The trend step, and the tail of the row when a tie break makes it, else None."""
    got, gave = _directions(snapshot, gets), _directions(snapshot, gives)
    if not got and not gave:
        # Every share is flat, so the WOPR of a WR or TE decides, and then red-zone use.
        wopr = _wopr_step(snapshot, gets, gives)
        if wopr is not None:
            return wopr, WOPR_TAILS[wopr]
        got_rz, gave_rz = _red_zone_touches(snapshot, gets), _red_zone_touches(snapshot, gives)
        if got_rz != gave_rz:
            step = 1 if got_rz > gave_rz else -1
            return step, RED_ZONE_TAILS[step]
        return 0, None
    # A player with one share up and one share down puts both in his side's set, so his trade is mixed.
    if got <= {"up"} and gave <= {"down"}:
        return 1, None
    if got <= {"down"} and gave <= {"up"}:
        return -1, None
    return 0, None


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


def _out_sentence(snapshot: Snapshot, player_id: str, name: str) -> str | None:
    """How long the player is out, such as "Cooper is out until week 11.", or None when he is not out.

    A player out with a return week after the last completed week is out until that week. A player out with no
    returns row has no known return.
    """
    if player_id in snapshot.out_for_season:
        return f"{name} is out for the season."
    if _due_back(snapshot, player_id):
        return f"{name} is out until week {snapshot.returns[player_id]}."
    if snapshot.players[player_id].injury_status in OUT_STATUSES:
        return f"{name} is out with no return week on file."
    return None


def _report_sentence(snapshot: Snapshot, player_id: str, lead: str) -> str | None:
    """The count of weeks on the injury report, such as "He was on the injury report in 5 of 8 weeks.".

    `lead` is the name, or "He" after a sentence that names him. None when no count ran or the count is 0.
    """
    weeks = _report_weeks(snapshot, player_id)
    if not weeks:
        return None
    return f"{lead} was on the injury report in {weeks} of {snapshot.as_of.completed_through} weeks."


def _injury_text(snapshot: Snapshot, player_id: str, name: str) -> str:
    """The injury sentences of one player: how long he is out, then his weeks on the injury report."""
    out = _out_sentence(snapshot, player_id, name)
    report = _report_sentence(snapshot, player_id, name if out is None else "He")
    return " ".join(sentence for sentence in (out, report) if sentence is not None)


def _injury(snapshot: Snapshot, side: Side) -> Adjuster:
    """Injury: a player it gets who is out for the season, out with no near return, or on the report in many weeks.

    With no step, the row still names each player it gets who is out now, because his return week is news.
    """
    # A star return bet is the upside's credit, so the injury never counts him against the same side. ADR 0005.
    exempt = set(_credited_return_bets(snapshot, side)) | {pid for pid in side.gets if _star_return_bet(snapshot, pid)}
    names = _short_names(snapshot, side.gets)
    for pid in side.gets:
        if pid in exempt:
            continue
        # The season mark comes first, then no near return, then the count of report weeks, as the step reads them.
        if (pid in snapshot.out_for_season or _out_with_no_near_return(snapshot, pid)
                or (_report_weeks(snapshot, pid) or 0) >= INJURY_WEEKS):
            return Adjuster(name=INJURY, step=-1, reason=_injury_text(snapshot, pid, names[pid]))
    out_now = [_injury_text(snapshot, pid, names[pid]) for pid in side.gets
               if _out_sentence(snapshot, pid, names[pid]) is not None]
    notes = []
    if not _has_injury_report(snapshot):
        notes.append("The injury report is not available, so no count of report weeks ran.")
    elif unmapped := _not_in_id_map(snapshot, side.gets):
        notes.append(named(snapshot, unmapped, "has no injury report count on file.",
                           "have no injury report count on file."))
    reason = " ".join([*out_now, *notes]) or "No player it gets is out for long or often on the injury report."
    # A count that did not run is a fact the reader needs, so only a full count that finds nothing is silent.
    return Adjuster(name=INJURY, step=0, reason=reason, silent=not out_now and not notes)


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
        if _star_return_bet(snapshot, pid):
            name = _short_name(snapshot, pid)
            position = snapshot.players[pid].position
            week = snapshot.returns.get(pid)
            back = f"due back in week {week}" if week is not None else "out now with no return week on file"
            return Adjuster(name=UPSIDE, step=1, reason=f"{name} is a top {position}, {back}.")
        teammate = _opportunity_from(snapshot, pid)
        if teammate is None:
            continue
        if _rising_signal(snapshot, pid) is not None:
            # _out_with_no_near_return holds the season mark too, so the reason names the plainer cause first.
            out = "out for the season" if teammate in snapshot.out_for_season else "out"
            names = _short_names(snapshot, [pid, teammate])
            return Adjuster(name=UPSIDE, step=1, reason=f"{names[pid]} gets more work while {names[teammate]} is {out}.")
    return Adjuster(name=UPSIDE, step=0, reason="No player it gets is a top player out now or gets more work.",
                    silent=True)


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
    after = _roster_after(snapshot, side.roster_id, side.gives, side.gets)
    parts = [f"{_backs_up(snapshot, pid, after)}." for pid in side.gets_handcuffs]
    freed = [pid for pid in side.gets if pid not in side.handcuffs and _behind_a_starter(snapshot, pid, after)]
    # The gate compares the exact share. The reason shows it rounded, as every other percent in a reason.
    parts.extend(f"{_backs_up(snapshot, pid, after)}, but he takes {int(round_half_up(_carry_share(snapshot, pid)))}% "
                 "of the carries, so he is no handcuff."
                 for pid in freed)
    reason = " ".join(parts) if parts else "No player it gets is a handcuff."
    # Only a running back can be a handcuff, so only a running back with no gsis_id misses a check.
    unmapped = _not_in_id_map(snapshot, [pid for pid in side.gets if snapshot.players[pid].position == "RB"])
    if unmapped:
        reason += " " + named(snapshot, unmapped, "has no depth chart entry on file, so no handcuff check ran for him.",
                               "have no depth chart entry on file, so no handcuff check ran for them.")
    # A check that did not run is a fact the reader needs, so only a full check that finds no handcuff is silent.
    return Adjuster(name=HANDCUFF, step=0, reason=reason, silent=not parts and not unmapped)


def _backs_up(snapshot: Snapshot, player_id: str, roster: list[str]) -> str:
    """The player, the starter on the roster that he backs up, and the team, such as
    "Spears backs up your RB, Pollard, on the Titans depth chart". The player is behind a starter on the roster."""
    team = snapshot.players[player_id].nfl_team or ""
    sleeper_of_gsis = {snapshot.id_map[pid]: pid for pid in roster if pid in snapshot.id_map}
    starter = sleeper_of_gsis[_rb_chart(snapshot, team)[0]]
    names = _short_names(snapshot, [player_id, starter])
    return f"{names[player_id]} backs up your RB, {names[starter]}, on the {team_name(team)} depth chart"


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
    playoff_lean: Lean
    if rank_got is None or rank_gave is None:
        playoff_lean = "even"
    elif rank_gave - rank_got >= SCHEDULE_RANK_GAP:
        playoff_lean = "for"
    elif rank_got - rank_gave >= SCHEDULE_RANK_GAP:
        playoff_lean = "against"
    else:
        playoff_lean = "even"
    # Two signals that agree, or one signal with the other even, give the lean. Two that conflict cancel out.
    leans = {bye_lean, playoff_lean} - {"even"}
    lean: Lean = leans.pop() if len(leans) == 1 else "even"
    # The mark shows the lean, so the row names the facts behind it: each bye and each playoff opponent.
    names = _short_names(snapshot, side.gets)
    sentences = [sentence for pid in side.gets if (sentence := _schedule_sentence(snapshot, pid, names[pid]))]
    if not sentences:
        return Adjuster(name=SCHEDULE, step=0, lean=lean, reason="No player you get has a playoff schedule.",
                        silent=lean == "even")
    return Adjuster(name=SCHEDULE, step=0, lean=lean, reason=" ".join(sentences))


def _span_text(weeks: list[int]) -> str:
    """The weeks as a span, such as "weeks 15 to 17", when they run in a row, else as a list."""
    if len(weeks) > 2 and weeks == list(range(weeks[0], weeks[-1] + 1)):
        return f"weeks {weeks[0]} to {weeks[-1]}"
    return _weeks_text(weeks)


def _schedule_sentence(snapshot: Snapshot, player_id: str, name: str) -> str | None:
    """The bye of the player after the Week line weeks, and each playoff opponent with its rank at his position.

    The Week line covers the trade week and the next week, so a bye in those weeks is its fact, not this row's.
    The first opponent gives the rank in full, such as "TEN (3rd most points to WRs)", and the rest give the ordinal.
    None for a player with no schedule, or with no bye left and no playoff game.
    """
    schedule = _scheduled(snapshot, player_id)
    if schedule is None:
        return None
    position = snapshot.players[player_id].position
    parts = []
    if schedule.bye_week is not None and schedule.bye_week > snapshot.week + 1:
        parts.append(f"has his bye in week {schedule.bye_week}")
    weeks = sorted(schedule.playoff_opponents)
    if weeks:
        opponents = []
        for opponent in (schedule.playoff_opponents[week] for week in weeks):
            rank = opponent_rank(snapshot.points_allowed, opponent, position)
            if rank is None:
                opponents.append(opponent)
            elif not any("(" in text for text in opponents):
                opponents.append(f"{opponent} ({most_points_text(rank, position)})")
            else:
                opponents.append(f"{opponent} ({ordinal(rank)})")
        parts.append(f"faces {_series(opponents)} in {_span_text(weeks)}")
    if not parts:
        return None
    return f"{name} {' and '.join(parts)}."


def _series(items: list[str]) -> str:
    """The items as a list with a comma before the last "and", such as "TEN, CLE, and HOU"."""
    if len(items) <= 2:
        return " and ".join(items)
    return ", ".join(items[:-1]) + ", and " + items[-1]


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
