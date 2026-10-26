# 11: A backup with real usage is not a handcuff

Brian's case on 2026-10-26: Blake Corum backs up Kyren Williams on the depth chart but carries the ball a lot.
The handcuff rule reads the depth chart only, so it counts him as insurance: zero lineup value in the roster
fit sums, no step up from the trend adjuster, and never in a finder trade. He has value of his own.

**What to build:** A running back is a handcuff only when his own usage is thin. The handcuff test gains one
gate: his carry share over his last 3 played games, which count the known games. At or above the gate he is
not a handcuff, and every adjuster and the finder grade him as any running back. Below it he is insurance, as
today. The gate is a tunable, 30 percent of his team's carries to start, with a why comment. A player with
fewer than 2 played games, or with no carry data, keeps the depth chart answer. The handcuff reason names the
share when the gate frees a backup: "Corum backs up the team's own starter but takes 38% of the carries, so he
counts as a running back." The glossary entry "Handcuff" says what a handcuff is with the gate.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] A backup running back at 38% carry share over his last 3 played games is not a handcuff: his lineup value counts in roster fit, the trend adjuster can step for him, and the finder can trade him.
- [ ] A backup at 15% carry share is a handcuff, as today.
- [ ] A backup with 1 played game, or with no carry data, keeps the depth chart answer.
- [ ] The handcuff reason names the share when the gate frees a backup.
- [ ] The known games count: a Thursday breakout changes the answer on a Saturday grade, with a test on the known-games snapshot.
- [ ] The gate is in the tunables file with a why comment.
- [ ] The glossary "Handcuff" entry states the gate in plain words.
- [ ] Real-data check: the hand-worked week 6 trades in the rubric tests, with the old and new values named in the report for any that change.
