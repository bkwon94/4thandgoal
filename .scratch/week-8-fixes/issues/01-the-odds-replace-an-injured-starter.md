# 01: The odds replace an injured starter

Spec: `.scratch/week-8-fixes/PRD.md`, part 1.

**What to build:** In the playoff odds, a starter whose projection is zero because of an injury is replaced
by the better of the best bench player and the best waiver player at that position. The projection shift
then measures the real roster, not a hole. Any position, not only QB. Week 8 case: Lamar Jackson, listed Out.

**Blocked by:** none.

**Status:** done

- [x] Find where the odds engine builds each roster's projection and the projection shift. Name the module in the close comment, and say how you found it.
- [x] An injured starter is a starter with a zero projection and an injury status that is not healthy. A healthy starter with a zero projection is not replaced; say why in a comment.
- [x] The replacement is the better projection of the best bench player and the best waiver player at that slot's position. A flex slot takes any of its positions.
- [x] The waiver pool is the free agents the data already holds. No new fetch.
- [x] A test with one injured QB starter and a bench QB at 15 points shows the roster's projection rises by 15.
- [x] A test with no bench QB and one waiver QB at 12 points shows the rise of 12.
- [x] A test with a healthy zero-projection starter shows no change.
- [x] The week 8 odds from the saved data change for the rosters with an injured starter. Name each one and its before and after in the close comment.
- [x] `make golden` ran, and the golden diff is named in the close comment.
- [x] `make check` passes.

## Comments

- 2026-11-03: merged into `main` from branch `week-8-fixes-01-odds`, commits a83e081, 1f34b39, and 9e5f61a, with `--no-ff`. 1510 passed, 9 deselected. The roster projection behind the shift sits in `projected_totals` of `src/cornerstone/sheet/base.py`, found through the sheet README's odds line and the callers of `odds.py`. The parse now reads the injuries and the pool from the players and projections files; the cover reads the pool only, because `fill_slots` already seats the best bench player. No cover in a bye week, from `NflverseWeek.bye_weeks`. No golden change: the week 6 fixture holds no pool, so the PRD line about the golden odds was wrong for this ticket. Week 8 from the saved data: only Bo Girds has an injured starter at zero, Lamar Jackson; playoff odds 59 to 76, bye 13 to 25, seed 6 to 4. The first pass gave 78; the bye fix caught Baltimore's week 13 bye. Other rosters move 0 to 4 points. Notes for later: a shared `pool.py` leaf module for the four pool rules; a Questionable starter at zero counts as injured, which has no week 8 case. Vision finding: no README names `sheet/base.py` as the home of the roster projection, nor `facts_league.py` for the byes. Two reviewers passed it after one fix pass. Read 31 files on the first pass and 11 on the fix pass: CLAUDE.md, docs/agents/state.md, the ticket, the PRD, src/cornerstone/README.md, sheet/README.md, provider/README.md, odds.py, sheet/base.py, adjusters.py, models.py, data/2026/week-08/raw/projections_ahead.json, parse.py, pipeline.py, config.py, snapshot.py, waiver.py, ranks.py, tests/test_layers.py, history.py, provider/raw.py, .scratch/odds-level/PRD.md, GLOSSARY.md, Makefile, tests/golden.py, tests/test_sheet.py, tests/test_parse.py, pyproject.toml, provider/sleeper.py, facts_league.py, nflverse.py.
