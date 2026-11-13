# 07: The READMEs name the module an agent needs

Spec: `.scratch/week-8-fixes/PRD.md`, "This is a test of the One vision". The files-read lines of tickets 01 to 06.

**What to build:** Six cold builders read 15 to 49 files each. Each named a README line that sent it right and
a line that was missing. Add the missing lines, under 25 lines per README, and fix the one wrong line in
`CLAUDE.md`. Add a README for the saved data layout.

**Blocked by:** none.

**Status:** wontfix

- [ ] `src/cornerstone/README.md` Knows: the award picks, Matchup of the Week, and next week are models in `facts_league.py`; the roster projection behind the odds shift is `projected_totals` in `sheet/base.py`; the byes come from `NflverseWeek.bye_weeks`; the free agent pool has three rules in `ranks.in_pool`, the snapshot, and the waiver board; `NUMBER_TOKEN` lives in `sheet/base.py`.
- [ ] `src/cornerstone/sheet/README.md` Knows: a chapter picks its facts by the `M<n>.` id prefix in `assemble.py`; a fact reads nflverse data only through `Context.nfl`; `sheet/matchups.py` holds the wording of the lead and turn facts.
- [ ] `src/cornerstone/provider/README.md` Knows: a new field on the extract makes an old saved extract fetch again.
- [ ] `data/README.md`, new, outside the rule because it is no package: the layout `data/<season>/week-NN/raw/`, `history/week-NN/injuries.json`, `data/cache/nflverse/`; a fresh worktree has no cache; `raw/nflverse.json` saves only when every source is complete.
- [ ] `CLAUDE.md` pipeline step 2: the raw data sits under `data/<season>/week-NN/raw/`, not `data/cache/`. `page-json` re-renders saved facts only; a sheet change needs `make build`. `make build WEEK=N` reads the saved raw data and does not fetch Sleeper again.
- [ ] Tests: `tests/test_writer.py` holds the prompt rule tests. Say so in the sheet README under Does not do, or in `tests/README.md` if one exists.
- [ ] `make check` passes. The README rule passes.

## Comments

Closes as wontfix in the audit of `todoist-queue` on 2026-11-12. Brian dropped it, because it fixes no real bug and changes nothing that a manager sees.
Proof: No README holds the lines the ticket asks for, and no `data/README.md` exists. The clients and package moves changed the target paths and the `CLAUDE.md` step 2 line, so the ticket needs new paths before an agent builds it.
Read 1 file: .scratch/todoist-queue/audit.md.
