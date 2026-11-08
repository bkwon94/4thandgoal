# 09: Where does the site get the grade weights?

Map: `.scratch/card-polish/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** open

## Question

The Grade dial shows the weight of each part: 45, 30, 10, and 15. The weights live in `GRADE_WEIGHTS` in `packages/managers/python/src/managers/tunables.py`. `managers.json` does not carry them. The spec changes the site only, so a copy in the site can drift from the pipeline. The spec must choose: a site constant with a test that compares it to the pipeline value, or move this one field into `managers.json` as an exception to "site only".

## Decision

None yet.
