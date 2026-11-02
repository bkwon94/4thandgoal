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

**Status:** ready-for-agent

- [ ] `playoff_odds` draws a level per roster per run and a normal score per week around it.
- [ ] `LEVEL_SHRINK_WEEKS` is in `tunables.py`. `RECENT_WEEKS`, `RECENT_WEIGHT`, and `_draw_weights` are gone.
- [ ] A test shows that a roster with a wide spread of past scores gets no better odds than one with the same average and a narrow spread.
- [ ] A test shows the shrink: with k above 0, a roster's drawn level sits between its average and the league average.
- [ ] The week 7 odds from the saved data match the Level column above within 3 points.
- [ ] `make golden` ran, and the golden diff is named in the close comment.
- [ ] `ruff`, `make typecheck`, and the full suite pass.
