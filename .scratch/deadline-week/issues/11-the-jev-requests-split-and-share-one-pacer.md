# 11: The Jev requests split under 64k and share one pacer

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-63, AT-64, and AT-71.

**App:** api

**What to build:** A partner with more offers than one Jev request can hold sends them in several requests, each under the 64k context of one request, so no offer passes as unsure because a request was too large. Every press in the API process shares one pacer, so two managers who press at once stay under the account limit of 100,000 tokens per second. No request sends the long-context header of TypeSafe. Today's press keeps working the same way. This is the prefactor that lets the larger lists of tickets 12 and 13 run safely (decisions 14 and 16).

**Blocked by:** none

**Status:** done

- [x] A test with one partner of 1,200 offers sends 3 or more requests, each under 64,000 tokens by the estimate, and no offer passes as unsure.
- [x] A test with a fixed clock and two presses of 300,000 tokens each, at once, never holds more than 100,000 tokens in one second.
- [x] No Jev request of a real press sends `TypeSafe-Danger-Zone-Long-Context`.
- [x] A real press for Bo Girds and every team on the local API gives the same kind of Shortlist as before this ticket.

## Comments

The merge: `deadline-week-11` merged into `deadline-week` as a fast-forward before `562fddf1` on 2026-11-20; review fixes and the Judge fix round followed on the same branch.
The proof: `make check-fast` passed at each merge, and the Judge gave PASS to all 72 tests, AT-1 to AT-73 with AT-42 retired, after one fix round.
Read at least 5 files: AGENTS.md, .scratch/deadline-week/PRD.md, .scratch/deadline-week/ACCEPTANCE.md, docs/agents/issue-tracker.md, .scratch/deadline-week/issues/11-the-jev-requests-split-and-share-one-pacer.md.
Closes with the squash merge of the spec PR.
