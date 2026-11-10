"""
The Week line of each side of a grade, for the trade week and the next week: the count of its players who play, the
opponent of each player it gets, each bye, each player who is out, and each player who steps up. The code writes it
as a plain fact for the page, and the Advisor makes the call.
"""
from datetime import timedelta
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from analyzer.measures import _join, _short_names
from analyzer.trade import ProposedTrade
from analyzer.tunables import STEP_UP_CHART_HOURS
from league.lineup import _above_the_line
from league.nflverse import SKILL_POSITIONS, ScheduledGame
from league.points_allowed import most_points_text, opponent_rank
from league.ranks import RANKED_POSITIONS, _back_in_a_known_game
from league.snapshot import Snapshot, SnapshotPlayer

# The Sleeper statuses that keep a player out of both weeks. An NFL player on IR misses at least 4 games.
# Decision 02 of grade-clarity. "Out" counts for the trade week only, and Questionable and Doubtful never count.
LONG_OUT_STATUSES = ("IR", "PUP", "NA", "Sus")
OUT = "Out"
# Sleeper keeps the status of the last game until the new injury reports of the week, so on a Tuesday and a Wednesday
# an Out is the one of the last game. The day is the one in US Eastern time, where the NFL week runs.
EASTERN = ZoneInfo("America/New_York")
LAST_GAME_DAYS = (1, 2)


class WeekLine(BaseModel):
    """The Week line of one side for one week: the week and the text, such as "Week 9: WRs in the top 36 ..."."""

    week: int
    text: str


def week_lines(trade: ProposedTrade, snapshot: Snapshot) -> dict[int, list[WeekLine]]:
    """The Week lines of each side by roster id, one for the trade week and one for the next week.

    A next week past the regular season has no line, because a Week line covers the weeks of the regular season only.
    """
    weeks = [week for week in (snapshot.week, snapshot.week + 1)
             if week <= snapshot.client.settings.last_regular_week]
    lines = snapshot.client.settings.lines
    touched = [position for position in RANKED_POSITIONS if position in lines
               and any(snapshot.players[pid].position == position for pid in trade.player_ids)]
    return {side.roster_id: [WeekLine(week=week, text=_text(trade, snapshot, side.roster_id, touched, week))
                             for week in weeks]
            for side in trade.sides}


def _text(trade: ProposedTrade, snapshot: Snapshot, roster_id: int, touched: list[str], week: int) -> str:
    """The text of the Week line of one side for one week. Each part is one sentence."""
    gives = next(side.player_ids for side in trade.sides if side.roster_id == roster_id)
    gets = trade.gets(roster_id)
    before = snapshot.rosters[roster_id]
    after = [pid for pid in before if pid not in gives] + gets
    # The line names the players at the touched positions, and the opponent of each player the side gets.
    named = [pid for pid in after if snapshot.players[pid].position in touched]
    names = _short_names(snapshot, list(dict.fromkeys(named + gets)))
    sentences = [_count_sentence(snapshot, position, before, after, week) for position in touched]
    sentences += [sentence for pid in gets if (sentence := _opponent_sentence(snapshot, pid, names[pid], week))]
    byes = [names[pid] for pid in named if _has_bye(snapshot, pid, week)]
    if byes:
        sentences.append(f"{_join(byes)} {'has' if len(byes) == 1 else 'have'} a bye.")
    sentences += _absence_sentences(snapshot, named, names, week)
    steps_up = [names[pid] for pid in named if _steps_up(snapshot, pid, week)]
    if steps_up:
        sentences.append(f"{_join(steps_up)} {'steps' if len(steps_up) == 1 else 'step'} up.")
    if snapshot.schedules is None:
        sentences.append("No NFL schedule is on file, so no bye or opponent shows.")
    return f"Week {week}: " + " ".join(sentences)


def _count_sentence(snapshot: Snapshot, position: str, before: list[str], after: list[str], week: int) -> str:
    """The count of the players at the position in the top N who play that week, before and after the trade.

    N is the line of the position, as the roster row says it. The count assigns no lineup slot.
    """
    def count(roster: list[str]) -> int:
        return sum(1 for pid in roster if snapshot.players[pid].position == position
                   and _above_the_line(snapshot, pid) and _plays(snapshot, pid, week)
                   and _out_reason(snapshot, snapshot.players[pid], week) is None)

    old, new = count(before), count(after)
    who = f"{position}s in the top {snapshot.client.settings.lines[position]} who play"
    return f"{who} stay at {old}." if old == new else f"{who} go from {old} to {new}."


def _game(snapshot: Snapshot, player_id: str, week: int) -> ScheduledGame | None:
    """The game of the player's NFL team that week. None on a bye, for a player with no team, or with no schedule."""
    team = snapshot.players[player_id].nfl_team
    schedule = None if snapshot.schedules is None or team is None else snapshot.schedules.get(team)
    return None if schedule is None else schedule.games.get(week)


def _plays(snapshot: Snapshot, player_id: str, week: int) -> bool:
    """True when the player's NFL team has a game that week. With no schedule on file, every player plays."""
    return snapshot.schedules is None or _game(snapshot, player_id, week) is not None


def _has_bye(snapshot: Snapshot, player_id: str, week: int) -> bool:
    """True when the schedule of the player's NFL team has its bye that week."""
    team = snapshot.players[player_id].nfl_team
    schedule = None if snapshot.schedules is None or team is None else snapshot.schedules.get(team)
    return schedule is not None and schedule.bye_week == week


def _opponent_sentence(snapshot: Snapshot, player_id: str, name: str, week: int) -> str | None:
    """The opponent of a player the side gets, with its rank in points allowed at his position. Rank 1 gives up the
    most. None for a player who does not play that week, or who is out, or a kicker or a defense."""
    position = snapshot.players[player_id].position
    game = _game(snapshot, player_id, week)
    if (game is None or position not in SKILL_POSITIONS
            or _out_reason(snapshot, snapshot.players[player_id], week) is not None):
        return None
    where = f"{game.opponent} at home" if game.home else f"at {game.opponent}"
    rank = None if snapshot.points_allowed is None else opponent_rank(snapshot.points_allowed, game.opponent, position)
    if rank is None:
        return f"{name} plays {where}."
    return f"{name} plays {where}, {most_points_text(rank, position)}."


def _out_reason(snapshot: Snapshot, player: SnapshotPlayer, week: int) -> tuple[str, int | None] | None:
    """Why the player is out that week, as a kind and a return week, or None when he can play. Decision 02.

    Out for the season and a return week on file after the week count in each week. IR, PUP, NA, and Sus count in
    each week too. Out counts in the trade week only. Questionable and Doubtful never count.
    The player can be on no roster, as the player ahead on a depth chart often is.
    A player with a returns row by the trade week who played in its known games is back, as `due_back_week` reads
    him, though his status can still say out.
    """
    if player.player_id in snapshot.out_for_season:
        return "season", None
    if _back_in_a_known_game(snapshot, player.player_id):
        return None
    back = snapshot.returns.get(player.player_id)
    if back is not None and back > week:
        return "until", back
    status = player.injury_status
    if status in LONG_OUT_STATUSES:
        return status, None
    if status == OUT and week == snapshot.week:
        return OUT, None
    return None


def counted_status(status: str | None) -> str | None:
    """The Sleeper status as the Week line reads it: an out status, or None for a status that never counts."""
    return status if status == OUT or status in LONG_OUT_STATUSES else None


def chart_is_fresh(snapshot: Snapshot) -> bool:
    """True when the newest depth chart is at most STEP_UP_CHART_HOURS older than the grade. Decision 02.

    With no grade time, the age of the chart is not known, so the chart is not fresh.
    """
    graded_at, dt = snapshot.as_of.graded_at, snapshot.depth_chart_dt
    return graded_at is not None and dt is not None and graded_at - dt <= timedelta(hours=STEP_UP_CHART_HOURS)


def _steps_up(snapshot: Snapshot, player_id: str, week: int) -> bool:
    """True when the player directly ahead of him on his NFL team's depth chart is out that week. QB, RB, WR, TE.

    A player who is out himself, or whose team does not play that week, does not step up. A depth chart more than
    STEP_UP_CHART_HOURS older than the grade names no step-up.
    """
    ahead = snapshot.ahead_on_chart.get(player_id)
    return (ahead is not None and snapshot.players[player_id].position in SKILL_POSITIONS and chart_is_fresh(snapshot)
            and _plays(snapshot, player_id, week) and _out_reason(snapshot, snapshot.players[player_id], week) is None
            and _out_reason(snapshot, ahead, week) is not None)


def last_game_status(snapshot: Snapshot) -> bool:
    """True when the grade runs on a Tuesday or a Wednesday in US Eastern time, so an Out is from the last game."""
    graded_at = snapshot.as_of.graded_at
    return graded_at is not None and graded_at.astimezone(EASTERN).weekday() in LAST_GAME_DAYS


def _absence_words(snapshot: Snapshot, kind: str, back: int | None, many: bool) -> str:
    """The words after the names of the players out for one reason, such as "is on IR" or "are listed Out"."""
    verb = "are" if many else "is"
    if kind == "season":
        return f"{verb} out for the season"
    if kind == "until":
        return f"{verb} out until week {back}"
    if kind == OUT:
        return f"{'were' if many else 'was'} listed Out last week" if last_game_status(snapshot) else f"{verb} listed Out"
    return {"IR": f"{verb} on IR", "PUP": f"{verb} on the PUP list", "NA": f"{verb} not active",
            "Sus": f"{verb} suspended"}[kind]


def _absence_sentences(snapshot: Snapshot, players: list[str], names: dict[str, str], week: int) -> list[str]:
    """One sentence for each reason a player of the side is out that week, with the names of the players."""
    by_reason: dict[tuple[str, int | None], list[str]] = {}
    for pid in players:
        reason = _out_reason(snapshot, snapshot.players[pid], week)
        if reason is not None:
            by_reason.setdefault(reason, []).append(names[pid])
    return [f"{_join(out)} {_absence_words(snapshot, kind, back, len(out) > 1)}."
            for (kind, back), out in by_reason.items()]
