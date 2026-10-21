# 02: Chart fetch, read, match, and the `chart` command

**What to build:** `cornerstone chart --season 2026 --week 6` finds the week 6 chart PNG on the public site, caches it, reads it with Claude, checks the read against the guards, matches the rows to Sleeper players, and prints the table and the guard results. A second run reads from the cache and makes no network call and no Claude call.

**Blocked by:** 01 (Value facts on the sheet), for the chart values model

**Status:** ready-for-agent

- [ ] A chart module exposes a fetch, a read, and a match. The fetch takes a `fetch` callable like the nflverse download. The read takes a `read` callable like the writer takes a Claude call.
- [ ] The fetch queries the site's WordPress media API for the half-PPR redraft files and picks the file whose filename date falls on or after the Tuesday cutoff of week N and before the cutoff of week N+1. The cutoff is the trade window cutoff.
- [ ] The cache holds, per week, the PNG and the parsed JSON under one charts directory in the data cache.
- [ ] A PNG placed in the cache by hand wins. The build never overwrites or re-fetches it.
- [ ] A parsed JSON that exists is reused, so the image read runs once per week.
- [ ] If the media API or the file fetch fails and no file exists for the week, the fetch returns the newest cached chart that is 14 days old or less, else none, with a warning in both cases. It never raises.
- [ ] The read sends the PNG to Claude through the writer's client and parse path, with a structured output of header week, header date, and rows of value, name, and position. The model is the writer's model.
- [ ] Guards, all required: the header week equals the expected week; values never rise row to row; every value is a multiple of 0.5 from 0 to 100; every position is RB, WR, TE, or QB; when a parsed prior week exists, the row count is within 10 percent of it.
- [ ] A failed guard logs which guard failed, keeps the PNG, writes no parsed JSON, and yields no values.
- [ ] The match builds a key from letters only, lowercase, with a Jr, Sr, II, III, or IV suffix removed, plus the position. It runs from each league player to the chart, never the other way.
- [ ] Tests fake the fetch and the read. They cover the week-to-file pick, the hand-placed PNG, the parsed JSON reuse, the stale fallback at 14 days, the no-chart case, each guard, and the match on a suffix, periods in initials, an apostrophe, and a hyphen.
- [ ] One test marked `live` reads the real week 6 PNG with Claude and checks that the guards pass.
- [ ] `uv run pytest -q` passes.
