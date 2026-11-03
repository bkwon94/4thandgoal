# 05: Blurbs with more fun and more detail

Spec: `.scratch/week-8-fixes/PRD.md`, part 5.

**What to build:** The chapter blurbs read flat. Loosen the voice inside the tone rules, and ask for one more
concrete detail per blurb: the number, the player, or the turn that made the chapter. Use the facts ticket 03
found where they fit.

**Blocked by:** 03.

**Status:** done

- [x] Read the tone rules in `.scratch/tone/PRD.md` and the writer prompt. Name what you change and what you keep.
  - Changed: rules 30 and 31, the tone Humor bullet, the rule 29 game-time line, the verifier gate, the two-number code check, and the defense name in the player check.
  - Kept: rules 1 to 29, the opener, the banned words and phrases, the number rules, and the examples.
- [x] The prompt asks for one concrete detail per blurb and allows a light joke where the facts earn it.
- [x] The word bans and the number rules stay. A test shows that.
- [x] `make build WEEK=8` from the saved data. Paste three blurbs, before and after, in the close comment.
- [ ] Brian reads the page before the publish.
- [x] `make check` passes.

## Comments

- 2026-11-03: merged into `main` from branch `week-8-fixes-05-blurbs`, commits 5eb330e, 5af76a7, 9aadcc7, c239420, 3418eda, 31263dc, 5deeda7, 36acdaa, and 9e5611f, with `--no-ff`. 1536 passed, 9 deselected. Changed: writer rule 30 (one concrete detail per blurb), rule 31 (a rank or a comparison only from one fact), the rule 29 game-time line, the tone Humor bullet, the verifier gate on ranks with two allowances, a code check that fails a sentence with more than two numbers, and a defense-name skip in the player check that failed recap 4 on every build. Kept: rules 1 to 29, the opener, the banned words and phrases, the number rules, the examples. Three real builds: the first had 0 fallbacks and six unbacked sentences; the second, with the gate alone, had 5 fallbacks; the third, with the writer taught the rule, had 1 fallback, the rankings chapter, because the fact "1st in scoring" names a component and reads as most points. Blurbs before and after are in the builder reports of this session. The final page comes from the build on `main` after this merge. Note for later: the power rankings fact text "1st in scoring" needs "in the scoring component". Two reviewers passed each pass. Read 21 files on the first pass and 17 across the fix passes: CLAUDE.md, docs/agents/state.md, the ticket, the PRD, .scratch/tone/PRD.md, src/cornerstone/README.md, sheet/README.md, prompts/writer.md, tone.md, vocabulary.md, verifier.md, writer.py, verifier.py, names.py, models.py, power_rankings.py, sheet/base.py, sheet/matchups.py, tests/test_writer.py, tests/test_verifier.py, tests/test_pipeline.py, tests/conftest.py, GLOSSARY.md, Makefile, cli.py, data/2026/week-08 facts, blurbs, verify.
