# 02: The baseline times of the checks

Map: `.scratch/design-checks-speed/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

The speed targets need a baseline. Measure each one and record the command and the machine:

1. The wall-clock time of a full `make check-fast` on the laptop, with no other check running. Give the time of each step: scripts, the client build, `tsc`, Vitest, the pipeline, and the API.
2. The time of each CI job of `.github/workflows/check.yml` on the last 5 green runs of `main`, and the time of its install step.
3. The cost of `create_app` per API test in `apps/api/tests`. Each test builds its own app with its own settings. Say whether one shared app saves enough time to be worth the change.

## Decision

None yet.
