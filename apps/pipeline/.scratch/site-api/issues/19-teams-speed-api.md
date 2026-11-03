# 19: The teams route answers fast

**What to build:** The `/teams` route answers from an in-process cache for about 5 minutes per season, so the analyzer form fills at once. The Fly machine stays warm. On start, the service warms the slow sources in the background, so the first request after a deploy finds them on the volume. This ticket takes over the build items of ticket 12.

**Why:** The commissioner sees "Loading teams" for many seconds on an almost blank page. Today each `/teams` request builds a full live snapshot: a Sleeper fetch, the slow source refresh, and a history save.

**Blocked by:** 17 (both touch `src/cornerstone_api/analyzer.py` and `app.py`).

**Status:** done

- [x] `TEAMS_CACHE_SECONDS = 300` in `src/cornerstone/tunables.py`, with the reason.
- [x] `/teams` keeps its last answer per season in memory with the time it was built. Within the window it answers from memory. Past it, it builds again. A refresh by the cron is never blocked by this cache and never waits on it.
- [x] `/teams` never waits on the chart or the schedule downloads it does not use. Check what `live_snapshot` with `read_chart=None` still fetches, and skip what the rosters do not need.
- [x] On app start, a background thread runs the sources refresh with the normal `max_age_seconds`, so a fresh volume or a deploy pays the downloads before the first request. A failure logs a warning and never stops the app.
- [x] `fly.toml` sets `min_machines_running = 1`. The runbook notes the cost: one shared-cpu-1x machine with 1 GB, about $6 per month at Fly list price. Check the current price and write the real number. The real number is $6.70 per month in `ewr`, from the Fly pricing page on 2026-10-21.
- [x] Tests with the sources patched: the second `/teams` within the window does not call the sources; a call past the window does; the start-up warm runs once and a raised error does not stop the app.
- [x] The runbook names the teams cache and the start-up warm.
- [x] After the deploy on 2026-10-21: a cold `/health` on the stopped machine took 4.6 seconds, then the machine stayed on. A warm `/teams` is Brian's measure from the browser. Ticket 12 closes with this.
- [x] `uv run pytest -q` passes with no failed test.
- [x] Deployed 2026-10-21, main `faff426`.
