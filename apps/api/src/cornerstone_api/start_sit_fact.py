"""
The Suggestion fact of Start or sit, from code facts only: the starters who cannot play and the Q starters of the Sleeper
lineup, or the next kickoff of the lineup when both counts are zero (decision 08 of front-door-lineup).
"""
from dataclasses import dataclass
from datetime import datetime

from cornerstone_api.start_sit import LiveWeek
from cornerstone_api.week_lineup import CANNOT_PLAY_STATUSES, QUESTIONABLE
from league.lineup import BENCH_SLOTS

# The id that Sleeper gives an empty starting slot.
EMPTY_SLOT = "0"


@dataclass(frozen=True)
class StartSitFact:
    """The fact text, and the next kickoff when the text names it, so the site shows the time in the browser zone."""

    text: str
    kickoff: datetime | None


def start_sit_fact(week: LiveWeek, roster_id: int) -> StartSitFact | None:
    """The fact of the Sleeper lineup of the roster, such as "1 can't play, 1 Q" or "Next kickoff Sun 1:00 PM".

    It reads the starters that the manager set in Sleeper, because the lineup by projection never starts a player who
    cannot play. An empty slot, a player who is out, and a player on a bye each count as can't play. A starter whose
    game has started is locked, so no change helps and he counts in neither part. With no matchup, or no kickoff
    ahead, the Topic has no fact.
    """
    raw = week.raw
    matchup = next((m for m in raw.matchups if m.roster_id == roster_id), None)
    if matchup is None:
        return None
    games = {team: game for game in week.kickoffs for team in (game.home, game.away)}
    slots = [slot for slot in raw.league.roster_positions if slot not in BENCH_SLOTS]
    held = list(matchup.starters or [])
    held += [EMPTY_SLOT] * (len(slots) - len(held))
    holes = questionable = 0
    kickoffs = []
    for pid in held[:len(slots)]:
        entry = raw.players.get(pid) if pid != EMPTY_SLOT else None
        if entry is None:
            holes += 1
            continue
        game = games.get(entry.get("team") or "")
        if game is not None and game.locked(week.now):
            continue
        status = entry.get("injury_status")
        if game is None or status in CANNOT_PLAY_STATUSES:
            holes += 1
            continue
        if status == QUESTIONABLE:
            questionable += 1
        kickoffs.append(game.start)
    parts = [*([f"{holes} can't play"] if holes else []), *([f"{questionable} Q"] if questionable else [])]
    if parts:
        return StartSitFact(text=", ".join(parts), kickoff=None)
    if not kickoffs:
        return None
    first = min(kickoffs)
    return StartSitFact(text=f"Next kickoff {first.astimezone(week.tz):%a %-I:%M %p}", kickoff=first)
