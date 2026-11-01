"""
A Sleeper player ID tells two things: whether the player is a DEF, and the URL of its headshot.
The page writer and the API both read it, so it is in the model layer with the player models.
"""


def is_def(player_id: str) -> bool:
    """Whether a player ID is a DEF.
    Sleeper gives a DEF the team abbreviation as its player ID, and a player a numeric ID."""
    return not player_id.isdigit()


def headshot_url(player_id: str, is_def: bool) -> str:
    """The Sleeper CDN URL for a player's headshot.
    A DEF has no headshot, and its player ID is the team abbreviation, so it maps to the team logo."""
    if is_def:
        return f"https://sleepercdn.com/images/team_logos/nfl/{player_id.lower()}.png"
    return f"https://sleepercdn.com/content/nfl/players/{player_id}.jpg"
