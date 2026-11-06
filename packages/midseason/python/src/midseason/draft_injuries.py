"""
The games that each drafted player missed with an injury, for the "hurt" tag of a draft bust. It reads the weekly
injury report that the app hands in and the games of the saved history.
"""
from collections.abc import Collection, Mapping

from league.history import scored_weeks
from league.models import History


def injured_games(
    player_ids: Collection[str], report: Mapping[str, Mapping[int, str]], history: History, through: int,
) -> dict[str, int]:
    """The count of weeks 1 to `through` in which each player played no game and the injury report named him.

    `report` is the report status by Sleeper player ID and week, from the nflverse weekly injury report. A week with
    no game and no report row, such as a bye, is no injured game.
    """
    counts: dict[str, int] = {}
    for player_id in player_ids:
        played = set(scored_weeks(history, player_id, through))
        statuses = report.get(player_id, {})
        counts[player_id] = sum(1 for week in range(1, through + 1)
                                if week not in played and statuses.get(week))
    return counts
