"""
The nickname of each NFL team by its Sleeper code, such as "Titans" for TEN.
The text of the grade names a team this way, as in "on the Titans depth chart".
"""

# The Sleeper codes and the last names of the 32 team defenses in the Sleeper players file.
NFL_TEAM_NAMES: dict[str, str] = {
    "ARI": "Cardinals", "ATL": "Falcons", "BAL": "Ravens", "BUF": "Bills", "CAR": "Panthers", "CHI": "Bears",
    "CIN": "Bengals", "CLE": "Browns", "DAL": "Cowboys", "DEN": "Broncos", "DET": "Lions", "GB": "Packers",
    "HOU": "Texans", "IND": "Colts", "JAX": "Jaguars", "KC": "Chiefs", "LAC": "Chargers", "LAR": "Rams",
    "LV": "Raiders", "MIA": "Dolphins", "MIN": "Vikings", "NE": "Patriots", "NO": "Saints", "NYG": "Giants",
    "NYJ": "Jets", "PHI": "Eagles", "PIT": "Steelers", "SEA": "Seahawks", "SF": "49ers", "TB": "Buccaneers",
    "TEN": "Titans", "WAS": "Commanders",
}


def team_name(code: str) -> str:
    """The nickname of the team, or the code itself for a code not in the map."""
    return NFL_TEAM_NAMES.get(code, code)
