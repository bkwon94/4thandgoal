# 10: Sell high or buy low

Spec: `.scratch/front-door/PRD.md`. Acceptance tests AT-27.

**App:** both

**What to build:** A new Advisor route `POST /sell-high` in the `analyzer` package uses Sonnet 5.5 and reuses the Playbook, the fact helpers, the verifier, and the Jev checks of the Advisor. Code puts each player's trade value, lineup value, trend of the last 4 weeks, and schedule ahead side by side. The Advisor picks the players and writes why. The Topic shows its steps, then the whole Answer.

**Blocked by:** 09

**Status:** ready-for-agent

- [ ] The Answer names at least one player on the roster of Lil Fridge to sell, with the reason (AT-27).
- [ ] The route reuses the verifier and the Jev checks of the Advisor. No math screen picks the players.
- [ ] The steps show before the whole Answer, as in ticket 09.
