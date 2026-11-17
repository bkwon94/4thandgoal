# 05: Stage lines

Spec: `.scratch/analyzer-stage/PRD.md`. Acceptance tests AT-6, AT-7, AT-8, AT-9, and AT-14.

**App:** site

**What to build:** During the grade wait, stage lines cycle under the title, one every 2.5 s. One pure function builds 12 lines from the trade on the stage: line 1 "Weighing the sides", line 12 "Weighing it all together", and between them general lines from the measures of the grade mixed with lines that name a player, a team, or a manager of the trade. After line 12, the list starts again at line 2. No line names an internal part, says "rival", or says that a step is done. The lines use the thinking states and shimmer text recipes of transitions.dev. They are hidden from a screen reader, and the status keeps one label, "Grading the trade". With motion off, a line swaps with no shimmer. The lines run in the grading hero of today. Add the glossary term "Stage line" from the spec.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] A unit test gives 12 lines for trade T and for a real trade of three sides, with the fixed first and last lines and none of the banned words.
- [ ] Over 10 s of a held wait, 4 different lines show, the first one "Weighing the sides".
- [ ] Over 30 s of a held wait, at least one line names a player, a team, or a manager of trade T.
- [ ] Two snapshots of the accessibility tree, at 2 s and 7 s, show only the status "Grading the trade".
- [ ] With reduced motion on, the line still changes about every 2.5 s, with no shimmer.
- [ ] `GLOSSARY.md` defines "Stage line".
