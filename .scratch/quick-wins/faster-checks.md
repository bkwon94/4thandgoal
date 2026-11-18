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
Red: at `5dcc8f82` with `scripts/test_changed_apps.py` of `771478a6`, `cd scripts && python3 -B -m unittest test_changed_apps.TheSiteTestSelection`

```text
FAIL: test_a_base_run_of_the_site_tests_only_the_files_changed_since_the_base
AssertionError: '--changed HEAD~1' not found in '\techo "==> site: check-fast"; pnpm --dir apps/site check:fast; '
FAIL: test_a_staged_run_of_the_site_tests_only_the_changed_files
AssertionError: '--changed' not found in '\techo "==> site: check-fast"; pnpm --dir apps/site check:fast; '
Ran 3 tests in 0.574s
FAILED (failures=2)
```

Green: at `771478a6`, `cd scripts && python3 -B -m unittest test_changed_apps.TheSiteTestSelection`

```text
...
Ran 3 tests in 0.541s
OK
```

The run with no selection passes at both commits, so the full suite stays the default. `make check-fast BASE=main` passes at `771478a6`. It runs all 160 files, because this change edits `apps/site/package.json`, which Vitest treats as a rerun trigger. A small change selects few files: `vitest run --changed HEAD` after one added comment line in `apps/site/src/lib/config.ts` ran 27 of 160 files in 58 s, against 156 s for all. The same run with `packages/waiver/site/format.ts` ran 3 files in 3 s.
Test verdict: PASS

### 2. Playwright runs 4 workers on CI

Done condition: `apps/site/playwright.config.ts` runs 4 workers when `CI` is set and 2 workers when it is not, and each floor test that measures wall time runs in a pass of its own with 1 worker, after the parallel pass.
Method: tdd
Red: pending
Green: pending
Test verdict: pending

### 3. CI runs the site check as two jobs at the same time

Done condition: `.github/workflows/check.yml` runs the unit check of the site and the browser check of the site as two jobs at the same time, the gate job needs both, and `make check-site` still runs the same commands in sequence.
Method: text only
Red: none, text only.
Green: at `b1d75aa5`, the diff of the text. `check.yml` has the jobs `site-unit` and `site-browser`, and the gate needs both. `site-unit` runs `make check-site-unit` with no browser. `site-browser` runs `make check-site-browser`. In `apps/site/package.json`, `check` is `pnpm check:fast && pnpm check:browser`, so `make check-site` runs both halves in sequence. Only `verdict` is a required check, so the new job names break no rule.
Test verdict: none

### 4. The egg hunt test uses fake timers

Done condition: `packages/eggs/site/hunt/egg-hunt.test.tsx` passes all of its tests with fake timers in place of real waits, and its file time in the vitest JSON report is under 15 s.
Method: tdd
Red: at `8d4ae5d7`, the parent of the change, with a loop that is not a file. It runs `pnpm exec vitest run ../../packages/eggs/site/hunt/egg-hunt.test.tsx --reporter=json` in `apps/site`, reads the file time from the JSON report, and exits 1 if a test fails or the file time is 15 s or more.

```text
tests 40 failed 0 file time 77.3 s
exit 1
```

Green: at `ffaa7e93`, the same loop.

```text
tests 40 failed 0 file time 2.1 s
exit 0
```

`beforeEach` calls `vi.useFakeTimers({ shouldAdvanceTime: true })` and `afterEach` calls `vi.useRealTimers()`. `wait` is now `act(() => vi.advanceTimersByTimeAsync(ms))`. No assertion changed. Three more runs took 2.1 s, 2.2 s, and 2.4 s with 40 of 40 passed. `make check-fast BASE=main` passes.
Test verdict: PASS

### 5. A change of the tracker or the docs alone selects only the members that read it

Done condition: `scripts/changed_apps.py` selects only the members whose tests read the changed paths for a change only under `.scratch/` or `docs/`, and any other root path still selects every member.
Method: tdd
Red: at `024ee32f` with `scripts/test_changed_apps.py` of `6a1c31d0`, `cd scripts && python3 -B -m unittest test_changed_apps.TheRootFolderSelection`

```text
AssertionError: Lists differ: ['site', 'pipeline', 'api'] != ['site', 'pipeline']
AssertionError: Lists differ: ['site', 'pipeline', 'api'] != []
AssertionError: Lists differ: ['site', 'pipeline', 'api'] != ['api']
Ran 7 tests in 0.017s
FAILED (failures=7)
```

Green: at `6a1c31d0`, `cd scripts && python3 -B -m unittest test_changed_apps.TheRootFolderSelection`

```text
Ran 7 tests in 0.043s
OK
```

The hook runs the root script tests, so it rejects a red commit. The loop and the change share the commit `6a1c31d0`. The whole file `test_changed_apps` runs 35 tests and passes. `make check-fast BASE=main` passes. A staged change of only `.scratch/quick-wins/faster-checks.md` makes `python3 -B scripts/changed_apps.py --staged` print `site pipeline`. The site still runs, because `apps/site/src/tracker-rule.test.ts` reads `.scratch/` and `docs/agents/state.md`. The pipeline reads the same files in `apps/pipeline/tests/test_rule_tracker.py`. No test of the API or of a package reads `.scratch/` or `docs/`. A change of only an ADR under `docs/adr/` selects no member. A `CLAUDE.md` or `AGENTS.md` under either folder selects the site and the pipeline, because the rules-file rule reads its name in every folder (`apps/site/src/readme-rule.test.ts`, `apps/pipeline/tests/test_rule_readmes.py`).
Test verdict: PASS

## Comments

Closes with the squash merge of the PR of `win-faster-checks`. Commits: `771478a6`, `872c7a15`, `b1d75aa5`, `ffaa7e93`, `6a1c31d0`. Date: 2026-11-18.
The loops of items 1, 4, and 5 went red, then green; `test_changed_apps` runs 35 tests, the egg hunt file passes 40 of 40 in 2.1 s, and `make check-fast BASE=main` passes.
A later run can follow up on these notes:
- On a change of only a `.scratch/` ticket, `vitest run --changed` finds no affected file, so the hook skips `apps/site/src/tracker-rule.test.ts` and `apps/site/src/readme-rule.test.ts`. The pipeline twins `test_rule_tracker.py` and `test_rule_readmes.py` still run, and CI runs both.
- `apps/site/src/app/page-free.test.tsx` (36 s) and `page-personal.test.tsx` (26 s) are the next files for fake timers.
- `scripts/test_queue.py` takes about 6 s on each commit, but the root `Makefile` comment says the root scripts take under a second.
- A change to `apps/site/package.json` or a Vitest config file reruns all vitest files, because Vitest treats each one as a rerun trigger.
Read 16 files: AGENTS.md, Makefile, .github/workflows/check.yml, .pre-commit-config.yaml, scripts/changed_apps.py, scripts/test_changed_apps.py, scripts/queue.py, scripts/test_queue.py, apps/site/package.json, apps/site/playwright.config.ts, apps/site/vitest.config.ts, apps/site/scripts/build-each-client.mjs, apps/site/e2e/floor-rules.spec.ts, packages/eggs/site/hunt/egg-hunt.test.tsx, apps/pipeline/Makefile, apps/api/Makefile.

The CI run 44393438643 of PR #68 failed one floor test: `e2e/analyzer-stage.spec.ts:300` measured 116 ms against a limit of 100 ms under 4 workers. Brian chose a timing pass of 1 worker for the wall-time tests, so item 2 gets a test and a Judge. The close comment above names the commits before this fix.
