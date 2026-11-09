"""
Read the nflverse team stats file: the offense of each NFL team as expected points added per play, with its rank.
The Advisor reads it to tell a player on a bad offense from a player on a good one.
"""
from pathlib import Path

from pydantic import BaseModel

from league.nflverse_rows import _number, _rows, _sleeper_team


class TeamOffense(BaseModel):
    """The offense of one NFL team over its regular-season games."""
    games: int
    # The sum of the passing and rushing expected points added, over the dropbacks and the carries.
    epa_per_play: float
    # 1 is the offense with the most expected points added per play. Equal values share a rank.
    rank: int


def read_team_stats(path: Path, through: int) -> dict[str, TeamOffense] | None:
    """The offense of each team in weeks 1 to `through`, by Sleeper team code. None when the file has no such row.

    A dropback is a pass attempt or a sack. The passing expected points include the sacks, so the plays match.
    """
    games: dict[str, int] = {}
    epa: dict[str, float] = {}
    plays: dict[str, float] = {}
    for row in _rows(path):
        if row["season_type"] != "REG" or not row["week"].isdigit() or not 1 <= int(row["week"]) <= through:
            continue
        team = _sleeper_team(row["team"])
        games[team] = games.get(team, 0) + 1
        epa[team] = epa.get(team, 0.0) + _number(row["passing_epa"]) + _number(row["rushing_epa"])
        plays[team] = plays.get(team, 0.0) + _number(row["attempts"]) + _number(row["sacks_suffered"]) + _number(
            row["carries"])
    per_play = {team: epa[team] / plays[team] for team in games if plays[team]}
    if not per_play:
        return None
    return {team: TeamOffense(games=games[team], epa_per_play=value,
                              rank=1 + sum(other > value for other in per_play.values()))
            for team, value in per_play.items()}
