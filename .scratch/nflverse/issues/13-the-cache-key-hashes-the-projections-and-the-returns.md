# 13 — The cache key hashes the projections and the returns

Spec: `.scratch/nflverse/PRD.md`, "The trade rubric". Found in the ticket 10 review on 2026-10-24.

**What to build:** `cache_key` in `src/cornerstone_api/cache.py` hashes the trade, the two rosters, the two
records, the chart week, the stats week, and `DOCUMENT_VERSION`. It does not hash the projections ahead or the
returns file. Inside a week, a change in either file does not clear a cached grade, so a player whose return
week moves keeps his old lineup value until the week turns. `_content_hash` gains the projections ahead and the
return week of every player on the two rosters. The finder key shares `_content_hash`, so it gains them too.

**Why:** `DOCUMENT_VERSION` covers a deploy only. A new injuries file lands daily and changes return weeks.

**Blocked by:** None.

**Status:** open

- [x] Two snapshots that differ only in one rostered player's return week give two different keys.
- [x] Two snapshots that differ only in one rostered player's projection ahead give two different keys.
- [x] A change to a player on neither roster leaves the key the same.
- [x] Every existing cache test passes unchanged.
