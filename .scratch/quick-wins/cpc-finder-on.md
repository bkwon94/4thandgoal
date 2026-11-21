# Turn on the Finder of cpc

Kind: quick-win
Status: in-progress
Branch: `win-cpc-finder-on`.
Source: the handoff file `.handoff/cpc-finder-on.md` and the session of 2026-11-20.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam, it flips one existing flag; the done condition is one sentence.

## Items

### 1. Turn on the Finder of cpc

Done condition: `clients/cpc/client.toml` sets `finder = true`, and the full check passes for cpc, with `client-steps.test.mjs` and the grade-bar project on the cpc export.
Method: tdd
Red: at `2c28eb94` with `apps/site/scripts/client-steps.test.mjs` of `3f4e0e33`, `cd apps/site && pnpm exec vitest run scripts/client-steps.test.mjs`

```text
FAIL  scripts/client-steps.test.mjs > the steps of a client > runs the grade-bar project on a second build for cpc, the client with the finder on
AssertionError: expected [ 'build', 'check:export', …(1) ] to deeply equal [ 'build', 'check:export', …(3) ]
-   "build",
-   "check:grade-bar-export",
 Tests  1 failed | 2 passed (3)
```
Green: at `3f4e0e33`, `cd apps/site && pnpm exec vitest run scripts/client-steps.test.mjs`

```text
 Test Files  1 passed (1)
      Tests  3 passed (3)
```
Test verdict: pending

## Smoke

Smoke: flow `Analyzer` on cpc. "Smoke run: 1 flow, 1 passed, 0 failed". Shots in `.scratch/quick-wins/cpc-finder-on/smoke/`.

## Comments

Grade-bar run on cpc at `d0d53fac`: `cd apps/site && CLIENT=cpc NEXT_PUBLIC_API_URL=http://localhost:8080 pnpm build && CLIENT=cpc pnpm check:export && CLIENT=cpc pnpm check:grade-bar-export`. Result: check:export passed; 38 passed, 4 skipped.
The first run failed 2 tests: the back check of `finder-ledger.spec.ts` on the iPhone, light and dark. The cpc page has little content under the last card, so the page ends with the card top 20 px above the screen. NorCal has more content under it. The spec held a NorCal-only assumption (`box.y >= 0`). The check now also accepts a page at its end. NorCal still passes: 38 passed, 4 skipped.
The first two smoke runs were red. Run 1 had no API keys in the shell, so the grade failed with status 500. Run 2 had the keys, but the fair warm-up of cpc started with 0 cached answers and held the grade past 120 s. One warm-up run filled `data/cache/fair/cpc.json` for $1.27, and run 3 passed.
