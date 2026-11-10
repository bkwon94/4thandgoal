"""
The sell high sheet of one roster: per player the trade value, the lineup value, the injury, the trend of the last 4
weeks, and the schedule ahead, side by side as facts. Code measures and drops no player. The Advisor picks and writes
why.
"""
from decimal import Decimal

from analyzer.chart_facts import player_value_facts
from analyzer.measures import _injury_text, _report_weeks
from facts.tokens import Nums, fact
from league.history import season_rank
from league.models import Fact
from league.points_allowed import most_points_text, opponent_rank
from league.ranks import (
    RANKED_POSITIONS,
    due_back_week,
    recent_points_per_game,
    recent_rank,
    season_points_per_game,
)
from league.snapshot import Snapshot
from league.tunables import LINEUP_WEEKS

# The weeks of the schedule ahead: the trade week and the 3 weeks after it, as many as the trend looks back.
AHEAD_WEEKS = LINEUP_WEEKS


def sheet_players(snapshot: Snapshot, roster_id: int) -> list[str]:
    """The players of the roster that the sheet lists: each QB, RB, WR, and TE, in roster order.

    A kicker or a defense has no position rank and no chart row, so no manager sells one high. That is a hard rule of
    the positions, not a screen: every player at a ranked position is on the sheet.
    """
    return [pid for pid in snapshot.rosters[roster_id]
            if pid in snapshot.players and snapshot.players[pid].position in RANKED_POSITIONS]


def _who(snapshot: Snapshot, pid: str) -> str:
    player = snapshot.players[pid]
    return f"{player.name} ({player.position}, {player.nfl_team})" if player.nfl_team else player.name


def _per_game(value: Decimal) -> float:
    return float(round(value, 1))


def _lineup_fact(snapshot: Snapshot, pid: str) -> Fact:
    """The points per game that the player counts for in a lineup now, and his position rank. A player due back
    counts for his projection ahead, and a player out for the season counts for none. GLOSSARY.md, "Lineup value"."""
    n = Nums()
    player = snapshot.players[pid]
    who = _who(snapshot, pid)
    value = _per_game(snapshot.lineup_value(pid))
    back = None if snapshot.projections_ahead is None else due_back_week(snapshot, pid)
    if pid in snapshot.out_for_season:
        text = f"{who} is out for the season, so he counts for no points in a lineup."
    elif back is not None:
        text = (f"{who} is out now. He is due back in week {n(back)}, and he counts for {n(value)} points per game "
                "in a lineup, by his projection from then on.")
    else:
        text = f"{who} counts for {n(value)} points per game in a lineup now."
    rank = snapshot.position_rank(pid)
    if rank is not None:
        text += f" His position rank is {n.text(f'{player.position}{rank}')}."
    return fact(f"{pid}.lineup", text, n, [], [player.name])


def _injury_fact(snapshot: Snapshot, pid: str) -> Fact:
    """The text of the injury Measure for the player: how long he is out, then his weeks on the injury report.

    A player who is out has a low price, so the Advisor needs this fact to judge a sell. The fact only states the
    injury: no code drops an injured player from the sheet (ADR 0030). A player with no injury gets a plain line, so
    each player has the same reads.
    """
    n = Nums()
    player = snapshot.players[pid]
    text = _injury_text(snapshot, pid, player.name)
    if not text:
        text = f"{player.name} is not out now."
        if _report_weeks(snapshot, pid) is None:
            text += " No count of his weeks on the injury report is on file."
    return fact(f"{pid}.injury", n.text(text), n, [], [player.name])


def _trend_fact(snapshot: Snapshot, pid: str) -> Fact:
    """The points per game over the last 4 weeks beside the points per game of the season, with the Recent rank and
    the Season rank. GLOSSARY.md, "Recent rank" and "Season rank"."""
    n = Nums()
    player = snapshot.players[pid]
    recent = _per_game(recent_points_per_game(snapshot, pid))
    season = _per_game(season_points_per_game(snapshot, pid))
    text = (f"Over the last {n(LINEUP_WEEKS)} weeks, {player.name} scored {n(recent)} points per game, against "
            f"{n(season)} over the season.")
    ranks = []
    if (recent_place := recent_rank(snapshot, pid)) is not None:
        ranks.append(f"his Recent rank is {n.text(f'{player.position}{recent_place}')}")
    if (season_place := season_rank(snapshot.stats, pid, snapshot.as_of.stats_through)) is not None:
        ranks.append(f"his Season rank is {n.text(f'{player.position}{season_place[0]}')}")
    if ranks:
        joined = " and ".join(ranks)
        text += f" {joined[0].upper()}{joined[1:]}."
    return fact(f"{pid}.trend", text, n, [], [player.name])


def _game_text(snapshot: Snapshot, pid: str, week: int, n: Nums) -> str:
    """One week of the schedule ahead: the opponent with its rank in points allowed at his position, or the bye."""
    player = snapshot.players[pid]
    schedule = snapshot.schedules.get(player.nfl_team or "") if snapshot.schedules is not None else None
    game = None if schedule is None else schedule.games.get(week)
    if game is None:
        return f"week {n(week)} bye" if schedule is not None and schedule.bye_week == week else f"week {n(week)} no game"
    where = f"{game.opponent} at home" if game.home else f"at {game.opponent}"
    rank = None if snapshot.points_allowed is None else opponent_rank(snapshot.points_allowed, game.opponent,
                                                                      player.position)
    if rank is None:
        return f"week {n(week)} {where}"
    # The rank goes through Nums, so a Bullet may say "3rd most points to WRs" or "4th fewest points to RBs".
    teams = len(snapshot.points_allowed)
    return f"week {n(week)} {where}, {n.text(most_points_text(rank, player.position, teams))}"


def _schedule_fact(snapshot: Snapshot, pid: str) -> Fact:
    """The NFL games of the player's team in the trade week and the weeks after it, through the regular season, each
    with the rank of the opponent in points allowed at his position. Rank 1 gives up the most, and a rank in the bottom
    half reads from the fewest."""
    n = Nums()
    player = snapshot.players[pid]
    last = min(snapshot.week + AHEAD_WEEKS - 1, snapshot.client.settings.last_regular_week)
    weeks = list(range(snapshot.week, last + 1))
    if snapshot.schedules is None or not player.nfl_team or not weeks:
        text = f"No NFL schedule ahead is on file for {player.name}."
    else:
        text = f"The schedule ahead of {player.name}: " + "; ".join(_game_text(snapshot, pid, w, n) for w in weeks) + "."
    return fact(f"{pid}.schedule", text, n, [], [player.name])


def _week_fact(snapshot: Snapshot) -> Fact:
    """The week of the sheet and the last week the stats read."""
    n = Nums()
    text = (f"It is week {n(snapshot.week)} of the {n(snapshot.season)} season. "
            f"Player stats run through week {n(snapshot.as_of.stats_through)}.")
    return fact("sell.week", text, n, [], [])


def sell_sheet(snapshot: Snapshot, roster_id: int) -> dict[str, Fact]:
    """The facts of the sell high sheet by id: the week, then for each player of the roster his trade value, his
    lineup value, his injury, his trend, and his schedule ahead. A week with no chart has the one trade.chart fact
    instead of each value fact. The news of each player comes after, from the news feed of the Advisor."""
    players = sheet_players(snapshot, roster_id)
    values = {f.id: f for f in player_value_facts(players, snapshot)}
    facts = [_week_fact(snapshot), *(values.values() if "trade.chart" in values else [])]
    for pid in players:
        facts += [*([values[f"{pid}.value"]] if f"{pid}.value" in values else []), _lineup_fact(snapshot, pid),
                  _injury_fact(snapshot, pid), _trend_fact(snapshot, pid), _schedule_fact(snapshot, pid)]
    return {f.id: f for f in facts}
