# 02 — Odds why fact

**What to build:** the sheet holds one `ODDS.{roster_id}.why` fact per team, beside the odds facts,
that reads "{team} projects 112 a week from here against a 101 pace, with the 3rd easiest remaining
schedule." The projected pace is the mean of the projected best-lineup totals over the weeks left.
The season pace is the mean of the played-week scores. The remaining schedule is the mean season pace
of the opponents left, ranked 1 to 12 with 1 the easiest. The fact exists only when the odds facts
exist. Demo: print the 12 texts from the week 6 fixture bundle.

Spec: `.scratch/reasons/PRD.md`, "The odds why".

**Blocked by:** None — can start immediately.

**Status:** done

- [x] One `ODDS.{roster_id}.why` fact per team when the odds facts exist; none otherwise.
- [x] The projected pace and the season pace round to whole points.
- [x] The remaining schedule rank is 1 for the easiest, ties by roster id.
- [x] A team with no projected totals gets no why fact.
- [x] Every digit in the text is in the fact's numbers, so the bundle checks pass.
- [x] Tests on the week 6 fixture: the paces match the means of the inputs; the easiest schedule is rank 1; no projections means no fact; no odds means no why.
- [x] Ruff adds no finding from the diff; the full suite passes.
