# 12: Move the rest of the site app tests and the script tests

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests none alone. It feeds AT-20 and AT-21.

**App:** site

**What to build:** The rest of the test files of the site app and the script tests move to the native `bun:test` calls and run on `bun test`.

**Blocked by:** 08

**Status:** ready-for-agent

- [ ] The moved files pass on `bun test` with no `vi.` call and no `vitest` import.
- [ ] The count of tests that pass equals the count before the move for these files, or the ticket names each change.
- [ ] The fast site check exits 0.
