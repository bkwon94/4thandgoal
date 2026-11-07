# 13: Does open PR 13 keep the old verdict rule

Map: `.scratch/fast-cycle/MAP.md`.

**Kind:** grill

**Blocked by:** 06

**Status:** done

## Question

PR #13 `midseason-report` is open under ADR 0020, and its redesign tickets still wait for `cpc:implement`. The spec must say if the PR moves to the Judge when this spec merges, or merges on Brian's verdicts first.

## Decision

Brian decided on 2026-11-06, in a grill.

PR #13 `midseason-report` keeps the old rule: Brian posts its Test verdicts. `fast-cycle` merges to `main` only after PR #13 merges. The work of this spec comes after the midseason report.

The reason: the code needs no special case for one PR, and the redesign of the midseason report does not wait on this spec.
