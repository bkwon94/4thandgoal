# 09: Move the tests of analyzer, eggs, and managers

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests none alone. It feeds AT-20 and AT-21.

**App:** site

**What to build:** The 40 test files of the analyzer, eggs, and managers packages move to the native `bun:test` calls and run on `bun test`.

**Blocked by:** 08

**Status:** done

- [x] The 40 files pass on `bun test` with no `vi.` call and no `vitest` import.
- [x] The count of tests that pass equals the count before the move for these files, or the ticket names each change.
- [x] The fast site check exits 0.

**Counts:** All 40 files moved. The counts match for each file: analyzer 170 before and 170 after for the first 36 files, eggs 129 and 129, managers 58 and 58. The last four files kept their counts: `trade-form.test.tsx` 72 and 72, `analyzer.test.tsx` 19 and 19, `grade-popover.test.tsx` 7 and 7, `motion.test.tsx` 4 and 4.

**Not moved:** none. All 40 files run on Bun, and Vitest runs none of them.

**Changes:** `scripts/bun-test.mjs` runs `bun test --isolate`, because Framer Motion reads `matchMedia` once per module. An entry of `BUN_TEST_DIRS` can be one file, and the Vitest config skips the file and the folder. Six test files needed small happy-dom fixes: page address, scroll, layout, same-origin check, and accessible names.

**Changes of the last four files:** `trade-form.test.tsx` and `analyzer.test.tsx` use `mock` and `spyOn(globalThis, "fetch")`. `trade-form.test.tsx` has its own `fakeTimeouts()` clock for `setTimeout` and `clearTimeout`, because `jest.useFakeTimers` of `bun:test` drops each timer that is pending when it ends, and has no `advanceTimersByTimeAsync`. `motion.test.tsx` removes `IntersectionObserver` in `beforeEach`, because happy-dom never reports an entry and a reveal that waits for the viewport never plays. `grade-popover.test.tsx` needed only the import. `form-steps.ts` no longer imports `vitest`, because a Vitest file and a `bun test` file both use it. The preload keeps its frame timer on the `setTimeout` of load, so a test that fakes `setTimeout` cannot stall the frame loop. `test/dom.test.ts` proves it. `bun-test-files.mjs` now lists the folders `packages/analyzer/site/form` and `packages/managers/site/page`.

## Comments

The merge: `26a72381` merged into `design-checks-speed` on 2026-11-20; review fixes on fix branches a to n; Judge fix round on AT-13 (evidence only).
The proof: `make check-fast BASE=main` passed at each merge, 3 green CI runs on 4d5f4d13 gave a median of 315 s, and the Judge gave PASS to AT-1 to AT-39.
Read at least 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/design-checks-speed/PRD.md, .scratch/design-checks-speed/ACCEPTANCE.md, .scratch/design-checks-speed/issues/09-move-analyzer-eggs-managers.md.
Closes with the squash merge of the spec PR.
