# 06: Live Sleeper snapshot

**What to build:** A commissioner runs `cornerstone analyze` with no fixture flag and the grade reads today's league. Rosters, users, and standings come from Sleeper at request time. The NFL state gives the current week. The chart week is the trade window week from the cutoff rule. The slow sources refresh when their cache is older than a day. Every fetch takes a callable, so tests run with no network.

**Blocked by:** 02 (Schedules, depth charts, and points allowed per position)

**Status:** done

- [x] A live snapshot builder fetches rosters, users, standings, and the NFL state from Sleeper and stamps the fetch time.
- [x] The current trade window week is the one whose cutoff is the latest past cutoff. The chart for that week comes from the chart module and its per-week cache.
- [x] Season stats through the last completed week, snap and target and red-zone use, and the injury report come from the history and nflverse caches. Schedules, depth charts, and points allowed come from the ticket 02 caches.
- [x] Any slow source whose cache is older than a day refreshes before the snapshot is built. A refresh that fails leaves the old cache in place and notes it.
- [x] The as-of stamps on the snapshot hold the chart week, the stats-through week, and the rosters fetch time.
- [x] Every Sleeper and nflverse fetch in the builder takes a callable with the real download as the default.
- [x] Tests build the live snapshot with the fetches patched to the week 6 raw files and assert the chart week, the stats-through week, the stamps, the day-old refresh, and the failed-refresh note.
- [x] `cornerstone analyze` with no fixture flag and the skip-Claude flag grades a trade on the live snapshot and prints the as-of line.
- [x] `uv run pytest -q` passes with no failed test.
