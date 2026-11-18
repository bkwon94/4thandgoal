# Faster checks

Kind: quick-win
Status: in-progress
Branch: `win-faster-checks`.
Source: the session of 2026-11-18.
Boundary: holds. 5 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## The baseline

Measured on 2026-11-18 at `6b75d218`.

- CI run 44232612432: the site job takes 842 s, and the other jobs take 223 s or less. The site job sets the wall time of the check, and each deploy waits on the check.
- The site step takes 781 s: vitest 154 s, Playwright `rules` 105 s, Playwright `floor` of cpc, norcal, and midseason 485 s, and the three `next build` runs about 30 s.
- Playwright runs 2 workers, but a public repo gets a runner with 4 cores.
- Local `make check-fast` of the site: `vitest run` takes 179 s of 160 files. Each other piece of the hook takes 13 s or less.
- A change only under `.scratch/` selects every member, so a commit of a tracker note waits on vitest too.
- `packages/eggs/site/hunt/egg-hunt.test.tsx` takes 79 s of 237 s of file time, with 20 real waits of `setTimeout`.

## Items

### 1. The fast check runs only the vitest files that a change selects

Done condition: `make check-fast STAGED=1` and `make check-fast BASE=<ref>` run only the vitest files related to the changed files, and a site run with no `STAGED` and no `BASE` still runs all vitest files.
Method: tdd
Red: pending
Green: pending
Test verdict: pending

### 2. Playwright runs 4 workers on CI

Done condition: `apps/site/playwright.config.ts` runs 4 workers when `CI` is set and 2 workers when it is not, and its comment names the 4 cores of the runner.
Method: text only
Red: pending
Green: pending
Test verdict: pending

### 3. CI runs the site check as two jobs at the same time

Done condition: `.github/workflows/check.yml` runs the unit check of the site and the browser check of the site as two jobs at the same time, the gate job needs both, and `make check-site` still runs the same commands in sequence.
Method: text only
Red: pending
Green: pending
Test verdict: pending

### 4. The egg hunt test uses fake timers

Done condition: `packages/eggs/site/hunt/egg-hunt.test.tsx` passes all of its tests with fake timers in place of real waits, and its file time in the vitest JSON report is under 15 s.
Method: tdd
Red: pending
Green: pending
Test verdict: pending

### 5. A change of the tracker or the docs alone skips the site

Done condition: `scripts/changed_apps.py` selects only the members whose tests read the changed paths for a change only under `.scratch/` or `docs/`, and any other root path still selects every member.
Method: tdd
Red: pending
Green: pending
Test verdict: pending

## Comments
