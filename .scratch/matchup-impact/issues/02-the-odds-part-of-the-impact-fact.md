# 02: The odds part of the impact fact

Spec: `.scratch/matchup-impact/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, and AT-7.

**App:** pipeline

**What to build:** The impact fact of each matchup gives the playoff odds of both teams before and after the week, as "playoff odds went from 99% to 86% this week". The odds before are last week's saved odds. The odds after are this week's. A week with no saved odds before it leaves the odds part out, and keeps the other parts. The weekly odds engine still runs once.

**Blocked by:** 01

**Status:** done

- [x] A test finds the odds part in `M<n>.impact` with both numbers as whole percents, the words "playoff odds", and the words "this week".
- [x] A test of a week with no saved odds the week before finds no odds part, and finds the other parts.
- [x] The odds after the week in the fact match the playoff odds that the same build saves for the team.
- [x] The build runs the odds engine once per week, as before.
- [x] The golden files hold the changed facts, and `make check` passes.
- [ ] Builds of `2026` weeks 6 and 8 record the evidence of AT-1, AT-2, AT-3, and AT-7 in `EVIDENCE.md`.

## Comments
- Closed by the merge of PR #2.
