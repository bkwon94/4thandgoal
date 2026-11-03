# 01: The level draw

**What to build:** In `src/cornerstone/odds.py`, replace the bootstrap draw with a level draw. Per run, each roster's level is `rng.gauss(mean, se)`, where `mean` is the shrunk season average and `se` is the league spread over the square root of `n + k`. Each remaining week's score is `rng.gauss(level, spread)` plus the projection shift the engine already computes. `spread` is the population standard deviation of every played score from its own roster's average, pooled over the league. `k` is a new tunable `LEVEL_SHRINK_WEEKS = 5` in `tunables.py`, with a comment that says why 5. Remove `_draw_weights`, `RECENT_WEEKS`, and `RECENT_WEIGHT`, and every reader of them. Update the odds docstring and any doc, ADR, or glossary line that says the odds draw from past scores. Run `make golden` and commit the rewritten files with the code.

**Prototype on the week 7 data, playoff odds in percent, main against this model:**

| Team | Record | Avg | Main | Level |
| --- | --- | --- | --- | --- |
| Lil Fridge | 10-4 | 118.5 | 99 | 94 |
| Bo Girds | 9-5 | 119.1 | 99 | 94 |
| London Cooking | 9-5 | 117.2 | 99 | 94 |
| All You Need Is Love | 9-5 | 104.8 | 76 | 71 |
| Maye d'force B with U | 7-7 | 111.4 | 49 | 61 |
| Brock 'N' Roll | 7-7 | 110.1 | 42 | 57 |
| Return of T Mac | 7-7 | 102.9 | 54 | 34 |
| Amon-Ra Dawg Your Team | 6-8 | 107.4 | 58 | 53 |
| Unsolicited Dak Picks | 6-8 | 100.1 | 15 | 25 |
| behold the lamb | 6-8 | 97.1 | 6 | 16 |

**Blocked by:** none

**Status:** done

- [x] `playoff_odds` draws a level per roster per run and a normal score per week around it.
- [x] `LEVEL_SHRINK_WEEKS` is in `tunables.py`. `RECENT_WEEKS`, `RECENT_WEIGHT`, and `_draw_weights` are gone.
- [x] A test shows that a roster with a wide spread of past scores gets no better odds than one with the same average and a narrow spread.
- [x] A test shows the shrink: with k above 0, a roster's drawn level sits between its average and the league average.
- [x] The week 7 odds from the saved data match the Level column above within 3 points.
- [x] `make golden` ran, and the golden diff is named in the close comment.
- [x] `ruff`, `make typecheck`, and the full suite pass.

## Comments

- 2026-11-02: merged into `main` from branch `odds-level-01-level-draw`, commits 1b135b1, aebd3e4, and e03a6f2. 1,483 tests collected. The week 7 odds from the saved data match the Level column exactly. Golden change: `facts.json` and `rankings.json` only, in the `ODDS.` and `SW.` facts and the odds rows of week 6; the rankings chapter drops `ODDS.2.why` because team 2 rose from 21 to 46. Week 6 top three: 99, 99, 99 to 96, 96, 91. `page.json` and `managers.json` unchanged. The projection shift keeps its gap from the raw average, since it measures the roster change and the shrink already sits in the level. Two notes for later: the pooled spread divides by the count of scores, so it reads about 7 percent low at 7 weeks; the wide-against-narrow test allows a 5-point gap. Two reviewers passed it after one fix pass.
