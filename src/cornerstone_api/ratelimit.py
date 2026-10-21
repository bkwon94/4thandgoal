"""
The per-address rate limit of the API, in memory: a fixed window of one minute per client address.
The service runs as one process, so memory is enough, and a restart clears every count.
"""
import math
import time
from collections.abc import Callable

WINDOW_SECONDS = 60
# The most addresses the map holds before it drops the expired windows, so a flood of new addresses cannot fill memory.
MAX_TRACKED_ADDRESSES = 10_000


class RateLimiter:
    """Count the requests of each address in its current window."""

    def __init__(self, limit: int, clock: Callable[[], float] = time.monotonic) -> None:
        self.limit = limit
        self.clock = clock
        # The start of the current window and the count in it, by address.
        self.windows: dict[str, tuple[float, int]] = {}

    def hit(self, address: str) -> int | None:
        """Count one request. Return None when it is within the limit, else the seconds until the window ends."""
        now = self.clock()
        start, count = self.windows.get(address, (now, 0))
        if now - start >= WINDOW_SECONDS:
            start, count = now, 0
        if count >= self.limit:
            return max(1, math.ceil(start + WINDOW_SECONDS - now))
        self.windows[address] = (start, count + 1)
        # Old windows go when the map grows, so a stream of new addresses cannot fill the memory.
        if len(self.windows) > MAX_TRACKED_ADDRESSES:
            self.windows = {a: w for a, w in self.windows.items() if now - w[0] < WINDOW_SECONDS}
        return None
