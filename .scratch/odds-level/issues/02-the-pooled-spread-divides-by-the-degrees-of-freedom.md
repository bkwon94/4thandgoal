# 02: The pooled spread divides by the degrees of freedom

Spec: `.scratch/odds-level/PRD.md`. The two notes in the close comment of ticket 01.

**What to build:** In `src/cornerstone/odds.py`, the pooled spread divides the sum of squares by the count of
scores. Each roster's average uses one degree of freedom, so the spread reads low. With 10 rosters and 7 weeks
the divisor is 70 where 60 is right, and the spread reads about 7 percent low. Divide by the count of scores
minus the count of rosters with two or more scores. Then tighten the wide-against-narrow test from a 5-point gap.

**Blocked by:** none. Merge after the week 8 page is live, so the week 8 build runs on the `main` that ticket 01
tested.

**Status:** done

- [x] `spread` divides by `sum(len(scores[rid]) - 1 for rid in rosters)`, the pooled degrees of freedom. A roster
  with one score adds no square and no degree of freedom.
  - Choice: the ticket first said `len(played) - rosters_with_two_or_more`. That form gives a one-score roster one
    degree of freedom and makes the zero guard unreachable, so the standard form won.
- [x] If the divisor is 0, the spread is 0 and every draw is the mean. Keep the comment that says so.
- [x] The comment above `spread` says why the divisor drops one per roster.
- [x] The docstring of `playoff_odds` still reads true. Change "standard deviation" only if the sentence now lies.
- [x] `test_a_wide_spread_of_past_scores_gives_no_better_odds_than_a_narrow_spread` runs 5000 runs and allows a
  3-point gap. If 3 fails at 5000 runs, say why in the close comment and keep 5.
- [x] A test shows that two rosters with one score each give a spread of 0.
- [x] `make golden` ran, and the golden diff is named in the close comment. Expect the odds to move toward 50
  by a point or two, because a wider spread adds noise.
- [x] `ruff`, `make typecheck`, and the full suite pass.

## Comments

- 2026-11-02: merged into `main` from branch `odds-level-02-spread-divisor`, commits f062979, f79e0bd, 14b65e2, and b173494, with `--no-ff`. 1475 passed, 9 deselected. Golden change: `facts.json` and `rankings.json` only, in the `ODDS.` and `SW.` facts and the odds rows of week 6. Top three 96, 96, 91 to 96, 95, 90. Bottom three 18, 6, 1 to 18, 7, 1. Middle teams move 1 to 2 points toward 50. `page.json` and `managers.json` unchanged. Week 7 saved data: top three 94 to 93, every team within 2 points of the Level column. The wide-against-narrow gap is 0 at 5000 runs, so the test allows 3. The divisor is `sum(n_i - 1)`, not the formula the ticket first gave; the Choice bullet says why. Two reviewers passed it after one fix pass. Read 10 files: .scratch/odds-level/issues/02-the-pooled-spread-divides-by-the-degrees-of-freedom.md, .scratch/odds-level/PRD.md, .scratch/odds-level/issues/01-the-level-draw.md, src/cornerstone/odds.py, tests/test_odds.py, src/cornerstone/tunables.py, Makefile, tests/golden.py, tests/test_golden.py, pyproject.toml.
