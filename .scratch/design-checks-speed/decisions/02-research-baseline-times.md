# 02: The baseline times of the checks

Map: `.scratch/design-checks-speed/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The speed targets need a baseline. Measure each one and record the command and the machine:

1. The wall-clock time of a full `make check-fast` on the laptop, with no other check running. Give the time of each step: scripts, the client build, `tsc`, Vitest, the pipeline, and the API.
2. The time of each CI job of `.github/workflows/check.yml` on the last 5 green runs of `main`, and the time of its install step.
3. The cost of `create_app` per API test in `apps/api/tests`. Each test builds its own app with its own settings. Say whether one shared app saves enough time to be worth the change.

## Decision

A research agent measured each item on 2026-11-20. The notes are `02-research-baseline-times.notes.md`.

1. The laptop, an M2 Pro with 10 cores: a full `make check-fast` took 195 s and 194 s. Vitest took 138 s of it, or 71 percent, for 183 files and 1,775 tests, with the local cap of 2 workers. The other steps take 1 to 10 s each. Half the baseline is about 97 s, so Vitest must drop below about 90 s.
2. CI, the median of 5 green runs of `main`: the whole run took 754 s. The jobs run in parallel, so the longest job sets the time: site-browser 746 s, pipeline 375 s, api 233 s, site-unit 201 s, packages 91 s, scripts 34 s. The Playwright test step of site-browser takes 666 s. The dependency install takes only 1 to 3 s.
3. `create_app` costs 4 ms per call: 527 calls, 2.09 s of a 489 s API run. One shared app is not worth it, so the idea drops. The slow API tests are in `test_trade_topics.py`, at 5 to 13 s each.

The CI target of 360 s cannot hold with the speed list of the map. The Bun swap touches only site-unit, and site-browser and pipeline sit above 360 s. A `node_modules` cache saves at most 3 s. New ticket 07 decides the target.
