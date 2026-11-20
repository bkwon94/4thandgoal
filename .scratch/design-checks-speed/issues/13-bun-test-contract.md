# 13: Contract: Vitest goes away

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-19, AT-20, AT-21, AT-25, and AT-35.

**App:** site

**What to build:** No test runs on Vitest. Vitest, its config, and its dependency go away. The site unit check runs `bun test` alone. The full count of tests that pass equals 1,775 plus or minus each named change. pnpm stays the installer, and no locked version changes.

**Blocked by:** 09, 10, 11, and 12

**Status:** ready-for-agent

- [ ] The site unit check runs `bun test` and exits 0.
- [ ] No `package.json` names `vitest`, and the Vitest config does not exist.
- [ ] No site test file holds a `vi.` call or a `vitest` import.
- [ ] The `bun test` pass count equals 1,775 plus or minus each named change, with no skipped test.
- [ ] The lock diff changes no version that `main` locks, and no `bun.lock` exists.
- [ ] ADR 0038 is in the ADR index.
