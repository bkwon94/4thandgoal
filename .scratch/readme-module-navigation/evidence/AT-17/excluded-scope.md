Implementation revision: `dad744db4f3b49732adc1586e08c34be2f381f73`.
Base revision: `17f45a15d1c324e36beefd0da29b77fe56b7ef91`.
All source excerpts below come from Git objects at the stated revision.
No behavior test or cold task runs during this static capture.

The complete changed-file list is ../AT-16/document-scope.md. feature.diff contains the full feature diff.
Every changed path in the fixed implementation diff is Markdown. No module move, product code, test code, schema, or API contract file changes.
The product maps group responsibilities; they contain no T1–T6 answer table or exhaustive package catalogue.
The full 13 document snapshots appear in ../AT-5/document-duties.md for direct inspection.
No root README or separate API instruction file enters the diff.
Provider-refresh, saved-data, prompt-test, fact-selection, and build-behavior gaps receive no feature edit.
The current-roster projection route addresses one historical gap; it does not complete historical ticket 07.

## Historical ticket at implementation

## `.scratch/week-8-fixes/issues/07-the-readmes-name-the-module-an-agent-needs.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–19

```text
1: # 07: The READMEs name the module an agent needs
2: 
3: Spec: `.scratch/week-8-fixes/PRD.md`, "This is a test of the One vision". The files-read lines of tickets 01 to 06.
4: 
5: **What to build:** Six cold builders read 15 to 49 files each. Each named a README line that sent it right and
6: a line that was missing. Add the missing lines, under 25 lines per README, and fix the one wrong line in
7: `CLAUDE.md`. Add a README for the saved data layout.
8: 
9: **Blocked by:** none.
10: 
11: **Status:** ready-for-agent
12: 
13: - [ ] `src/cornerstone/README.md` Knows: the award picks, Matchup of the Week, and next week are models in `facts_league.py`; the roster projection behind the odds shift is `projected_totals` in `sheet/base.py`; the byes come from `NflverseWeek.bye_weeks`; the free agent pool has three rules in `ranks.in_pool`, the snapshot, and the waiver board; `NUMBER_TOKEN` lives in `sheet/base.py`.
14: - [ ] `src/cornerstone/sheet/README.md` Knows: a chapter picks its facts by the `M<n>.` id prefix in `assemble.py`; a fact reads nflverse data only through `Context.nfl`; `sheet/matchups.py` holds the wording of the lead and turn facts.
15: - [ ] `src/cornerstone/provider/README.md` Knows: a new field on the extract makes an old saved extract fetch again.
16: - [ ] `data/README.md`, new, outside the rule because it is no package: the layout `data/<season>/week-NN/raw/`, `history/week-NN/injuries.json`, `data/cache/nflverse/`; a fresh worktree has no cache; `raw/nflverse.json` saves only when every source is complete.
17: - [ ] `CLAUDE.md` pipeline step 2: the raw data sits under `data/<season>/week-NN/raw/`, not `data/cache/`. `page-json` re-renders saved facts only; a sheet change needs `make build`. `make build WEEK=N` reads the saved raw data and does not fetch Sleeper again.
18: - [ ] Tests: `tests/test_writer.py` holds the prompt rule tests. Say so in the sheet README under Does not do, or in `tests/README.md` if one exists.
19: - [ ] `make check` passes. The README rule passes.
```

## Historical ticket diff

```diff
```

## Deferred scope decision

## `.scratch/readme-module-navigation/decisions/02-grill-readme-coverage-and-structure.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 72–81

```text
72: ### Deferred historical gaps
73: 
74: Brian keeps the remaining gaps from `.scratch/week-8-fixes/issues/07-the-readmes-name-the-module-an-agent-needs.md` separate and open.
75: These gaps cover provider refresh, saved data, prompt tests, fact selection, and build behavior.
76: They exceed the six approved task routes and need separate scope decisions.
77: The projection route covers one historical gap at its current package path.
78: This feature does not complete ticket 07.
79: 
80: Brian approves this coverage, structure, size policy, and deferral.
81: This decision changes no README, agent instruction, code, or test procedure.
```

