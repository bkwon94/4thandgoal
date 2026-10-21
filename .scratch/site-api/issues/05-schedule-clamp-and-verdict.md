# 05: Schedule, clamp, and verdict

**What to build:** The breakdown is complete. Schedule shows as for, against, or even per side and never moves a letter. The adjuster steps sum, clamp to two either way, and give the final letter. The verdict rule gives accept, counter, or decline for the asker with one reason. The six real week 6 trades become hand-worked base cases, and the analyze command prints the full breakdown and the code's verdict.

**Blocked by:** 04 (Trend, injury, and handcuff adjusters)

**Status:** ready-for-agent

- [ ] Schedule: byes left against byes done for the players got and gave, and the rank of the week 15 to 17 opponents in points allowed to the position. The result is for, against, or even. It adds no step.
- [ ] The sum of the adjuster steps is clamped to two either way. The final letter is the start letter plus the sum, clamped to A through F. The breakdown shows the start letter, each adjuster, and the final letter.
- [ ] Verdict: accept when the asker's letter is B or better, or C with the other side at C or worse. Decline when the asker's letter is D or worse. Counter otherwise. Schedule for the asker turns a counter into an accept. Schedule against turns an accept at C into a counter.
- [ ] The same proposed trade on the same snapshot returns the same breakdown every time.
- [ ] The clamp and the verdict bands join the tunable table. The rubric file states the schedule rule, the clamp, the letter meanings, and the verdict rule.
- [ ] The six real week 6 trades, graded on the week 6 snapshot, each have the start letter, the adjusters, and the final letter worked out by hand from the rubric and asserted in a test. The Josh Jacobs trade is among them.
- [ ] Tests at the grade seam: schedule for, against, and even; the clamp at plus three and minus three; each verdict branch and both schedule flips.
- [ ] `cornerstone analyze` with the skip-Claude flag prints the full breakdown per side, the verdict, and the as-of line.
- [ ] `uv run pytest -q` passes with no failed test.
