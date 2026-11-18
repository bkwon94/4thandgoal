# 03: The page block and the weekly sim file

Spec: `.scratch/season-sim/PRD.md`. Acceptance tests AT-1, AT-6, AT-7, AT-8, AT-9, AT-10, and AT-64. Decisions 02, 04, and 07.

**App:** pipeline

**What to build:** One weighted sim gives a page block for a team by a split of its runs: the ladder and its sentence, the results of each week left, the odds after a loss, the root-for rows, and the "about" flag. The weekly build writes `week-NN/sim.json` in each week folder, with `teams`, 200 runs in `sample`, the inputs of the draw, a `pages` block with one page for each team, and the league fact of the Sim tile. The schema of the page block sits in the site schema of the sim package, next to the schema of `sim.json`. The season file `2026/sim.json` and `midseason.json` do not change.

**Blocked by:** 02.

**Status:** ready-for-agent

- [x] The sim step for `cpc` 2026 week 10 writes `week-10/sim.json` with 10,000 runs, 12 teams, 200 stored runs, and 12 pages (AT-1).
- [x] The ladder of Bo Girds lists each count of more wins, and the sentence names the smallest count with odds of 90 % or more (AT-6).
- [x] Week 11 of Bo Girds in `cpc` has four results against Maye d'force B with U, with wins added of 2, 1, 1, and 0 (AT-7).
- [x] Week 11 of Bo Girds in `norcal` has two results against The Mean Machine (AT-8).
- [x] The root-for rows follow the rules of the spec: at most 3, a lift of 1 point or more, whole numbers, ranked by the lift, a tie broken by the standings, and one of the five reasons (AT-9).
- [x] Each result whose chance times `effective_runs` is under 400 has the "about" flag, and no other result has it (AT-10).
- [x] `git diff main` of the season `sim.json` and `midseason.json` of each client is empty (AT-64).
- [x] The schema test of the site reads the new `week-10/sim.json` with no error.
- [x] `make check-fast` passes.
