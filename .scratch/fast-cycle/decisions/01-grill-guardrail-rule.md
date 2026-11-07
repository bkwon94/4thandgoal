# 01: What counts as the same guardrails

Map: `.scratch/fast-cycle/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Each later decision must keep the guardrails. The spec needs one rule that says which change to a check is allowed.

## Decision

Brian decided on 2026-11-06, in a grill.

1. A check can move to a different place, run in parallel, or use a cache.
2. A check never disappears and never gets weaker: no skipped test, no lower assertion, and no `xfail`.
3. The merge to `main` needs the full `make check` green on the final commit, plus a Test verdict of PASS for each acceptance test.
4. A ticket merge-back needs `make check-fast` green on the merged result.
5. CI always runs the full check of every app. A CI run of only the changed apps is out.
6. A smaller sim sample in a test is allowed, if the assertion stays the same and holds with a fixed seed.

The reason: the speed must come from where and how a check runs, not from fewer checks.
