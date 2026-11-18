# 05: The shape of the approved diff list

Map: `.scratch/trusted-green/MAP.md`.

**Kind:** spec

**Blocked by:** 09

**Status:** done

## Question

A PR that changes the output of a week on purpose must name each approved diff, so the rebuild job passes. The spec sets the path and the shape of that list, and how a reader sees each approved diff in the PR.

## Decision

Recorded in `PRD.md` under Implementation Decisions, approved by Brian on 2026-11-18. The list of approved diffs: `REBUILD.md` or a `Rebuild:` block; the changed set must equal the listed set.
