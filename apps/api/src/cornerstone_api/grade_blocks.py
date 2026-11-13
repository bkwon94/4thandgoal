"""
The blocks of two personal Topics: the slot rank bars of How you stack up, from the roster grade, and the bye grid of
Weak spots, from the bye weeks of the NFL schedules in the live snapshot. Code reads the data and adds no formula.
"""
from league.lineup import lineup_now
from league.numbers import ordinal
from league.snapshot import Snapshot
from managers.grade import SLOT_POSITIONS, ManagerGrade, Starter

SLOT_RANKS_KIND = "slot_ranks"
BYE_GRID_KIND = "bye_grid"
# The slots of a lineup that the roster grade does not fill. The grade starts only the positions with a line, so the
# bye grid takes these starters from the lineup now.
UNGRADED_SLOTS = ("K", "DEF")
# The weeks of the bye grid, from the live week on. Six columns fit the card at 375 px wide, and a bye further out
# changes no decision of this week.
BYE_GRID_WEEKS = 6


def slot_rank_bars(grade: ManagerGrade, teams: int) -> dict:
    """The slot rank bars: one row for each of the SLOT_POSITIONS, in that order, with the grade and its read.

    The roster grade ranks only these positions. A FLEX slot takes an RB, a WR, or a TE, so a FLEX rank counts the same
    players twice, and a DEF rank is out of the grade (decision 11).
    """
    ranks = {slot.position: slot.rank for slot in grade.slots}
    return {"kind": SLOT_RANKS_KIND, "grade": grade.letter, "read": grade.read, "teams": teams,
            "rows": [{"position": position, "rank": ranks[position], "label": f"{ordinal(ranks[position])} of {teams}"}
                     for position in SLOT_POSITIONS if position in ranks]}


def bye_grid(snapshot: Snapshot, roster_id: int, starters: list[Starter]) -> dict:
    """The bye grid: the starters in slot order, with the K and the DEF of the lineup now, then the bench, each with the bye week of his NFL team, against the
    next weeks of the regular season. The site draws a red dot for a starter in his bye week.

    The bye week comes from the NFL schedules of the snapshot, by Sleeper team code. A player with no NFL team, or a
    snapshot with no schedules, has no bye week.
    """
    schedules = snapshot.schedules or {}
    last = snapshot.client.settings.last_regular_week
    weeks = list(range(snapshot.week, min(snapshot.week + BYE_GRID_WEEKS, last + 1)))

    def row(pid: str, slot: str | None) -> dict:
        player = snapshot.players[pid]
        schedule = schedules.get(player.nfl_team or "")
        return {"name": player.name, "position": player.position, "nfl_team": player.nfl_team, "slot": slot,
                "starter": slot is not None, "bye": schedule.bye_week if schedule else None}

    started = [(s.player_id, s.slot) for s in starters if s.player_id is not None]
    # A K or a DEF on a bye leaves a slot empty too, so the grid marks him as it marks a skill starter.
    started += [(slot.player, slot.roster_slot) for slot in lineup_now(snapshot.rosters[roster_id], snapshot)
                if slot.roster_slot in UNGRADED_SLOTS and slot.player is not None]
    shown = {pid for pid, _ in started}
    bench = sorted((pid for pid in snapshot.rosters[roster_id] if pid not in shown and pid in snapshot.players),
                   key=lambda pid: (snapshot.players[pid].position, snapshot.players[pid].name))
    return {"kind": BYE_GRID_KIND, "weeks": weeks,
            "players": [row(pid, slot) for pid, slot in started] + [row(pid, None) for pid in bench]}
