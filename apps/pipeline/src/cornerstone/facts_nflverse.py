"""
Drop value and drop lines from the nflverse drop plays and the Sleeper stats, the unlucky and lucky starters,
the shootouts of next week, and the leader volume ranks.
The fact text lives in sheet.py with the other facts.
"""
from collections.abc import Mapping
from decimal import Decimal
from typing import NamedTuple

from cornerstone.tunables import AWARDS_PER_PLAYER
from league.models import DropLine, DropPlay, NflverseWeek, PlayerLine, Shootout, TeamWeek, Week, sub
from league.numbers import round_half_up

# The fewest points a starter must score under or over his expected points to win the unlucky or lucky award.
# A smaller gap in one game is noise, so a quiet week gives no award. The commissioner tunes it.
EXPECTED_AWARD_FLOOR = 5.0


class GapLine(NamedTuple):
    """A starter's line, with his expected points for week N and his expected gap."""
    line: PlayerLine
    roster_id: int
    expected: float
    gap: float


# A shootout reads the last 3 games a team played, so one odd game does not decide the rate. A team with fewer
# games uses all of them.
SHOOTOUT_GAMES = 3


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
    week: Week, nfl: NflverseWeek | None, awards_held: Mapping[str, int],
) -> dict[str, GapLine]:
    """The unlucky and the lucky starter of week N by expected gap, keyed "unlucky" and "lucky".

    A key is absent when no starter clears EXPECTED_AWARD_FLOOR. Both are absent when the expected points are
    missing or read through the week before, because then the file holds no game of week N.
    The expected gap is his points in this league minus his expected points. The file's own points miss part
    of the league scoring, so they stay out.
    Each award picks its own winner, so a starter with another award can win one here too, unless he holds the cap.
    `awards_held` counts the awards each Sleeper ID already holds. They pick after the other awards, so these awards
    skip a starter who holds AWARDS_PER_PLAYER.
    """
    if nfl is None or nfl.expected is None or nfl.expected.through_week < week.week:
        return {}
    gaps = []
    for m in week.matchups:
        for side in (m.a, m.b):
            for line in side.lines:
                games = nfl.expected.players.get(line.player_id, [])
                game = next((g for g in games if g.week == week.week), None)
                capped = awards_held.get(line.player_id, 0) >= AWARDS_PER_PLAYER
                if line.started and game is not None and not capped:
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


def _recent_rate(weeks: list[TeamWeek]) -> tuple[float, int] | None:
    """The pass rate over expected over the last SHOOTOUT_GAMES games a team played, and the count of those games."""
    recent = weeks[-SHOOTOUT_GAMES:]
    plays = sum(w.plays for w in recent)
    if not plays:
        return None
    # The sums weigh each play the same, so a week with few plays does not count as much as a full one.
    # The fact shows one decimal, so the check reads the same value and never calls a "0.0" rate positive.
    return round_half_up(sum(w.pass_oe for w in recent) / plays, 1), len(recent)


def shootouts(nfl: NflverseWeek | None) -> list[Shootout]:
    """The NFL games of week N+1 where both teams have a positive recent pass rate over expected, in schedule order."""
    if nfl is None or nfl.environment is None or nfl.next_games is None:
        return []
    found = []
    for away, home in nfl.next_games:
        a, h = _recent_rate(nfl.environment.get(away, [])), _recent_rate(nfl.environment.get(home, []))
        if a is None or h is None or a[0] <= 0 or h[0] <= 0:
            continue
        found.append(Shootout(away=away, home=home, away_rate=a[0], home_rate=h[0], away_games=a[1], home_games=h[1]))
    return found


# The usage field that measures a leader's volume at each position. A QB, a K, or a DEF has none.
VOLUME_FIELDS = {"RB": "carry_share", "WR": "wopr", "TE": "wopr"}


def volume_ranks(week: Week, nfl: NflverseWeek | None, position: str) -> dict[str, tuple[int, int]]:
    """Each started player's week N volume at the position and his rank on it, by Sleeper ID.

    The rank is league wide at the position, the higher volume first. Equal volumes share a rank, and the next
    rank skips past them, as in 1, 1, 3. The name orders the list only.
    A player with no usage row for week N, or with no value in it, has no entry and takes no rank.
    """
    field = VOLUME_FIELDS.get(position)
    if field is None or nfl is None or nfl.usage is None:
        return {}
    found = []
    for m in week.matchups:
        for side in (m.a, m.b):
            for line in side.lines:
                if not line.started or line.position != position:
                    continue
                row = next((u for u in nfl.usage.get(line.player_id, []) if u.week == week.week), None)
                value = None if row is None else getattr(row, field)
                if value is not None:
                    found.append((-value, line.name, line.player_id, value))
    found.sort()
    # Standard competition rank: a player's rank is one more than the count of players with a higher volume.
    return {pid: (value, 1 + sum(other > value for *_, other in found)) for _, _, pid, value in found}
