# 02: The pooled spread divides by the degrees of freedom

Spec: `.scratch/odds-level/PRD.md`. The two notes in the close comment of ticket 01.

**What to build:** In `src/cornerstone/odds.py`, the pooled spread divides the sum of squares by the count of
scores. Each roster's average uses one degree of freedom, so the spread reads low. With 10 rosters and 7 weeks
the divisor is 70 where 60 is right, and the spread reads about 7 percent low. Divide by the count of scores
minus the count of rosters with two or more scores. Then tighten the wide-against-narrow test from a 5-point gap.

**Blocked by:** none. Merge after the week 8 page is live, so the week 8 build runs on the `main` that ticket 01
tested.

**Status:** ready-for-agent

- [ ] `spread` divides by `len(played) - rosters_with_two_or_more`. A roster with one score adds no square and no
  degree of freedom.
- [ ] If the divisor is 0, the spread is 0 and every draw is the mean. Keep the comment that says so.
- [ ] The comment above `spread` says why the divisor drops one per roster.
- [ ] The docstring of `playoff_odds` still reads true. Change "standard deviation" only if the sentence now lies.
- [ ] `test_a_wide_spread_of_past_scores_gives_no_better_odds_than_a_narrow_spread` runs 5000 runs and allows a
  3-point gap. If 3 fails at 5000 runs, say why in the close comment and keep 5.
- [ ] A test shows that two rosters with one score each give a spread of 0.
- [ ] `make golden` ran, and the golden diff is named in the close comment. Expect the odds to move toward 50
  by a point or two, because a wider spread adds noise.
- [ ] `ruff`, `make typecheck`, and the full suite pass.
