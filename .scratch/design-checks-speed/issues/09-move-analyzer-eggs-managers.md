# 09: Move the tests of analyzer, eggs, and managers

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests none alone. It feeds AT-20 and AT-21.

**App:** site

**What to build:** The 40 test files of the analyzer, eggs, and managers packages move to the native `bun:test` calls and run on `bun test`.

**Blocked by:** 08

**Status:** ready-for-agent

- [ ] The 40 files pass on `bun test` with no `vi.` call and no `vitest` import.
- [ ] The count of tests that pass equals the count before the move for these files, or the ticket names each change.
- [ ] The fast site check exits 0.
