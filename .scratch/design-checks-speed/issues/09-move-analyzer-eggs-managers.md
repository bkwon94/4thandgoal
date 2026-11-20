# 09: Move the tests of analyzer, eggs, and managers

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests none alone. It feeds AT-20 and AT-21.

**App:** site

**What to build:** The 40 test files of the analyzer, eggs, and managers packages move to the native `bun:test` calls and run on `bun test`.

**Blocked by:** 08

**Status:** in-review

- [ ] The 40 files pass on `bun test` with no `vi.` call and no `vitest` import.
- [x] The count of tests that pass equals the count before the move for these files, or the ticket names each change.
- [x] The fast site check exits 0.

**Counts:** 36 of the 40 files moved. The counts match for the moved files: analyzer 170 before and 170 after, eggs 129 and 129, managers 58 and 58. `bun test` of the site app now passes 522 tests in 59 files. Vitest had 261 for the whole analyzer package, and 69 for managers.

**Not moved:** four files stay on Vitest, because happy-dom under `bun test` hangs or flakes on each one. `analyzer/site/form/trade-form.test.tsx` hangs on frame timers. `analyzer/site/form/analyzer.test.tsx` takes 30 s in `getByRole` and fails. `managers/site/page/grade-popover.test.tsx` times out at the Escape test. `managers/site/page/motion.test.tsx` fails by timing on the frame loop. They wait for the happy-dom fixes in the preload.

**Changes:** `scripts/bun-test.mjs` runs `bun test --isolate`, because Framer Motion reads `matchMedia` once per module. An entry of `BUN_TEST_DIRS` can be one file, and the Vitest config skips the file and the folder. Six test files needed small happy-dom fixes: page address, scroll, layout, same-origin check, and accessible names.
