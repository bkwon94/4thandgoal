# 12: Buy low targets from other rosters

Spec: `.scratch/front-door/PRD.md`, story 34.

**App:** both

**What to build:** The Topic "Sell high or buy low" names players of Your team to sell, and no buy-low targets. Add buy-low targets from the other rosters: players whose facts say their trade value sits under what they give. The Advisor picks them and writes why, from the same facts side by side as the sell list. No code screen picks a player.

**Blocked by:** none. The front-door spec ships with sells only. Brian, 2026-11-10.

**Status:** wontfix

- [ ] The Answer names at least one player on another roster to buy, with the reason.
- [ ] The route reuses the sheet, the verifier, and the Jev checks of the sell high press.

## Comments

Closes as wontfix in the audit of `todoist-queue` on 2026-11-12. Brian deferred buy low, so it moves to the Ideas section of the queue.
Proof: No buy-low code exists, and `front-door-lineup` PRD story 50 keeps the sell list only. Brian deferred buy low on 2026-11-10, so he may prefer `needs-triage` until he picks a spec.
Read 1 file: .scratch/todoist-queue/audit.md.
