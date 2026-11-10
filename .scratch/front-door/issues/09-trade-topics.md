# 09: The trade check and trade ideas

Spec: `.scratch/front-door/PRD.md`. Acceptance tests AT-24, AT-25, AT-26, AT-28, AT-58.

**App:** both

**What to build:** The trade check calls `POST /analyze`, and trade ideas calls `POST /find`, both as `manager-brain` left them. For a typed trade check, Jev picks each player from the real rosters. An unsure pick opens the Trade page with the form. The Advisor gets one optional stage callback, and the route sends each stage as a plain step before the whole Answer. Trade ideas runs in each client, whatever the `finder` flag of the page says.

**Blocked by:** 04

**Status:** ready-for-agent

- [x] A typed trade of a Lil Fridge player for a Bo Girds player shows the Lean, the Case, the top Bullets, and a Trade page link (AT-24).
- [x] The first sentence of the Case gives the reason for the Lean, and the fairness line agrees (AT-25).
- [x] Trade ideas on CPC show real `/find` offers for the weak spots of Lil Fridge (AT-26).
- [x] Plain steps show one by one before the whole Answer (AT-28).
- [x] "is my RB for their WR fair" opens the Trade page and fills no unsure player (AT-58).
- [ ] The commissioner sees the trade ideas Answer with real `/find` output before the PR, as decision 08 asks.
