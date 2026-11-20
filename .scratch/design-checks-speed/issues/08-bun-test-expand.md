# 08: Expand: `bun test` runs beside Vitest, and the design package moves

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-22.

**App:** site

**What to build:** `bun test` runs from the site app with the happy-dom preload and the `@` alias. One helper gives `stubGlobal` and `stubEnv`, each restored after each test. The fast site check runs Vitest on the files not yet moved and `bun test` on the moved files. The 21 test files of the design package move to the native `bun:test` calls.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] Two tests in one file prove that `stubGlobal` and `stubEnv` restore the real values for the next test.
- [ ] The fast site check runs both runners, each on its own files, and exits 0.
- [ ] The 21 test files of the design package pass on `bun test` with no `vi.` call.
- [ ] The count of tests that pass equals the count before the move for these files, or the ticket names each change.
