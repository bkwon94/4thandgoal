"""
Drop value and drop lines from the nflverse drop plays and the Sleeper stats.
The fact text lives in sheet.py with the other facts.
"""
from decimal import Decimal

from cornerstone.models import DropLine, DropPlay, NflverseWeek, Week


def _drop_value(play: DropPlay, scoring: dict[str, float]) -> Decimal:
    # Decimal keeps the sum exact: float sums drift, and the page shows two decimals.
    value = Decimal(str(scoring["rec"])) + Decimal(str(max(play.air_yards, 0))) * Decimal(str(scoring["rec_yd"]))
    # A negative air yards count as 0, but the end zone test uses the raw number.
    if play.air_yards >= play.yardline_100:
        value += Decimal(str(scoring["rec_td"]))
    return value


def drop_value(play: DropPlay, scoring: dict[str, float]) -> float:
    """What the catch would have scored: one reception, the air yards, and a touchdown in the end zone."""
    return float(_drop_value(play, scoring))


def drop_lines(week: Week, nfl: NflverseWeek | None = None) -> list[DropLine]:
    """Started lines with 1 or more drops, most drops first, then most value, then name."""
    nflverse_up = nfl is not None and nfl.drops is not None
    found = []
    for m in week.matchups:
        for side in (m.a, m.b):
            for line in side.lines:
                if not line.started:
                    continue
                stats = week.stats.get(line.player_id, {})
                targets = stats.get("rec_tgt")
                if nflverse_up:
                    plays = nfl.drops.get(line.player_id, [])
                    count = len(plays)
                    value = float(sum((_drop_value(p, week.scoring) for p in plays), Decimal(0)))
                    end_zone = sum(p.air_yards >= p.yardline_100 for p in plays)
                else:
                    count = int(stats.get("rec_drop", 0))
                    value = end_zone = None
                if count < 1:
                    continue
                found.append((line.name, DropLine(
                    player_id=line.player_id, roster_id=side.roster_id, matchup_id=m.matchup_id,
                    drops=count, targets=None if targets is None else int(targets),
                    value=value, end_zone=end_zone)))
    found.sort(key=lambda x: (-x[1].drops, -(x[1].value or 0), x[0]))
    return [d for _, d in found]
