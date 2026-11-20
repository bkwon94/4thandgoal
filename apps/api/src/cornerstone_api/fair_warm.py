"""
The fair warm-up of the API: a worker thread that asks the fair question of each Value offer of every team pair before
a press, so a press reads the answers from the fair cache (decision 19). It asks again only after a change.
"""
import logging
import threading
import time
from collections.abc import Mapping

from analyzer.fair_cache import FairCache
from analyzer.finder_search import warm_fair
from analyzer.jev_waves import PACER, JevWaves, Pacer
from analyzer.routes import Served
from league.jev_port import Jev
from league.snapshot import Snapshot

log = logging.getLogger(__name__)

# The worker looks at the live snapshot of each client this often, even with no change seen. A new chart week or a
# waiver move shows there. A press and the Trade Wire wake it at once.
REWARM_SECONDS = 15 * 60
# The price of Jev: $0.042 per million input tokens, and its output is free (docs.typesafe.ai/models.md).
JEV_USD_PER_TOKEN = 0.042 / 1_000_000
# The clients whose fair answers the worker warms. Brian chose cpc only on 2026-11-20: Deadline week is for cpc only, a
# warm-up of cpc costs about $1.46 of Jev per deploy, and norcal adds $1.72. A press of another client reads the cache
# and asks each miss live, as before.
WARM_SLUGS = ("cpc",)


def signature(snapshot: Snapshot) -> tuple:
    """What the fair keys of the snapshot rest on: the chart week and the players of each roster."""
    return snapshot.as_of.chart_week, tuple(sorted((rid, tuple(sorted(roster)))
                                                   for rid, roster in snapshot.rosters.items()))


class FairWarmer:
    """The worker of the fair cache of every client of the app.

    The worker warms each client, then sleeps until `wake` is set or REWARM_SECONDS pass. A press sets `wake` when its
    snapshot differs from the last warm-up, and the Trade Wire sets it when the trade list changes. A warm-up of the
    same rosters and chart week does nothing, so a wake with no change costs one snapshot load.
    """

    def __init__(self, served: Mapping[str, Served], cache: FairCache, jev: Jev, pacer: Pacer = PACER):
        self.served = served
        self.cache = cache
        self.jev = jev
        self.pacer = pacer
        self.wake = threading.Event()
        # The signature of the last warm-up of each client, by slug.
        self._signatures: dict[str, tuple] = {}
        # The trade ids of the last Trade Wire answer of each client, by slug.
        self._trades: dict[str, list[str]] = {}

    def check(self, snapshot: Snapshot) -> None:
        """Wake the worker when the snapshot of a press differs from the last warm-up of its client."""
        if signature(snapshot) != self._signatures.get(snapshot.client.slug):
            self.wake.set()

    def trades_seen(self, slug: str, trade_ids: list[str]) -> None:
        """Wake the worker when the Trade Wire of the client shows a trade list that differs from the last one."""
        if self._trades.get(slug) != trade_ids:
            self._trades[slug] = trade_ids
            self.wake.set()

    def warm(self, served: Served) -> None:
        """Warm the fair cache of one client of WARM_SLUGS from its live snapshot, unless its rosters and chart week are the same as
        at the last warm-up. The waves wait while a press is live."""
        slug = served.client.slug
        if slug not in WARM_SLUGS:
            return
        snapshot = served.sources.snapshot(served.client.values.latest_season)
        mark = signature(snapshot)
        if mark == self._signatures.get(slug):
            return
        log.info("Fair warm-up of %s started: chart week %s, %d teams", slug, snapshot.as_of.chart_week,
                 len(snapshot.rosters))
        start = time.monotonic()
        waves = JevWaves(self.jev, self.pacer, background=True)
        total, asked = warm_fair(snapshot, self.cache, waves)
        self._signatures[slug] = mark
        log.info("Fair warm-up of %s ended: %d questions, %d asked, %d held, about %d tokens, $%.4f, %.1fs", slug,
                 total, asked, total - asked, waves.input_tokens, waves.input_tokens * JEV_USD_PER_TOKEN,
                 time.monotonic() - start)

    def run(self) -> None:
        """Warm each client, then wait for a wake or REWARM_SECONDS, forever. A failed warm-up logs and the worker goes
        on, because a press asks each missing answer live."""
        while True:
            self.wake.clear()
            for slug, served in self.served.items():
                try:
                    self.warm(served)
                except Exception as error:  # noqa: BLE001 - the worker keeps running after a failed warm-up
                    # The log names only the error type, so it never holds a key.
                    log.warning("The fair warm-up of %s failed (%s)", slug, type(error).__name__)
            self.wake.wait(REWARM_SECONDS)

    def start(self) -> threading.Thread:
        """Start the worker in a daemon thread, so it never holds up a stop of the app."""
        thread = threading.Thread(target=self.run, name="fair-warm-up", daemon=True)
        thread.start()
        return thread
