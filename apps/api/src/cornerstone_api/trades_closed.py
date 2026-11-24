"""
Trades closed: the state of a client from its Lock onward. One pure function of the Lock and the time, so a test sets
the time and never waits for a date.
"""
from datetime import datetime


def trades_closed(lock: datetime | None, now: datetime) -> bool:
    """True at or after the Lock. A client with no Lock is never closed."""
    return lock is not None and now >= lock
