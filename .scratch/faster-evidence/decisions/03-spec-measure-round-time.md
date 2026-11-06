# 03: How we measure the 15 minutes of a round

Map: `.scratch/faster-evidence/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** done

## Question

The outcome sets 15 minutes or less for a full round of site evidence. The spec says how a reader sees the time. Proposal: the script prints the time of each test, and `EVIDENCE.md` records the total of the round.

## Decision

The spec records it, approved by Brian on 2026-11-05. The runner prints the time of each test and the total. `EVIDENCE.md` gets the line `Round time: <N> min for <M> site tests.` under `Built from`. See `PRD.md`, Implementation Decisions.
