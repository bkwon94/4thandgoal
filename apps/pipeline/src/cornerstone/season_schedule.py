"""
The head-to-head pairs of each regular week left after a saved week, from the saved raw data of that week.
The look ahead of the midseason report takes them through its port. The League settings set the last regular week.
"""
from league.client import Client
from league.parse import parse_week
from league.paths import raw_dir
from league.provider.sleeper import load_raw

Pair = tuple[int, int]


def remaining_schedule(season: int, week: int, *, client: Client) -> dict[int, list[Pair]]:
    """The pairs of weeks `week` + 1 to the last regular week, by week. The playoff weeks stay out."""
    raw = load_raw(raw_dir(client.folder, season, week))
    parsed = parse_week(raw, week=week, team_count=client.settings.team_count, points_key=client.settings.points_key)
    last = client.settings.last_regular_week
    # The next week's pairs sit apart from the schedule of the later weeks in the parsed week.
    pairs = {week + 1: list(parsed.next_matchups)} if week < last else {}
    pairs.update({number: list(games) for number, games in parsed.schedule.items() if week < number <= last})
    return pairs
