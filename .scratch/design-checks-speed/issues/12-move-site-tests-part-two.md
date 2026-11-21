# 12: Move the rest of the site app tests and the script tests

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests none alone. It feeds AT-20 and AT-21.

**App:** site

**What to build:** The rest of the test files of the site app and the script tests move to the native `bun:test` calls and run on `bun test`.

**Blocked by:** 08

**Status:** done

- [x] The moved files pass on `bun test` with no `vi.` call and no `vitest` import.
- [x] The count of tests that pass equals the count before the move for these files, or the ticket names each change.
- [x] The fast site check exits 0.

**Counts:** The 29 files had 231 passing tests on Vitest: 80 in `scripts/`, 53 in `src/lib/`, and 98 in the 17 files of `src/`. They have the same 231 on `bun test`, with the same count in each file. Two new files in `apps/site/test/` add 2 tests: `reset-modules.test.ts` has 1, and `fixture-site.test.ts` has 1.

**Changes:** `bun test` has no `vi.resetModules`, so `test/reset-modules.ts` gives `resetModules()`. `src/fixtures/sites.ts` no longer imports `vitest`: `readFixtureSite` sets `process.cwd` itself and `restoreFixtureSite` puts it back, because Vitest and `bun test` both run its callers. `src/fixtures/cpc-site.ts` replaces `vi.hoisted` as an import that runs first. `bun-test-files.mjs` and the Vitest config take a file as well as a folder. `scripts/bun-test.mjs` passes `--isolate`, because Framer Motion keeps the reduced-motion value of the first file, so 42 reduced-motion tests failed without it. `bunfig.toml` does not read `isolate`, so a direct `bun test` in ticket 15 needs the flag. Two reduced-motion fixes for happy-dom: the wait of `expectShown` is 3 s, because the fade runs about 1 s in real time, and one wait throws its own error, because a failed `expect` on an element takes 17 s to format.

## Comments

The merge: `ecc13ff6` merged into `design-checks-speed` on 2026-11-20; review fixes on fix branches a to n; Judge fix round on AT-13 (evidence only).
The proof: `make check-fast BASE=main` passed at each merge, 3 green CI runs on 4d5f4d13 gave a median of 315 s, and the Judge gave PASS to AT-1 to AT-39.
Read at least 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/design-checks-speed/PRD.md, .scratch/design-checks-speed/ACCEPTANCE.md, .scratch/design-checks-speed/issues/12-move-site-tests-part-two.md.
Closes with the squash merge of the spec PR.
