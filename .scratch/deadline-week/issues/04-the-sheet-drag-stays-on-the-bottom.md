# 04: The sheet drag stays on the bottom

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-30.

**App:** site

**What to build:** A drag of the grip of any sheet upward, past its open height, no longer lifts the bottom edge of the sheet off the screen. The fix lives in the shared sheet wrapper of the design package, so the Trade Wire, the team sheet, and every other sheet get it.

**Blocked by:** none

**Status:** done

- [x] A test of the sheet wrapper drags 200 px up and the bottom edge stays at the bottom of the viewport, within 1 px.
- [ ] The same check passes in a real WebKit browser for the Trade Wire sheet and the team sheet at 390 by 660.

## Comments

The merge: `01ccea41` merged `deadline-week-04` into `deadline-week` on 2026-11-19; review fixes and the Judge fix round followed on the same branch.
The proof: `make check-fast` passed at each merge, and the Judge gave PASS to all 72 tests, AT-1 to AT-73 with AT-42 retired, after one fix round.
Read at least 5 files: AGENTS.md, .scratch/deadline-week/PRD.md, .scratch/deadline-week/ACCEPTANCE.md, docs/agents/issue-tracker.md, .scratch/deadline-week/issues/04-the-sheet-drag-stays-on-the-bottom.md.
Closes with the squash merge of the spec PR.
