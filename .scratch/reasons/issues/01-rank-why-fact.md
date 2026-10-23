# 01 — Rank why fact

**What to build:** the sheet holds one `PR.{roster_id}.why` fact per team that names the component
that moved most since last week and the game behind it. A mover reads "{team} moved up 3 places after
a 61-point win over {opponent}, the 1st-place team: form rose from 9th to 3rd." A held team reads
"{team} held 7th: scoring sits 4th, schedule played 11th." The first week of the rankings has no fact.
Demo: print the 12 texts from the week 6 fixture bundle.

Spec: `.scratch/reasons/PRD.md`, "The rank why".

**Blocked by:** None — can start immediately.

**Status:** done

- [x] One `PR.{roster_id}.why` fact per team from week 2 of the rankings on; none in week 1.
- [x] The moved component is the one whose rank changed most between week N-1 and week N; ties go to the first in component order.
- [x] The game is last week's head-to-head game: the opponent, the margin as a whole number, win or loss or tie, and the opponent's standing place before this week.
- [x] A team with no rank move names its best and its worst component.
- [x] Every digit in the text is in the fact's numbers, so the bundle checks pass.
- [x] Tests on the week 6 fixture: a mover, a held team, the opponent's place, a tie reads "a tie with".
- [x] Ruff adds no finding beyond E501 at the repo's line width; the full suite passes.
