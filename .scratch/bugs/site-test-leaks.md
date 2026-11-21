# Site tests leak temp folders and reach the live API

Kind: bug
Status: in-progress
Branch: `bug-site-test-leaks`.
Source: the queue task `Site tests leave temp folders behind`, and the handoff file `.handoff/2026-11-21-quick-test-fixes.md`, items 1 and 3.
Boundary: holds. 2 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. Site tests leave temp folders behind

Done condition: One run of the site `bun test` suite leaves no more entries in the macOS temp folder than it found, for each `mkdtemp` prefix of a site test.
Method: diagnosing-bugs
Cause: `routeOver`, `readerOver`, `pageOver`, `routeOfClient`, `dataWithoutWaiver`, and two inline tests in nine site test files (`manager-page.test.tsx`, `managers/page.test.tsx`, `manager-data.test.ts`, `rankings/page.test.tsx`, `rankings-data.test.ts`, `waiver/page.test.tsx`, `waiver-data.test.ts`, `week-data.test.ts`, `page-personal.test.tsx`) make a temp `public/` folder with `mkdtempSync` under `os.tmpdir()` and never remove it, so each run of the suite leaves 73 folders in the macOS temp folder.
Red: at `2d625fd0`, `node scripts/temp-leak-check.mjs` in `apps/site`

```text
 1955 pass
 0 fail
Ran 1955 tests across 203 files. [82.19s]
bun test exit code: 0
LEAK front-door-personal-: 0 -> 1
LEAK manager-data-: 0 -> 9
LEAK manager-page-: 0 -> 25
LEAK managers-index-: 0 -> 12
LEAK rankings-data-: 0 -> 6
LEAK rankings-page-: 0 -> 8
LEAK waiver-data-: 0 -> 6
LEAK waiver-page-: 0 -> 4
LEAK week-data-: 0 -> 2
FAIL: 9 of 26 prefixes left temp folders behind.
```

Green: at `e0d999f0`, `node scripts/temp-leak-check.mjs` in `apps/site`

```text
 1955 pass
 0 fail
Ran 1955 tests across 203 files. [51.60s]
bun test exit code: 0
ok   front-door-personal-: 0 -> 0
ok   manager-data-: 0 -> 0
ok   manager-page-: 0 -> 0
ok   managers-index-: 0 -> 0
ok   rankings-data-: 0 -> 0
ok   rankings-page-: 0 -> 0
ok   waiver-data-: 0 -> 0
ok   waiver-page-: 0 -> 0
ok   week-data-: 0 -> 0
PASS: 0 of 26 prefixes left temp folders behind.
```

The check runs the full suite through `scripts/bun-test.mjs` with `TMPDIR` set to an empty folder under `apps/site/test-results/`, so the temp entries of other sessions do not change the count. The other 17 prefixes show `0 -> 0` in both runs. `reset-modules.test.ts` makes its folder under `apps/site/test-results/` and removes it in `afterAll`, so it has no `os.tmpdir()` prefix.
Test verdict: pending

### 2. Some site tests call the live API

Done condition: One run of the site `bun test` suite sends no request to `https://api.4thandgoal.app` or to a Fly address, and its output holds no `Cross-Origin Request Blocked` and no `ECONNREFUSED`.
Method: diagnosing-bugs
Cause: `useBoard` in `packages/eggs/site/board/use-board.ts` calls `/eggs/board` of `eggsTarget` from `src/lib/config.ts`, the live API, for the egg button in the shell of each page, and `door-page.tsx` also calls `/suggestions` and `/deadline/trades`. No test stubbed `fetch` for these calls, so happy-dom sent each one: a CORS block, or a socket to a Fly address that the window close of the file canceled. The two sim tests of `sim-page.test.tsx` and `in-playoffs.test.tsx` called `http://127.0.0.1:9` on purpose for a refused connection.
Red: at `ceba8eb5`, `node scripts/network-leak-check.mjs` in `apps/site`

```text
 1955 pass
 0 fail
Ran 1955 tests across 203 files. [49.10s]
bun test exit code: 0
LEAK ../../packages/sim/site/page/in-playoffs.test.tsx: ECONNREFUSED x2
LEAK ../../packages/sim/site/page/sim-page.test.tsx: ECONNREFUSED x4
LEAK src/app/_routes/ask/page.test.tsx: ECANCELED x2
LEAK src/app/_routes/ask/page.test.tsx: ECONNREFUSED x2
LEAK src/app/_routes/ask/page.test.tsx: a Fly address x4
LEAK src/app/_routes/eggs/targets.test.tsx: Cross-Origin Request Blocked x1
LEAK src/app/_routes/eggs/targets.test.tsx: ECANCELED x2
LEAK src/app/_routes/eggs/targets.test.tsx: ECONNREFUSED x2
LEAK src/app/_routes/eggs/targets.test.tsx: a Fly address x4
LEAK src/app/_routes/eggs/targets.test.tsx: the live API x2
LEAK src/app/front-door/tour-norcal.test.tsx: Cross-Origin Request Blocked x3
LEAK src/app/front-door/tour-norcal.test.tsx: the live API x6
LEAK src/app/front-door/tour-replay.test.tsx: Cross-Origin Request Blocked x12
LEAK src/app/front-door/tour-replay.test.tsx: the live API x24
LEAK src/app/front-door/tour.test.tsx: Cross-Origin Request Blocked x48
LEAK src/app/front-door/tour.test.tsx: the live API x96
LEAK src/app/home-flag.test.tsx: ECANCELED x2
LEAK src/app/home-flag.test.tsx: ECONNREFUSED x2
LEAK src/app/home-flag.test.tsx: a Fly address x4
LEAK src/app/page.test.tsx: Cross-Origin Request Blocked x78
LEAK src/app/page.test.tsx: ECANCELED x4
LEAK src/app/page.test.tsx: ECONNREFUSED x4
LEAK src/app/page.test.tsx: a Fly address x8
LEAK src/app/page.test.tsx: the live API x156
LEAK src/reduced-motion.test.tsx: Cross-Origin Request Blocked x9
LEAK src/reduced-motion.test.tsx: the live API x18
FAIL: 499 output lines show a request that left the test process.
```

Green: at `bae8b6c6`, `node scripts/network-leak-check.mjs` in `apps/site`

```text
 1956 pass
 0 fail
Ran 1956 tests across 203 files. [49.24s]
bun test exit code: 0
PASS: no output line shows a request to the live API, a Fly address, Cross-Origin Request Blocked, ECONNREFUSED, ECANCELED.
```

The Red block holds all 26 LEAK lines of a run at `ceba8eb5`. The count of each line changes from run to run, because each hit depends on network time. The check names the file that printed each hit, so a request that fails after its test ends shows under a later file. The fix gives each test a `fetch` in `test/preload.ts` that rejects each call to a host other than `localhost` or `127.0.0.1`, so a new page test is safe too. The extra test is in `test/stubs.test.ts` and proves that a call to the live API rejects. Two tests of `front-page.test.tsx` passed only because a hung board call of an earlier test held the shared `inFlight` promise of `boardApi`. They now read only the teams call.
Test verdict: pending

## Smoke

Smoke: flows `Front door`, `Passphrase`, `Week report`, `Manager page`, `Analyzer`, `Power rankings`, `Midseason report`. "Smoke run: 7 flows, 7 passed, 0 failed". Shots in `.scratch/bugs/site-test-leaks/smoke/`.

## Comments
