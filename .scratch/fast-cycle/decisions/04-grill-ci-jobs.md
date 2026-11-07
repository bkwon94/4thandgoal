# 04: The shape of the CI check

Map: `.scratch/fast-cycle/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

The CI check took 7 min in October and 26 min on the last `midseason-report` run. One job runs every app in sequence: the pipeline tests take 10.7 min, the Chromium install 6.3 min, the site 6 min, and the API 1.7 min. The step took 19.1 min against a 20 min job timeout.

## Decision

Brian decided on 2026-11-06, in a grill.

1. CI runs one job per app and package: `site`, `pipeline`, `api`, and `packages`. They run at the same time.
2. A final gate job named `check` needs all of them, so the required status and the `workflow_run` trigger of the deploys keep their name.
3. Chromium comes from a cache.
4. The pipeline tests run in parallel with `pytest-xdist`, if research 09 shows it is safe.

The target is 10 min or less for the CI check. The details are spec ticket 11.
