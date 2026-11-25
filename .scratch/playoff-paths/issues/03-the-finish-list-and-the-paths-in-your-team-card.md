# 03: The Finish list and the Paths in Your team card

Spec: `.scratch/playoff-paths/PRD.md`. Acceptance tests AT-6 to AT-11, AT-30, AT-31, AT-32, AT-41, and AT-52.

**App:** both

**What to build:** Your team card opens in place and shows the Finish list as a bar chart, each Finish with its chance, its final record, and its odds of the Goal. A tap on a Finish shows its Paths with the copy of decision 06. A tap on another team on the board opens its Finish list in a sheet, with "Make this Your team". The sim loop writes the results of each run as it draws, and a greedy cover finds the Paths: it stops at 90% or 3 teams, needs 400 runs, and skips a repeated Path (decision 03). The build writes the Finish lists and the Paths into `sim.json`, in the small shape of decision 03.

**Blocked by:** 02

**Status:** done

- [x] The Finish list of Bo Girds in `cpc` week 11 runs 6-0 to 0-6, sums to 100% within 1 point, and gives 4-2 the final record 15-13.
- [x] A NorCal Finish list runs 4-0 to 0-4 with no median results.
- [x] Each Path names 1 to 3 teams, has 400 runs or more, and reaches 90% unless it names 3 teams or is the best chance.
- [x] A sure Finish and a Finish under 0.5% have no Path, and the page shows their copy.
- [x] The card and the sheet pass the WebKit overlap check at the 4 sizes, in light and dark mode.
- [ ] `make check-fast` passes.

## Comments

- Merged into `playoff-paths` as 3a28f997, 2026-11-25. Closes with the squash merge of the spec PR.
- Proof: `make check-fast` passed at each merge, and the Judge gave PASS to each test of this ticket in `VERDICTS.md`.
