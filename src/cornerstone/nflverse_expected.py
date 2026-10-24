"""
Read the expected points of each player per game from the ffopportunity weekly file, rescaled to the league scoring.
The reader checks the file for the games of the last game day of week N. A file without them reads through week N-1.
"""
from pathlib import Path

from cornerstone.models import ExpectedGame, ExpectedPoints, r2
from cornerstone.nflverse_rows import _number, _rows

# The file scores full PPR: 1 point per reception and -2 per interception.
FILE_REC = 1.0
FILE_PASS_INT = -2.0
# The expected window: the last games a player played. Fewer games than the minimum give no window gap.
WINDOW_GAMES = 3
WINDOW_MIN_GAMES = 2


def _last_games(games: Path, season: int, week: int) -> set[str]:
    """The game ids of the last game day of week `week`. Empty when the schedules have no game of the week.

    Every game of the last game day must be in the file, so the rule also covers two games on that day.
    """
    days: dict[str, set[str]] = {}
    for row in _rows(games):
        if row["season"] == str(season) and row["game_type"] == "REG" and row["week"] == str(week):
            days.setdefault(row["gameday"], set()).add(row["game_id"])
    return days[max(days)] if days else set()


def _expected(row: dict[str, str], scoring: dict[str, float]) -> float:
    """The full-PPR expected total of the row, rescaled to the league weights for receptions and interceptions.

    The expected points have no fumble term, so fumbles stay out.
    """
    return (_number(row["total_fantasy_points_exp"])
            - (FILE_REC - scoring.get("rec", 0.0)) * _number(row["receptions_exp"])
            + (scoring.get("pass_int", 0.0) - FILE_PASS_INT) * _number(row["pass_interception_exp"]))


def read_expected(path: Path, games: Path, season: int, week: int, scoring: dict[str, float],
                  sleeper_of_gsis: dict[str, str]) -> ExpectedPoints | None:
    """The expected window of each player by Sleeper ID, through week `week` or week `week` - 1.

    The file reads through week `week` when it holds every game of the last game day of the week, and through
    the week before when it does not. None when the schedules have no game of week `week`, because then the
    reader cannot tell a full file from a lagged one. The reader skips a player with no Sleeper ID in the gsis map.
    The weights come from the league scoring, so a change of the scoring never silently breaks the rescale.
    The file's actual points cannot match the league's box score, so the reader gives expected points only.
    """
    last = _last_games(games, season, week)
    if not last:
        return None
    rows = [row for row in _rows(path) if row["week"].isdigit() and int(row["week"]) <= week]
    through = week if last <= {row["game_id"] for row in rows} else week - 1
    played: dict[str, list[ExpectedGame]] = {}
    for row in rows:
        pid = sleeper_of_gsis.get(row["player_id"])
        if pid is None or int(row["week"]) > through:
            continue
        played.setdefault(pid, []).append(ExpectedGame(
            week=int(row["week"]), game_id=row["game_id"], expected=r2(_expected(row, scoring))))
    # The file lists the games of a player out of week order. The reader alone cuts the window to the last games.
    return ExpectedPoints(through_week=through, players={
        pid: sorted(player, key=lambda g: g.week)[-WINDOW_GAMES:] for pid, player in sorted(played.items())})


def window_gap(games: list[ExpectedGame], actual: dict[int, float]) -> float | None:
    """The mean of the actual points minus the expected points over the expected window.

    `games` is the window that read_expected gives, so this function does not cut it again. `actual` holds the
    league's actual points of the player by week. A game with no actual points does not count, and fewer than
    WINDOW_MIN_GAMES games with them give None.
    """
    gaps = [actual[g.week] - g.expected for g in games if g.week in actual]
    if len(gaps) < WINDOW_MIN_GAMES:
        return None
    return r2(sum(gaps) / len(gaps))
