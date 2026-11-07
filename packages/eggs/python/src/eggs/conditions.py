"""
The check matcher of the egg hunt: does the state that the listener sends, and the clock of the client, meet each
condition of an egg. The API checks the clock window and the weekday, and the listener sends every other condition.
"""
from datetime import datetime, time
from typing import Any

# The conditions that the API checks on the clock of the client, so the listener never sends them.
CLOCK = "clock"
WEEKDAY = "weekday"
# The trail of a tap combo: the taps A and B before the double-tap on C. Its order counts, so it must match exactly.
TRAIL = "trail"
# The short names of the days, in the order of datetime.weekday().
WEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


def _in_window(window: str, now: datetime) -> bool:
    """True when `now` is inside the window "HH:MM-HH:MM". The start is in the window and the end is not.

    An end at or before the start runs past midnight, so "23:00-00:00" is 11 PM to midnight.
    """
    start, end = (time.fromisoformat(part.strip()) for part in window.split("-"))
    at = now.time().replace(tzinfo=None)
    if start < end:
        return start <= at < end
    return at >= start or at < end


def _holds(want: Any, given: Any) -> bool:
    """True when the state that the listener sends meets one condition of the egg.

    A list in the state, such as the open states, holds the condition when it holds each value that the egg wants.
    Any other state must equal the value of the egg.
    """
    if isinstance(given, list):
        wanted = want if isinstance(want, list) else [want]
        return all(value in given for value in wanted)
    return given == want


def conditions_hold(conditions: dict[str, Any], given: dict[str, Any], now: datetime) -> bool:
    """True when each condition of an egg holds. `now` is the clock of the client, in the timezone of the client."""
    for name, want in conditions.items():
        if name == CLOCK:
            if not _in_window(str(want), now):
                return False
        elif name == WEEKDAY:
            if WEEKDAYS[now.weekday()] != str(want).lower()[:3]:
                return False
        elif name == TRAIL:
            if list(given.get(TRAIL) or []) != list(want):
                return False
        elif not _holds(want, given.get(name)):
            return False
    return True
