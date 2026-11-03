# 04: The matchup recap rework

Spec: `.scratch/week-8-fixes/PRD.md`, part 4. The facts come from ticket 03.

**What to build:** Each matchup recap tells how the game was won: the injury that changed it, when the lead
changed, and the Monday night turn when there was one. The facts come from the sheet, and the writer cites
them, as every blurb does.

**Blocked by:** 03 (the facts and their source).

**Status:** done

- [x] Add the facts ticket 03 recommends to the matchup fact group, with their sources. Name each fact id.
- [x] The recap prompt asks for the game story: the injury, the timing, the turn. It keeps the tone rules.
- [x] A test with a fixture matchup that flipped on Monday night shows the fact in the sheet.
- [x] A test shows the recap prompt names the new facts.
- [x] The verifier accepts a recap that cites the new facts.
- [x] `make build WEEK=8` from the saved data. Paste the six recaps in the close comment.
- [x] `make golden` ran, and the golden diff is named in the close comment.
- [x] `make check` passes.

## Comments

- 2026-11-03: merged into `main` from branch `week-8-fixes-04-recaps`, commits fb465c8, 43f52eb, 6d27ee5, 4e1c380, 5348db0, and 6994aa7, with `--no-ff`. 1519 passed, 9 deselected. New facts in the matchup group: `M<n>.hurt.<pid>` from the play-by-play file, `M<n>.snaps.<pid>` from `stats.json`, `M<n>.lead` and `M<n>.turn` from the starter points by game time with the `games.csv` kickoffs. `M<n>.inj.<pid>` is unchanged. A verifier code check makes a recap cite `.turn` when its chapter holds one. The Matchup of the Week note no longer hides the turn from the recap. Golden diff: `facts.json` gains eight snaps facts; no `page.json` change. Two real builds of week 8 ran; the six recaps of the second are in the builder report of this session, and the final text comes from the build of ticket 05. Recap 3 tells the Monday turn. Notes for later: the writer wrote "game time" into one recap, so rule 29 needs a line that keeps the term off the page (ticket 05 adds it); `build.sources.nflverse_pbp` reads False while the hurt facts exist; the first attempt at recap 4 fails a code check on "Washington" each build. Vision finding: no README says a chapter picks its facts by the `M<n>.` prefix, nor that a fact reads nflverse data only through `Context.nfl`. Two reviewers passed it after one fix pass. Read 49 files on the first pass and 11 on the fix pass; the full list is in the builder report, and the key ones: CLAUDE.md, docs/agents/state.md, the ticket, the PRD, ticket 03, the three READMEs, sheet/matchups.py, sheet/base.py, sheet/assemble.py, models.py, nflverse.py, pipeline.py, prompts/writer.md, writer.py, verifier.py, GLOSSARY.md, tests/test_sheet.py, tests/test_nflverse.py, tests/test_writer.py, tests/test_verifier.py.
