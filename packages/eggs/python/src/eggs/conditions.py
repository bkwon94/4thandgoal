"""
The check matcher of the egg hunt: does the state that the listener sends, and the clock of the client, meet each
condition of an egg. The API checks the clock window and the weekday, and the listener sends every other condition.
"""
import re
from datetime import datetime, time
from typing import Any

# The conditions that the API checks on the clock of the client, so the listener never sends them.
CLOCK = "clock"
WEEKDAY = "weekday"
# The trail of a tap combo: the taps A and B before the double-tap on C. Its order counts, so it must match exactly.
TRAIL = "trail"
# The actions that the listener sends: a double-tap, a press of 2 seconds or more, and a selected word.
ACTIONS = ("tap2", "hold", "select")
# The two teams of an analyzer trade, as two roster ids. Any trade between exactly those two teams matches, in either
# direction and with any players. The listener derives them from the trade key on the root of the analyzer result.
TRADE_TEAMS = "trade_teams"
# The exact trade key of the first catalog. The drop refuses it, because the listener sends the two teams instead.
OLD_TRADE = "trade"
# The 404 page. An egg with not_found = true matches on the 404 page of any missing URL, so it holds no page of its own.
NOT_FOUND = "not_found"
# The one page of every 404 egg, and of every check from the 404 page. No real path starts with "*".
NOT_FOUND_PAGE = "*404"
# The short names of the days, in the order of datetime.weekday().
WEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
# The shape of a clock window, such as "23:00-00:00". The drop checks it, so a bad window never reaches a check.
CLOCK_WINDOW = re.compile(r"\d{2}:\d{2}-\d{2}:\d{2}")


def _in_window(window: str, now: datetime) -> bool:
    """True when `now` is inside the window "HH:MM-HH:MM". The start is in the window and the end is not.

    An end at or before the start runs past midnight, so "23:00-00:00" is 11 PM to midnight.
    """
    start, end = (time.fromisoformat(part.strip()) for part in window.split("-"))
    at = now.time().replace(tzinfo=None)
    if start < end:
        return start <= at < end
    return at >= start or at < end


def egg_page(page: str, conditions: dict[str, Any]) -> str:
    """The page that an egg or a check names: NOT_FOUND_PAGE for the 404 page, else the page itself.

    Any missing URL shows the 404 page, so a 404 egg matches a check from the 404 page of any path.
    """
    return NOT_FOUND_PAGE if conditions.get(NOT_FOUND) is True else page


def check_action(action: str) -> None:
    """Raise ValueError when the listener never sends the action, so the drop refuses an egg that nobody can find."""
    if action not in ACTIONS:
        raise ValueError(f"The action {action!r} is not one of {', '.join(ACTIONS)}.")


def check_conditions(conditions: dict[str, Any]) -> None:
    """Raise ValueError when a condition of an egg is bad, so the drop refuses the egg: a bad clock window or weekday,
    the old trade key, a team pair that is not two roster ids, or a 404 page that is not true.

    The check of an egg reads each one on each match, so a bad value would fail every check of its target.
    """
    if OLD_TRADE in conditions:
        raise ValueError(f'The condition "{OLD_TRADE}" is gone. Name two roster ids as "{TRADE_TEAMS}".')
    if TRADE_TEAMS in conditions:
        teams = conditions[TRADE_TEAMS]
        if (not isinstance(teams, list) or len(teams) != 2 or len(set(teams)) != 2
                or not all(isinstance(team, int) and not isinstance(team, bool) for team in teams)):
            raise ValueError(f"The team pair {teams!r} is not two different roster ids.")
    if NOT_FOUND in conditions and conditions[NOT_FOUND] is not True:
        raise ValueError(f"The condition {NOT_FOUND} must be true, not {conditions[NOT_FOUND]!r}.")
    if CLOCK in conditions:
        window = conditions[CLOCK]
        if not isinstance(window, str) or CLOCK_WINDOW.fullmatch(window) is None:
            raise ValueError(f'The clock window {window!r} is not "HH:MM-HH:MM".')
        for part in window.split("-"):
            try:
                time.fromisoformat(part)
            except ValueError:
                raise ValueError(f"The clock window {window!r} holds the bad time {part!r}.") from None
    if WEEKDAY in conditions:
        day = conditions[WEEKDAY]
        if not isinstance(day, str) or day.lower() not in WEEKDAYS:
            raise ValueError(f'The weekday {day!r} is not one of "mon" to "sun".')


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
        elif name == TRADE_TEAMS:
            # Exactly the two teams, in either order, so a trade of three teams is no match.
            if sorted(given.get(TRADE_TEAMS) or []) != sorted(want):
                return False
        elif not _holds(want, given.get(name)):
            return False
    return True
