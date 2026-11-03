# 02: A player can win two awards

Spec: `.scratch/week-8-fixes/PRD.md`, part 2.

**What to build:** Joe Burrow earned Top Scorer and Game Changer in week 8, and a rule gave him one. Find the
rule that keeps a player to one award and remove it. Each award picks its own winner.

**Blocked by:** none.

**Status:** done

- [x] Find the rule. Name the module and the line in the close comment, and say how you found it.
- [x] Remove it. Keep a comment that says each award picks its own winner, and why: a reader expects the top scorer to be the top scorer.
- [x] If a test asserted the one-award rule, change it to assert the new rule.
- [x] A test shows one player wins two awards when the numbers say so.
- [x] The week 8 awards from the saved data show Joe Burrow in both. Name the two blurbs' first sentences in the close comment.
- [x] `make golden` ran, and the golden diff is named in the close comment.
- [x] `make check` passes.

## Comments

- 2026-11-03: merged into `main` from branch `week-8-fixes-02-awards`, commits 448ecf5, 58b9878, and 46d81fe, with `--no-ff`. 1505 passed, 9 deselected. The rule was the `picked` loop in `awards()` of `src/cornerstone/facts_league.py`, found through `sheet/awards.py` and a grep for `skipped`, with a second copy in `expected_awards()` of `facts_nflverse.py`. Both are gone, and the dead `Award.skipped` field with them; the site never read it. Golden diff: `facts.json` and `page.json` drop the `skipped` keys only, because no week 6 player held two awards. Week 8 from the saved data: Joe Burrow is Game Changer, Top Scorer, and Overachiever. The blurb sentences come from the `make build` of ticket 04. Open for Brian: a cap of two tiles per player. Vision finding: no README names `facts_league.py` as the home of the award picks, and `page-json` re-renders saved facts only, so a sheet change needs a build. Two reviewers passed it after one fix pass. Read 18 files: CLAUDE.md, docs/agents/state.md, the ticket, the PRD, src/cornerstone/README.md, sheet/README.md, sheet/__init__.py, sheet/awards.py, facts_league.py, models.py, facts_nflverse.py, tests/test_facts_league.py, tests/test_facts_nflverse.py, Makefile, cli.py, pipeline.py, sheet/base.py, data/2026/week-08/facts.json.
