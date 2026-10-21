# 08: The FastAPI app

**What to build:** A manager with the passphrase posts a proposed trade to the analyze route and gets the result document the site renders. A teams route lists the league's teams with their players, positions, NFL teams, and headshot URLs for the form. A health route needs no passphrase. A wrong passphrase is 401. A player not on the giving roster is 422. A repeat of the same trade is a cache hit with no Claude call. Past the rate limit the route returns 429. The app lives in its own package beside the pipeline, with one module per route group, so a live page group lands beside the analyzer later with no refactor.

**Blocked by:** 06 (Live Sleeper snapshot), 07 (The Claude call)

**Status:** done

- [x] FastAPI and an ASGI server join the dependencies. The app package sits beside the pipeline package with one module per route group. The analyzer is the first group.
- [x] Routes: health; teams with players, positions, NFL teams, and headshot URLs; analyze, which takes the proposed trade and returns the result document.
- [x] Every route except health reads the passphrase from a request header. A wrong or missing passphrase returns 401 with no body. The passphrase comes from the environment.
- [x] A per-address rate limit in memory, with the limit in the tunable table. Past the limit the route returns 429 with a retry-after header.
- [x] The result cache key is the sorted players per side, the roster ids, the asker, and the as-of stamps. A hit returns the stored document with no Claude call. The cache lives on disk under a directory from the environment, so it survives a restart.
- [x] CORS allows the production site origin and localhost.
- [x] The result document holds the proposed trade echoed with names and headshots, per side the start letter, each adjuster with its step and reason, the final letter, and the analysis, the verdict with its reason, and the as-of stamps. No chart value, sum, ratio, or chart name.
- [x] A fixture response document is checked in under the test fixtures directory. The route test asserts the live route's output has the fixture's shape.
- [x] The Sleeper fetch and the slow-source fetchers are patched to callables in the route tests. The analyzer is injected: a stub, or the real analyzer with a fake Claude callable.
- [x] Route tests: a good request returns the document in the fixture's shape; a wrong passphrase is 401; a missing passphrase is 401; a player not on the giving roster is 422 with the id; a repeat is a cache hit with one Claude call total; the rate limit returns 429; a Claude letter two steps off falls back; health needs no passphrase.
- [x] The weekly build and the Tuesday job do not change.
- [x] `uv run pytest -q` passes with no failed test.

## Comments

- The result document carries three fields the PRD did not list: `lean` per adjuster, `final_reason` per side, and `verdict.differs`.
- The `/teams` route needs a `season` query parameter.
- The passphrase header is `X-League-Passphrase`.
- Ticket 09 copies the response fixture, so it reads these three fields from the fixture.
- The Claude analyzer is connected: the default analyzer is `cornerstone.analysis.analyze`, and the service needs `ANTHROPIC_API_KEY`.
