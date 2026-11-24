"""
Trades closed: the state of a client from its Lock onward. One pure function of the Lock and the time, so a test sets
the time and never waits for a date. The closed reply and the check of a client sit here too.
"""
from datetime import UTC, datetime

from analyzer.values import AnalyzerValues
from league.client import Client

# The line of the closed reply. The site shows the same words, so a change here changes the page.
CLOSED_LINE = "The trade deadline has passed. Trades open again next season."
CLOSED_BODY = {"closed": True, "line": CLOSED_LINE}
# The routes that grade, find, or list trades, as the path under /clients/<slug>. A client that is closed refuses each
# of them with the closed reply. /teams stays open, because the pages still list the teams.
TRADE_ROUTES = frozenset({"/analyze", "/find", "/trade-check", "/trade-ideas", "/find-stream", "/sell-high",
                          "/deadline/trades"})


def trades_closed(lock: datetime | None, now: datetime) -> bool:
    """True at or after the Lock. A client with no Lock is never closed."""
    return lock is not None and now >= lock


def wall_clock() -> datetime:
    """The time now. A test sets this one function, so no test waits for a date."""
    return datetime.now(UTC)


def client_closed(client: Client) -> bool:
    """True when the Lock of `client` has passed. A client with no analyzer package has no Lock, so it is never closed."""
    values = client.values.package_values.get(AnalyzerValues.package)
    return isinstance(values, AnalyzerValues) and trades_closed(values.lock, wall_clock())
