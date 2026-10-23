# 01 — Rank why fact

**What to build:** the sheet holds one `PR.{roster_id}.why` fact per team that names the component
that moved most since last week and the game behind it. A mover reads "{team} moved up 3 places after
a 61-point win over {opponent}, the 1st-place team: form rose from 9th to 3rd." A held team reads
"{team} held 7th: scoring sits 4th, schedule played 11th." The first week of the rankings has no fact.
Demo: print the 12 texts from the week 6 fixture bundle.

Spec: `.scratch/reasons/PRD.md`, "The rank why".

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] One `PR.{roster_id}.why` fact per team from week 2 of the rankings on; none in week 1.
- [ ] The moved component is the one whose rank changed most between week N-1 and week N; ties go to the first in component order.
- [ ] The game is last week's head-to-head game: the opponent, the margin as a whole number, win or loss or tie, and the opponent's standing place before this week.
- [ ] A team with no rank move names its best and its worst component.
- [ ] Every digit in the text is in the fact's numbers, so the bundle checks pass.
- [ ] Tests on the week 6 fixture: a mover, a held team, the opponent's place, a tie reads "a tie with".
- [ ] Ruff adds no finding from the diff; the full suite passes.
