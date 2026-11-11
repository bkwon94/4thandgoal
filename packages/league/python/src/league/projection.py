"""
The projections of one player from the projections ahead by week: the week N+1 projection and the rest of season sum.
The waiver board and the waiver targets of the API read them, so both sum a player the same way.
"""
from league.client import Client
from league.models import ProjectionsAhead
from league.numbers import r2


def next_week(ahead: ProjectionsAhead, player_id: str, week: int) -> float:
    """The projection of week N+1 after week `week`. A player with none, such as on a bye, gets 0."""
    return r2(ahead.get(week + 1, {}).get(player_id, 0.0))


def rest_of_season(ahead: ProjectionsAhead, player_id: str, week: int, client: Client) -> float:
    """The sum of the projections of weeks N+1 to the last season week of `client`.

    A week with no projection, such as his bye, counts 0.
    """
    last = client.settings.last_season_week
    return r2(sum(ahead.get(w, {}).get(player_id, 0.0) for w in range(week + 1, last + 1)))
