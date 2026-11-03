# 04 — Finder route

**Repo:** pipeline. **Spec:** `.scratch/win-win/pipeline/PRD.md`, phase 2.

**What to build:** The site can ask the API for the top three win-win trades between two teams. A new route behind the same passphrase takes the two roster ids, counts one grade against the minute and day limits, and caches the result per pair of rosters and chart week, so a repeat is free. One Claude call writes the three reasons in one response, with the same prose checks as the analysis. When the call fails twice, the three trades stand with an empty reason, and the fairness block stands. The finder document holds the two teams, the as-of stamps, and the list; each item holds the two sides with player ids and names, the fairness block, and the reason. An empty list carries the line that no swap between these rosters is good for both. A fixture finder document is checked in and copied to the site.

**Blocked by:** 03 — Finder function and command.

**Status:** done

- [x] The route takes `asker` and `partner` roster ids, with the passphrase check of the analyze route.
- [x] A finder call counts one grade. The sixth in a minute is 429, with a test. A cached repeat does not count, with a test.
- [x] The cache key is the ordered pair of rosters and the chart week, with a test.
- [x] One Claude call writes three reasons. The prose checks run on each. A failure retries once, then each reason is empty, with a test.
- [x] The finder document shape, with the as-of stamps and the empty-list line. The fixture `tests/fixtures/api/find-response.json` is checked in.
- [x] The runbook names the route and the cache.
- [x] `make test` passes. `make lint` stays at 123 or lower.
- [x] Deploy needs Brian's `fly deploy`.

## Comments

2026-10-22: The route is `POST /find` in `src/cornerstone_api/analyzer.py`, behind the passphrase of the analyze route. The body is `season`, `asker`, and `partner`. The same roster twice or a roster not in the league is 422 with a message, and it counts no grade. The order is the cache, then one grade, then the finder, then one Claude call, then the document. The analyze route and the find route share one helper for the grade count, so both read one limit.

The cache key is `finder_cache_key` in `src/cornerstone_api/cache.py`. It holds `DOCUMENT_VERSION`, the season, the ordered pair of rosters, the chart week, the stats week, and the content hash of both rosters and records. The pair keeps its order, so the asker is in the key. The finder puts the asker's side first, and its rank breaks a tie by the asker's letter. So the document for 2 and 3 can differ from the one for 3 and 2. A fallback is not stored.

The Claude call is `write_reasons` in `src/cornerstone/finder_reasons.py`, with the rules in `prompts/finder.md` after the rubric. The prompt numbers each trade, and each fact ID starts with the trade number, because the need fact of a roster depends on the trade. Each reason goes through `trade_prose_failures`, a new public helper in `analysis.py` over the existing private checks. A reason is one sentence, and its numbers come from its cited facts or its breakdown. An empty list makes no Claude call. After two failed attempts, each reason is null, and the document flags `fallback`.

The finder document holds `season`, `trade_pair`, `trades`, `empty`, `as_of`, `fallback`, `missing`, and `stale`. Each item holds `sides` in the shape of the analyze trade sides, `fairness`, and `reason`. The `empty` key is null with trades and holds the line with none, so the shape stays the same. The empty line moved from the CLI into `finder.py` as `NO_WIN_WIN`. The fixture `tests/fixtures/api/find-response.json` is the rosters 2 and 3 run on the test chart rows, with three reasons written by hand. The copy to the site repo is for the site ticket.

2026-10-22, the fix pass after the review: After a fallback, each `reason` is null, and the fairness block stands. The document has `season` at the top level, so the site can call the analyze route per card. A reason with no cited fact fails, and the fixture test runs the fixture reasons through the real checks. The route rejects the same roster twice before the snapshot loads, and only a roster that is gone clears the teams cache. `analyze` and `write_reasons` share `call_with_retry` in `writer.py`, and both prompts share `trade_side_lines`. `finder.md` has the count, two-number, and team-name rules of `analysis.md`. New tests cover a 503 with no chart and an empty list that counts one grade and is cached.
