# Notes for ticket 02: the baseline times of the checks

Date: 2026-11-20. Worktree branch `design-checks-speed`.

## 1. CI jobs on the last 5 green runs of main (ticket item 2)

Command: `gh run list --workflow check.yml --branch main --status success --limit 5`, then
`gh api repos/{owner}/{repo}/actions/runs/<id>/jobs`. Time = `completed_at - started_at` of the job or step.

Runs: A 44656282511, B 44653842000, C 44653817792, D 44649124810, E 44585015323.

| Job (seconds)  | A   | B   | C   | D   | E   | Median |
| -------------- | --- | --- | --- | --- | --- | ------ |
| site-browser   | 740 | 774 | 831 | 746 | 623 | 746    |
| pipeline       | 410 | 251 | 375 | 315 | 422 | 375    |
| api            | 233 | 238 | 233 | 225 | 204 | 233    |
| site-unit      | 208 | 200 | 200 | 202 | 201 | 201    |
| packages       | 84  | 91  | 101 | 100 | 87  | 91     |
| scripts        | 39  | 34  | 31  | 40  | 28  | 34     |
| Whole run      | 753 | 781 | 840 | 754 | 633 | 754    |

The jobs run in parallel, so the whole run is the slowest job (site-browser) plus about 10 to 90 s of queue and gate time.

Steps, in seconds, with the median of the 5 runs:

| Step                                            | Median | Range  |
| ----------------------------------------------- | ------ | ------ |
| Test step of site-browser (`check-site-browser`) | 666    | 555-739 |
| Test step of pipeline (`check-pipeline`)         | 342    | 219-373 |
| Test step of api (`check-api`)                   | 191    | 174-200 |
| Test step of site-unit (`check-site-unit`)       | 163    | 160-165 |
| Test step of packages                            | 60     | 44-66  |
| Test step of scripts                             | 5      | -      |
| Install Chromium and WebKit system packages (site-browser) | 35 | 27-56 |
| Check out the repository (each job)              | 25     | 19-36  |
| Set up pnpm or uv                                | 3      | 2-8    |
| Install dependencies (`pnpm install`, `uv sync`) | 2      | 1-3    |

The install steps are small. Dependency install is 1 to 3 s because the caches hit. The checkout step is 19 to 36 s in each job, which is large for a plain checkout. The Chromium and WebKit apt install is 27 to 56 s.

The check does not meet 360 s today. Two jobs sit above it: site-browser (median 746 s) and pipeline (median 375 s). The test step of the site-browser job is the most time in CI.

## 2. The cost of `create_app` in the API tests (ticket item 3)

Commands, from `apps/api`:
`PYTHONPATH=<scratchpad> uv run --exact --package cpc-api pytest -q -n 0 -p timeplugin --durations=15`.
The plugin `timeplugin.py` in the scratchpad wraps `cornerstone_api.app.create_app` and sums the time of each call. The run used `-n 0`, so one process ran all tests.

Result:
- 603 tests passed, 8 deselected. 527 calls of `create_app`.
- All calls together: 2.09 s. Mean 4.0 ms. Median 3.6 ms. Max 23.6 ms.
- The serial run took 489 s. It ran while another session ran its own checks, so the wall time is high. The share is what counts: `create_app` is 0.4 percent of the run.
- The slowest tests take 5 to 13 s each. 13 of the 15 slowest are in `test_trade_topics.py`. The other two are in `test_api.py` (a rate limit test, 12.3 s, and a two-failed-responses test, 10.1 s). The cause is in the test body, not in `create_app`. Not yet found.
- CI runs `make check-api`, which has `pytest -q -n auto` (xdist). The API check step takes 191 s median.

Verdict: one shared app saves at most 2 s of 489 s serial time, and less in CI with xdist. It is not worth the change, and a shared app would leak state between tests (rate limiter, kept answers, live cache). Look at the slow tests instead.

## 3. Laptop timing (ticket item 1)

Machine: Apple M2 Pro, 10 cores (`sysctl -n machdep.cpu.brand_string`, `sysctl -n hw.ncpu`). Node v24.15.0.
Vitest caps workers at 2 outside CI (`maxWorkers: process.env.CI ? undefined : 2` in `apps/site/vitest.config.ts`). CI uses the default.

Command: `make check-fast` at the worktree root, with no `BASE` and no `STAGED`. The wait script checked `pgrep -fl 'vitest|bun test|check-fast|pytest'` on three checks 30 s apart. Another session started a check-fast during the wait, so the script waited twice. The runs started on a quiet machine.

Full runs: run 1 = 195 s, run 2 = 194 s. Both exit 0. Each ran 15 sections: scripts, site, pipeline, api, and 11 packages (design is covered by the site).

Each step on its own (single run, after the full runs):

| Step                                               | Seconds |
| -------------------------------------------------- | ------- |
| Scripts check (`python3 -B -m unittest discover`)  | 10      |
| Client build (`CLIENT=cpc node scripts/client-build.mjs`, run from `apps/site`) | 0.2 |
| `pnpm typecheck` in `apps/site` (`next typegen && tsc --noEmit`) | 1 |
| `vitest run` in `apps/site`                        | 138     |
| Pipeline `make check-fast` (lint, typecheck, rules) | 6      |
| API `make check-fast` (lint, typecheck, rules)     | 3       |
| `packages/analyzer/python` check-fast              | 4       |

Vitest: 183 test files, 1775 tests, all passed. Duration 138.10 s: tests 68 percent, environment 20 percent, import 11 percent. Vitest reports 183 workers spawned at about 356 ms each, and says `isolate: false` would be at least about 32 s faster.

Caveats:
- The first attempt at the client build step failed with rc=1 because my script ran it from the wrong folder. That is my script error, not a repo fault. I ran it again from `apps/site`.
- The client build and typecheck times are warm: the output and the tsc cache already existed. A cold run is longer. I did not measure it.
- On the laptop, `check-fast` runs only the rule tests of the pipeline and the API, not the full tests. CI runs the full tests, which is why the CI pipeline and api jobs take far longer.

The step that takes the most time on the laptop is `vitest run` in the site (138 of 195 s, 71 percent).

## What the spec needs to know

1. Baseline for the CI `check` job: the whole run takes a median of 754 s. The 360 s target needs site-browser (746 s) cut by about half, and pipeline (375 s) cut by a little.
2. The test step of site-browser takes the most time in CI (median 666 s). The install steps are small: dependencies 1 to 3 s, Chromium and WebKit apt 35 s, checkout 25 s in each job.
3. Baseline for the laptop `make check-fast`: 195 s, 194 s. Half is about 97 s. Vitest takes 138 s alone, so the target needs Vitest to fall below about 90 s. Every other step together takes about 57 s.
4. The 2-worker cap of Vitest outside CI and the 183 worker spawns (about 32 s from `isolate: false` by Vitest's own estimate) are the first levers for the laptop. The estimate is not tested here.
5. A shared `create_app` is not worth it: 2.09 s of 489 s. Slow tests in `test_trade_topics.py` (5 to 13 s each) and the pipeline test step (342 s) are the API and pipeline targets.
