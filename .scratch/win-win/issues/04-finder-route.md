# 04 — Finder route

**Repo:** pipeline. **Spec:** `.scratch/win-win/PRD.md`, phase 2.

**What to build:** The site can ask the API for the top three win-win trades between two teams. A new route behind the same passphrase takes the two roster ids, counts one grade against the minute and day limits, and caches the result per pair of rosters and chart week, so a repeat is free. One Claude call writes the three reasons in one response, with the same prose checks as the analysis. When the call fails twice, the three trades stand with the code's fairness reasons. The finder document holds the two teams, the as-of stamps, and the list; each item holds the two sides with player ids and names, the fairness block, and the reason. An empty list carries the line that no swap between these rosters is good for both. A fixture finder document is checked in and copied to the site.

**Blocked by:** 03 — Finder function and command.

**Status:** ready-for-agent

- [ ] The route takes `asker` and `partner` roster ids, with the passphrase check of the analyze route.
- [ ] A finder call counts one grade. The sixth in a minute is 429, with a test. A cached repeat does not count, with a test.
- [ ] The cache key is the ordered pair of rosters and the chart week, with a test.
- [ ] One Claude call writes three reasons. The prose checks run on each. A failure retries once, then the code reasons stand, with a test.
- [ ] The finder document shape, with the as-of stamps and the empty-list line. The fixture `tests/fixtures/api/find-response.json` is checked in.
- [ ] The runbook names the route and the cache.
- [ ] `make test` passes. `make lint` stays at 123 or lower.
- [ ] Deploy needs Brian's `fly deploy`.
