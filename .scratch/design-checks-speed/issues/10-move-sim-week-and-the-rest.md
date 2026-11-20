# 10: Move the tests of sim, week, midseason, league, waiver, and rankings

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests none alone. It feeds AT-20 and AT-21.

**App:** site

**What to build:** The 40 test files of the sim, week, midseason, league, waiver, and rankings packages move to the native `bun:test` calls and run on `bun test`.

**Blocked by:** 08

**Status:** ready-for-agent

- [x] The 40 files pass on `bun test` with no `vi.` call and no `vitest` import.
- [x] The count of tests that pass equals the count before the move for these files, or the ticket names each change.
- [x] The fast site check exits 0.
