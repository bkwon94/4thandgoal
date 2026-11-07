# 05: When the full check runs before the push

Map: `.scratch/fast-cycle/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

On `midseason-report`, CI found a test that made a real Claude call, and then hit its timeout. One failure that CI found cost about 8 h of wall time, from 23:51 to 07:54.

## Decision

Brian decided on 2026-11-06, in a grill.

The orchestrator starts one `make check` in the background when the evidence stage starts. The evidence stage takes 11 to 17 min, so the run adds no wall time. A failure gets fixed before the push. CI stays the final gate.

This is one run per spec. A ticket build and a merge-back still run only `make check-fast`, per the memory of Brian on the full suite.
