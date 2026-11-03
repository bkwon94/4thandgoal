# 01 — Schedule fetch

**What to build:** a build saves the remaining regular-season pairings with the week's raw data, so
the odds engine can replay any week from the cache alone. The week fetch calls the matchups endpoint
once per week from N+2 to 14 and saves the pairings as one raw file, `schedule.json`. The file holds
one entry per week with the roster id and matchup id of each row, nothing else. A fetch for week 12
saves one week. A fetch for week 13 or 14 saves an empty list. Past weeks never need the file, so a cached
week without it still parses.

Spec: `.scratch/stakes/pipeline/PRD.md`, "The schedule".

**Blocked by:** None — can start immediately.

**Status:** done

- [x] The week fetch saves `schedule.json` beside the other raw files, keyed by week, weeks N+2 to 14.
- [x] Each entry keeps `roster_id` and `matchup_id` only. Points and lineups are dropped.
- [x] A fetch for week 13 or 14 saves an empty file, and a fetch for week 12 saves one week.
- [x] The parse of a cached week with no `schedule.json` still works, so old weeks and the history load as before.
- [x] A parsed week exposes the remaining pairings as a list of pairs per week, in the same shape as the next-week pairs.
- [x] The week 6 test fixture gains a `schedule.json` built from the live data of 2026-10-23, weeks 8 to 14.
- [x] Tests: the fetch saves the file from a fake client; the week 14 case is empty; the parse of the fixture gives 7 weeks of 6 pairs.
- [x] Ruff clean, the full suite passes.
