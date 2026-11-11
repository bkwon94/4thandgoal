# 42: A ranking of the teams of the league passes the check

Spec: `.scratch/front-door/PRD.md`. Source: H29 of `.scratch/front-door/HANDS-ON.md`.

**App:** API

**What to build:** "who are the highest scoring teams this season" ends as the honest miss, after two failed checks. Find the cause from the failed sentences in the log (ticket 26 logs each one with its noul), then fix it with the least change. Lesson of tickets 26 and 28: a field whose meaning Jev cannot read fails a true sentence.

**Blocked by:** 41

**Status:** done

- [x] The cause, with the failed sentences and their nouls.
- [x] Live: the question gives a list of the teams by points for, checked, in 3 of 3 runs.
- [x] The block eval stays at 17 of 20 or better.

## Cause

The standings result holds two ranks and no field meanings. `rank` is the place in the standings, and the teams come in that order. `points_for_rank` is the place by points. Jev read a row of a list by points against `rank`, or sorted close totals by eye, and doubted the true rows:

- 0.60, 0.48, 0.54: `Row 3 of the list "Points scored this season": Maye d'force B with U, 10-8, 1007.36.` Its `rank` is 7 and its `points_for_rank` is 3.
- 0.67, 0.70: `Row 4 of the list "Points scored this season": Lil Fridge, 11-7, 1004.64.`
- 0.69, 0.68: `Row 2 of the list "Points scored this season": Puka Deez..., 11-7, 1030.45.`

Each claim of row 3 alone passed at 0.91 or more. The tag form and the "..." of the name did not change the nouls.

## Fix

The standings result now holds `what_each_field_means` and `teams_by_points_for`, the team names by points for, most first. A probe of 10 samples: with the meanings only, 3 of 50 rows failed (row 4, min 0.65). With both, 0 of 50 failed (min 0.92).

## Evidence

- Before: 2 of 3 live runs ended as the honest miss.
- After: 3 of 3 live runs checked on the first text, with a list of 5 teams by points for.
- Block eval: 19 of 20. Case 5 now gives a list.

## Comments
- Closes with the squash merge of the spec PR.
