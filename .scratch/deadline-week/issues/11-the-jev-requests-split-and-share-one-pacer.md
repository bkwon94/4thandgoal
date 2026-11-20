# 11: The Jev requests split under 64k and share one pacer

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-63, AT-64, and AT-71.

**App:** api

**What to build:** A partner with more offers than one Jev request can hold sends them in several requests, each under the 64k context of one request, so no offer passes as unsure because a request was too large. Every press in the API process shares one pacer, so two managers who press at once stay under the account limit of 100,000 tokens per second. No request sends the long-context header of TypeSafe. Today's press keeps working the same way. This is the prefactor that lets the larger lists of tickets 12 and 13 run safely (decisions 14 and 16).

**Blocked by:** none

**Status:** ready-for-agent

- [ ] A test with one partner of 1,200 offers sends 3 or more requests, each under 64,000 tokens by the estimate, and no offer passes as unsure.
- [ ] A test with a fixed clock and two presses of 300,000 tokens each, at once, never holds more than 100,000 tokens in one second.
- [ ] No Jev request of a real press sends `TypeSafe-Danger-Zone-Long-Context`.
- [ ] A real press for Bo Girds and every team on the local API gives the same kind of Shortlist as before this ticket.
