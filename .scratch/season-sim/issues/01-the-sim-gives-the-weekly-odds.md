# 01: The sim gives the weekly odds, and the old odds engine goes away

Spec: `.scratch/season-sim/PRD.md`. Acceptance tests AT-2, AT-3, AT-4, and AT-5. ADR 0037.

**App:** pipeline

**What to build:** The weekly build takes the playoff odds, the bye odds, the seeds, and the swing of each game next week from the sim package, at 10,000 runs. The rankings page, the week page, and the facts show the odds of the sim. The old odds engine of the rankings package and its parity test go away. The odds of weeks 1 to 9 in `rankings.json` stay as they are.

**Blocked by:** none.

**Status:** ready-for-agent

- [ ] A rebuild of `cpc` 2026 week 10 writes `rankings.json` with week 10 odds equal to the odds of the sim (AT-2).
- [ ] Each odds number in the facts of `cpc` week 10 equals the number of the sim (AT-3).
- [ ] `git diff main` shows no change to the odds of weeks 1 to 9 in `rankings.json` (AT-4).
- [ ] No module imports the old odds engine, and its file and parity test are gone (AT-5).
- [ ] The cases of the old odds test that still apply now run against the sim: the odds, the status, the seed, and the swing.
- [ ] `make check-fast` passes.
