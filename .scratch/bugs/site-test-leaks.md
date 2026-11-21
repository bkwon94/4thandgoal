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
Cause: `routeOver`, `readerOver`, `pageOver`, `routeOfClient`, `dataWithoutWaiver`, and two inline tests in nine site test files (`manager-page.test.tsx`, `managers/page.test.tsx`, `manager-data.test.ts`, `rankings/page.test.tsx`, `rankings-data.test.ts`, `waiver/page.test.tsx`, `waiver-data.test.ts`, `week-data.test.ts`, `page-personal.test.tsx`) make a temp `public/` folder with `mkdtempSync` under `os.tmpdir()` and never remove it, so each run of the suite leaves 72 folders in the macOS temp folder.
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

The check runs the full suite through `scripts/bun-test.mjs` with `TMPDIR` set to an empty folder under `apps/site/test-results/`, so the temp entries of other sessions do not change the count. The other 17 prefixes, `reset-modules` among them, show `0 -> 0` in both runs.
Test verdict: pending

### 2. Some site tests call the live API

Done condition: One run of the site `bun test` suite sends no request to `https://api.4thandgoal.app` or to a Fly address, and its output holds no `Cross-Origin Request Blocked` and no `ECONNREFUSED`.
Method: diagnosing-bugs
Cause: pending
Red: pending
Green: pending
Test verdict: pending

## Smoke

Smoke: pending

## Comments
