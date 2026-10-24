"""
Drop value and drop lines from the nflverse drop plays and the Sleeper stats, and the unlucky and lucky starters.
The fact text lives in sheet.py with the other facts.
"""
from decimal import Decimal
from typing import NamedTuple

from cornerstone.models import DropLine, DropPlay, NflverseWeek, PlayerLine, Week, sub

# The fewest points a starter must score under or over his expected points to win the unlucky or lucky award.
# A smaller gap in one game is noise, so a quiet week gives no award. The commissioner tunes it.
EXPECTED_AWARD_FLOOR = 5.0


class GapLine(NamedTuple):
    """A starter's line, with his expected points for week N and his expected gap."""
    line: PlayerLine
    roster_id: int
    expected: float
    gap: float


def _drop_value(play: DropPlay, scoring: dict[str, float]) -> Decimal:
    # Decimal keeps the sum exact: float sums drift, and the page shows two decimals.
    value = Decimal(str(scoring["rec"])) + Decimal(str(max(play.air_yards, 0))) * Decimal(str(scoring["rec_yd"]))
    # Negative air yards count as 0, but the end zone test uses the raw number.
    if _in_end_zone(play):
        value += Decimal(str(scoring["rec_td"]))
    return value


def _in_end_zone(play: DropPlay) -> bool:
    # A play with no yard line has no proof that the throw reached the end zone.
    return play.yardline_100 is not None and play.air_yards >= play.yardline_100


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
                    end_zone = sum(_in_end_zone(p) for p in plays)
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


def expected_awards(
    week: Week, nfl: NflverseWeek | None = None, picked: frozenset[str] = frozenset(),
) -> dict[str, GapLine]:
    """The unlucky and the lucky starter of week N by expected gap, keyed "unlucky" and "lucky".

    A key is absent when no starter clears EXPECTED_AWARD_FLOOR. Both are absent when the expected points are
    missing or read through the week before, because then the file holds no game of week N.
    The expected gap is his points in this league minus his expected points. The file's own points miss part
    of the league scoring, so they stay out.
    `picked` holds the Sleeper IDs that already hold an award, so one starter never wins two awards.
    """
    if nfl is None or nfl.expected is None or nfl.expected.through_week < week.week:
        return {}
    gaps = []
    for m in week.matchups:
        for side in (m.a, m.b):
            for line in side.lines:
                games = nfl.expected.players.get(line.player_id, [])
                game = next((g for g in games if g.week == week.week), None)
                if line.started and game is not None and line.player_id not in picked:
                    gaps.append(GapLine(line, side.roster_id, game.expected, sub(line.points, game.expected)))
    out = {}
    # A tie goes to the first name, so a rebuild names the same player.
    unlucky = min(gaps, key=lambda g: (g.gap, g.line.name), default=None)
    if unlucky is not None and unlucky.gap <= -EXPECTED_AWARD_FLOOR:
        out["unlucky"] = unlucky
    lucky = min(gaps, key=lambda g: (-g.gap, g.line.name), default=None)
    if lucky is not None and lucky.gap >= EXPECTED_AWARD_FLOOR:
        out["lucky"] = lucky
    return out
