# 04: Does the cascade also cover the midseason blurbs and the publish re-check?

Map: `.scratch/jev/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** wontfix

## Question

The midseason report makes about 12 verifier calls in its build. `recheck_prose` in `midseason/prose.py` makes 12 more at `midseason-publish`.
The re-check is the last check before the report goes live, and it guards the edits that a person makes.

Choose one: the weekly build only, the midseason build too, or the midseason build and the re-check.

## Decision

Brian narrowed the spec to the bare minimum on 2026-11-09. The Jev check runs in the weekly build only. The midseason build and its re-check are out of scope.
