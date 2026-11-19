# 04: The sheet drag stays on the bottom

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-30.

**App:** site

**What to build:** A drag of the grip of any sheet upward, past its open height, no longer lifts the bottom edge of the sheet off the screen. The fix lives in the shared sheet wrapper of the design package, so the Trade Wire, the team sheet, and every other sheet get it.

**Blocked by:** none

**Status:** in-review

- [x] A test of the sheet wrapper drags 200 px up and the bottom edge stays at the bottom of the viewport, within 1 px.
- [ ] The same check passes in a real WebKit browser for the Trade Wire sheet and the team sheet at 390 by 660.
