# 04: The matchup recap rework

Spec: `.scratch/week-8-fixes/PRD.md`, part 4. The facts come from ticket 03.

**What to build:** Each matchup recap tells how the game was won: the injury that changed it, when the lead
changed, and the Monday night turn when there was one. The facts come from the sheet, and the writer cites
them, as every blurb does.

**Blocked by:** 03 (the facts and their source).

**Status:** ready-for-agent

- [ ] Add the facts ticket 03 recommends to the matchup fact group, with their sources. Name each fact id.
- [ ] The recap prompt asks for the game story: the injury, the timing, the turn. It keeps the tone rules.
- [ ] A test with a fixture matchup that flipped on Monday night shows the fact in the sheet.
- [ ] A test shows the recap prompt names the new facts.
- [ ] The verifier accepts a recap that cites the new facts.
- [ ] `make build WEEK=8` from the saved data. Paste the six recaps in the close comment.
- [ ] `make golden` ran, and the golden diff is named in the close comment.
- [ ] `make check` passes.
