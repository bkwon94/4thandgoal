# 04: Streaks, median games, and margins in the formula

**What to build:** Brian wants the power rank to weigh win streaks that count the median game, the margin of each win or loss, and points scored. Two components change; the weights stay equal at 0.25 each.

Form becomes three equal parts over the last 3 weeks:
1. The streak: wins or losses in a row, newest week back, counted over both games each week, the head-to-head and the median, the way Sleeper counts it. Scaled from -6 to 6 onto 0 to 1, with 0 at 0.5.
2. The record over the last 3 weeks, both games per week, wins over decided games.
3. The all-play rate over the last 3 weeks, as today.

Scoring becomes three equal parts over the season:
1. The points-for share, as today.
2. The all-play rate, as today.
3. The mean head-to-head margin per game, points for minus points against, scaled so the best is 1 and the worst is 0.

Standing and schedule played do not change. The streak fact `H.<rid>.streak` on the page stays head to head only; the formula's streak is its own number. The glossary gets "form streak" for the median-inclusive one, so the two do not blur. The `PR.` fact text does not change. The season file shape does not change, so the site needs no change.

Spec: `.scratch/rankings/pipeline/PRD.md`, section "The formula", amended by this ticket.

**Blocked by:** None. Main holds tickets 01 to 03.

**Status:** ready-for-agent

- [ ] Form is the mean of the three parts; a 4-game streak that counts a median win ranks above a 2-game head-to-head streak with the same record, on a built fixture.
- [ ] The form streak counts both games per week and breaks on the first loss or tie, newest week back.
- [ ] Scoring is the mean of the three parts; two teams with equal points for and equal all-play but different margins get different scoring values.
- [ ] A mutation that removes each new part fails a test.
- [ ] The glossary defines "form streak" and the formula section of the PRD is updated to this ticket's wording.
- [ ] `make rankings WEEK=6` on the real history runs clean; note the new week 6 top three and any team that moved 3 or more places against the old file, in a comment at the bottom of this file.
- [ ] `make test` passes. Lint count on the branch is no higher than 123.
