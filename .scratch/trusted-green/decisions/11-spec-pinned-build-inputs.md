# 11: How the build pins its inputs

Map: `.scratch/trusted-green/MAP.md`.

**Kind:** spec

**Blocked by:** 10

**Status:** done

## Question

The facts diff needs the five changes of ticket 10. The spec sets each one: where the clock comes from, the path and shape of each saved input, and how the research call reuses the saved claims. Recommended: save the slow-source values into the week folder, not the 24 MB cache. The spec also sets how an acceptance test proves the facts diff before a real week ships with the changes.

## Decision

Recorded in `PRD.md` under Implementation Decisions, approved by Brian on 2026-11-18. Each build saves its extract, slow-source values, and news; a facts-only rebuild reads the clock from `verify.json`.
