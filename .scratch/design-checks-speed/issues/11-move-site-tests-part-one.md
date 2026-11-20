# 11: Move the first half of the site app tests

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests none alone. It feeds AT-20 and AT-21.

**App:** site

**What to build:** About half of the 82 test files of the site app, the front door and its neighbors, move to the native `bun:test` calls and run on `bun test`. A test that depends on jsdom gets a fix for happy-dom, or the ticket names it for Brian.

**Blocked by:** 08

**Status:** ready-for-agent

- [ ] The moved files pass on `bun test` with no `vi.` call and no `vitest` import.
- [ ] The count of tests that pass equals the count before the move for these files, or the ticket names each change.
- [ ] The fast site check exits 0.
