# 02: How a merge conflict of a ticket clears

Map: `.scratch/fast-cycle/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

On `midseason-report`, 9 merge-backs hit a conflict. Each one went back to the ticket subagent, a round trip of 10 to 40 min, one after another. The build took 3.6 h for 14 tickets.

## Decision

Brian decided on 2026-11-06, in a grill.

The orchestrator resolves the conflict itself in the spec worktree with `resolving-merge-conflicts`. It then runs `make check-fast` on the result. No send-back to the ticket subagent. A red check still resets the spec branch to the head before the merge, as `build.md` says now.

A "Blocked by" edge for tickets that touch the same file is out of scope for now. Brian chose the smaller change first.
