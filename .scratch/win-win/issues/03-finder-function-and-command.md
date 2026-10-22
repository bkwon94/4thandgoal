# 03 — Finder function and command

**Repo:** pipeline. **Spec:** `.scratch/win-win/PRD.md`, phase 2.

**What to build:** A manager picks a partner team and gets the top three trades that are good for both. A finder function takes the asker's roster, the partner's roster, and the snapshot, grades every one-for-one swap and every two-for-one swap in both directions with the grade function, keeps the trades with the `win_win` state, and ranks them: the sum of both sides' adjuster steps up, then the higher of the two lower final letters, then the smaller gap between the two final letters, then the asker's letter. Three at most. A handcuff, a player out now with no return week on file, a kicker, and a defense are never candidates. A `cornerstone find` command takes the two roster ids and a week and prints the list, or the line that no swap between these rosters is good for both.

**Blocked by:** 01 — Fairness rule and document block.

**Status:** ready-for-agent

- [ ] The finder function in a new module, one level above the grade function. Tests on the week 6 snapshot with two fixture rosters: a pair with three or more win-wins returns three; a pair with one returns one; a pair with none returns the empty list.
- [ ] A handcuff never appears, with a test. An out player with no return week never appears, with a test. A kicker and a defense never appear, with a test.
- [ ] A two-for-one appears in both directions, with a test.
- [ ] The rank order holds on a tie, with a test per tie-break.
- [ ] A timing test on the week 6 snapshot. If one pair runs past a few seconds, cap the candidate pool at the top players by points per game on each roster, with the cap in the tunable table.
- [ ] `cornerstone find --season S --week N --asker A --partner B` prints the list or the empty line.
- [ ] `make test` passes. `make lint` stays at 123 or lower.
