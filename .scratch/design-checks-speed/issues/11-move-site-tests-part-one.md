# 11: Move the first half of the site app tests

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests none alone. It feeds AT-20 and AT-21.

**App:** site

**What to build:** About half of the 82 test files of the site app, the front door and its neighbors, move to the native `bun:test` calls and run on `bun test`. A test that depends on jsdom gets a fix for happy-dom, or the ticket names it for Brian.

**Blocked by:** 08

**Status:** ready-for-agent

- [x] The moved files pass on `bun test` with no `vi.` call and no `vitest` import.
- [x] The count of tests that pass equals the count before the move for these files, or the ticket names each change.
- [x] The fast site check exits 0.

**Counts:** `apps/site/src/app/` holds 58 test files with 619 passing tests on Vitest. 40 files move to `bun test`. They had 294 passing tests on Vitest, and they have 294 on `bun test`, with the same count in each file.

**Files on Vitest, named for Brian:** 18 files stay on Vitest, with 325 tests. Each one fails on a fault of happy-dom under `bun test`, as ticket 10 found:

- No page URL, so a root-relative `img` src fires `error` and the avatar swaps to its default: `_routes/managers/manager-page`, `_routes/managers/page`, `_routes/rankings/page`, `_routes/waiver/page`, `_routes/waiver/war-chest`, `front-page`.
- No page URL, so a relative `fetch` or `history.replaceState` fails: `_routes/sim/announcement`, `page-free`, `page-personal`, `page-grade-blocks`, `page-site`, `page-suggestions`, `page-topic-sweep`.
- No frame limit, so an exit or a wait stalls, or the file runs past 4 minutes: `page`, `page-ask`, `front-door/suggestions`, `front-door/steps`.
- `spyOn(Storage.prototype, ...)` has no effect after the first read: `front-door/tour`.

`waiver/page` also expects the Node date text "Fri, Oct 23, 10:05 AM". Bun gives "Fri, Oct 23 at 10:05 AM".

**Changes:**

- `scripts/bun-test.mjs` runs `bun test --isolate`. Without it, a file sees the DOM nodes and the module state of the files before it, and the Tour tests failed by the order of the run.
- `BUN_TEST_DIRS` takes a folder or one file. A folder with a file on Vitest lists each moved file. The Vitest config skips each entry and each file under it.
- `src/lib/data/week-data.ts` reads the working folder on each call, not once when it loads, so a test needs no `vi.resetModules` to point it at a fixture folder.
- `test/phone.ts` gives `stubPhone`. happy-dom has a desktop-wide window, so the menu sheet closed at once. Three tests stub `matchMedia` as a phone, as the jsdom stand-in did.
- `home-flag` sets the flag on `clientValues` in the test, in place of `vi.doMock`, because the page reads it when it renders.
- `tour-store` swaps `localStorage` for a blocked store, in place of a spy on `Storage.prototype`.
- `not-found` and `eggs/targets` drop the jsdom stubs of `matchMedia` and `IntersectionObserver`, because happy-dom has both.
- `eggs/targets` reads the status line inside the replay, not in the whole body.
