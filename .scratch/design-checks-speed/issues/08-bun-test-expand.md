# 08: Expand: `bun test` runs beside Vitest, and the design package moves

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-22.

**App:** site

**What to build:** `bun test` runs from the site app with the happy-dom preload and the `@` alias. One helper gives `stubGlobal` and `stubEnv`, each restored after each test. The fast site check runs Vitest on the files not yet moved and `bun test` on the moved files. The 21 test files of the design package move to the native `bun:test` calls.

**Blocked by:** 02

**Status:** in-review

- [x] Two tests in one file prove that `stubGlobal` and `stubEnv` restore the real values for the next test.
- [x] The fast site check runs both runners, each on its own files, and exits 0.
- [x] The 21 test files of the design package pass on `bun test` with no `vi.` call.
- [x] The count of tests that pass equals the count before the move for these files, or the ticket names each change.

**Counts:** The 21 files had 162 passing tests on Vitest. They have 162 passing tests on `bun test`, with the same count in each file. Two new files in `apps/site/test/` add 3 tests: `stubs.test.ts` has 2 for the stub helper (AT-22), and `dom.test.ts` has 1 for the canceled animation of happy-dom.

**Changes:** The helper sits in `apps/site/test/stubs.ts`, not in a package, because the component rule bans `process.env` in each package file. The three design files that stubbed `matchMedia` use `spyOn` of `bun:test` instead. The preload restores each spy and each stub after each test.
