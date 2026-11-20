# 11: Move the first half of the site app tests

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests none alone. It feeds AT-20 and AT-21.

**App:** site

**What to build:** About half of the 82 test files of the site app, the front door and its neighbors, move to the native `bun:test` calls and run on `bun test`. A test that depends on jsdom gets a fix for happy-dom, or the ticket names it for Brian.

**Blocked by:** 08

**Status:** in-review

- [x] The moved files pass on `bun test` with no `vi.` call and no `vitest` import.
- [x] The count of tests that pass equals the count before the move for these files, or the ticket names each change.
- [x] The fast site check exits 0.

**Counts:** `apps/site/src/app/` holds 58 test files with 619 passing tests on Vitest. 53 files move to `bun test`. They had 516 passing tests on Vitest, and they have 516 on `bun test`, with the same count in each file.

**Files on Vitest, named for Brian:** 5 files stay on Vitest, with 103 tests: `page-free`, `page-personal`, `page-grade-blocks`, `page-suggestions`, and `page-topic-sweep`. Each one streams an Answer. happy-dom puts its own stream classes on the globals, and the native `pipeThrough` of Bun refuses them: "The transform's 'readable' property must be a ReadableStream". The Answer then shows "The question did not go through". This fault is proven in `page-free`, `page-personal`, `page-grade-blocks`, and one test of `page-suggestions`. In `page-topic-sweep`, 8 personal Topics show no block, and in `page-suggestions` AT-44 finds no chip of Waiver targets. The same fault is the likely cause, but not proven.

**Changes:**

- `BUN_TEST_DIRS` lists `src/app/_routes`, `src/app/front-door`, and `src/app/fonts` as folders, and each moved file of the `src/app` root as its own entry.
- `src/lib/data/week-data.ts` reads the working folder on each call, not once when it loads, so a test needs no `resetModules` to point it at a fixture folder.
- `test/phone.ts` gives `stubPhone`. happy-dom has a desktop-wide window, so the menu sheet closed at once. Six tests stub `matchMedia` as a phone, as the jsdom stand-in did.
- Each moved file that calls `readFixtureSite` calls `restoreFixtureSite` after each test.
- `home-flag` sets the flag on `clientValues` in the test, in place of `vi.doMock`, because the page reads it when it renders.
- `not-found` and `eggs/targets` drop the jsdom stubs of `matchMedia` and `IntersectionObserver`, because happy-dom has both.
- `eggs/targets` reads the status line inside the replay, because the ui-sdk announcer is also a status line.
- `waiver/page` takes the date of Node, "Oct 23, 10:05", or of Bun, "Oct 23 at 10:05".
- `front-door/steps` lets the Framer Motion frames end, 1 s on fake timers, before it checks that no timer runs. A live spinner still leaves one timer.
- `page` fixes only `Date` with `setSystemTime`, in place of fake timers that fake only `Date`. `sim/announcement` fakes each timer, because Bun has no choice of which timers to fake.
- `front-door/suggestions` checks one call and its value in place of `toHaveBeenCalledExactlyOnceWith`, which Bun lacks.
- `page-free` and `page-personal` stay on Vitest, so their 8 s waits from ticket 04 stay as they are.
