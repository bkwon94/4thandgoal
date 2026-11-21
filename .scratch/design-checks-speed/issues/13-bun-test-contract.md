# 13: Contract: Vitest goes away

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-19, AT-20, AT-21, AT-25, and AT-35.

**App:** site

**What to build:** No test runs on Vitest. Vitest, its config, and its dependency go away. The site unit check runs `bun test` alone. The full count of tests that pass equals 1,775 plus or minus each named change. pnpm stays the installer, and no locked version changes.

**Blocked by:** 09, 10, 11, and 12

**Status:** in-review

- [x] The site unit check runs `bun test` and exits 0.
- [x] No `package.json` names `vitest`, and the Vitest config does not exist.
- [x] No site test file holds a `vi.` call or a `vitest` import.
- [x] The `bun test` pass count equals 1,775 plus or minus each named change, with no skipped test.
- [x] The lock diff changes no version that `main` locks, and no `bun.lock` exists.
- [x] ADR 0038 is in the ADR index.

**Counts:** `bun test` passes 1,808 tests in 193 files, with no skip and no fail. Vitest passed 1,775 tests in 183 files at the base of the Spec branch (ticket 08). The math: 1,775 − 5 + 38 = 1,808, and 183 − 1 + 11 = 193 files. Each moved file keeps its Vitest count.

**Count after ticket 15:** Ticket 15 adds `apps/site/scripts/test-scope.test.mjs`, with 14 tests in 1 file. The total is 1,808 + 14 = 1,822 tests in 193 + 1 = 194 files.

| Ticket | Test file | Change |
| --- | --- | --- |
| 01 | `src/ui-sdk-rule.test.ts`, removed (ADR 0035 rule test) | −5 |
| 01 | `src/design-rules.test.ts` | +2 |
| 03 | `scripts/typecheck.test.mjs` | +3 |
| 04 | `src/design-rule-no-raw-element.test.ts` | +4 |
| 05 | `src/design-rule-raw-color.test.ts` | +2 |
| 06 | `src/value-rule.test.ts` | +5 |
| 07 | `src/use-lines-rule.test.ts` | +4 |
| 08 | `test/stubs.test.ts` | +2 |
| 08 | `test/dom.test.ts`: the canceled animation | +1 |
| 09 to 12 | `test/dom.test.ts`: the frame rate, one time per frame, the page URL, the Storage spy, and the short print of a node (commit `b823ab82`, the preload fix of the move tickets) | +5 |
| 09 | `test/dom.test.ts`: the frames run when a test fakes `setTimeout` | +1 |
| 12 | `test/reset-modules.test.ts` and `test/fixture-site.test.ts` | +2 |
| 13 | `test/dom.test.ts`: the web stream classes | +1 |
| 16 | `scripts/playwright-shard.test.mjs` | +6 |

The two test files under `packages/design/lint/fixtures/` are lint fixtures, and no runner runs them.

**The last 6 files:** `page-free` 25 and 25, `page-personal` 27 and 27, `page-grade-blocks` 2 and 2, `page-suggestions` 17 and 17, `page-topic-sweep` 32 and 32, and `design-rule-no-raw-element` 4 and 4, on Vitest and on `bun test`.

**The cause of the stream fault:** happy-dom 21.0.4 sets `window.TransformStream = Stream.Transform` and `window.WritableStream = Stream.Writable`, the Node stream classes, in `lib/window/BrowserWindow.js`. They are not web streams, so the native `pipeThrough` of Bun refuses them. The preload keeps the native web stream classes of Bun, and `test/dom.test.ts` proves it. With the two restore lines off, the 4 personal Topics of `page-topic-sweep` fail in each league, 8 tests, and AT-35 of `page-suggestions` fails. With them on, all pass. AT-44 of `page-suggestions` passes with the restore off too. Its cause is the clock: with no fixed Wednesday, the page shows no Waiver targets chip. `setSystemTime` of `bun:test` fixes `Date`, and AT-44 passes.

**Changes:**

- `scripts/bun-test.mjs` runs `bun test --isolate` on `src/`, `scripts/`, `test/`, and the `site/` folder of each package. `scripts/bun-test-files.mjs`, its types, and `BUN_TEST_DIRS` go away, because no file needs a runner choice.
- `check:fast` and `pnpm test` run only `pnpm test:bun`. The Makefile drops `VITEST_CHANGED`. The `env -u GIT_DIR` prefix stays, because `src/tracker-rule.test.ts` runs git from `apps/site`. The root test of the prefix now cuts the command at `LINT_FILES=`.
- The site drops `vitest`, `@vitejs/plugin-react`, and `jsdom`, and each package drops `vitest`. The lock diff only removes 93 entries. No `bun.lock` exists. `entities@8.1.0` and `whatwg-mimetype@5.0.0` were jsdom entries on `main`. The `entities@7.0.1` and `whatwg-mimetype@3.0.0` entries come from happy-dom of ticket 08.
- `src/suppression-rule.test.ts` no longer lists `vitest.config.mts`, because the file is gone.
- The four tests of `src/lib/data/` drop their `resetModules`, because each reader reads the working folder on each call.
- `page-personal` sets `clientValues.packages` in the test, in place of `vi.doMock`, because `loadFrontDoor` reads it on each call. Bun types `toBe` strictly, so one `closest("li")` takes `<HTMLElement>`.
