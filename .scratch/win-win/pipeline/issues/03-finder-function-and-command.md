# 03 — Finder function and command

**Repo:** pipeline. **Spec:** `.scratch/win-win/pipeline/PRD.md`, phase 2.

**What to build:** A manager picks a partner team and gets the top three trades that are good for both. A finder function takes the asker's roster, the partner's roster, and the snapshot, grades every one-for-one swap and every two-for-one swap in both directions with the grade function, keeps the trades with the `win_win` state, and ranks them: the net sum of both sides' adjuster steps, up and down, then the higher of the two lower final letters, then the smaller gap between the two final letters, then the asker's letter. It walks the ranked list and keeps a trade only when none of its players is in a trade it kept before, and it stops at three. A handcuff, a player out now with no return week on file, and an unlisted player are never candidates. An unlisted player has no row on the chart week's chart, so a trade with him starts both sides at C by rule. The chart lists no kicker and no defense, so they are always unlisted. A `cornerstone find` command takes the two roster ids and a week and prints the list, or the line that no swap between these rosters is good for both.

**Blocked by:** 01 — Fairness rule and document block.

**Status:** done

- [x] The finder function in a new module, one level above the grade function. Tests on the week 6 snapshot with two fixture rosters: a pair with three or more win-wins returns three; a pair with one returns one; a pair with none returns the empty list.
- [x] A handcuff never appears, with a test. An out player with no return week never appears, with a test. An unlisted player never appears, with a test. A kicker and a defense never appear, with a test.
- [x] The three trades share no player, with a test on a pair whose best win-wins share one.
- [x] A two-for-one appears in both directions, with a test.
- [x] The rank order holds on a tie, with a test per tie-break.
- [x] A timing test on the week 6 snapshot. If one pair runs past a few seconds, cap the candidate pool at the top players by points per game on each roster, with the cap in the tunable table.
- [x] `cornerstone find --season S --week N --asker A --partner B` prints the list or the empty line.
- [x] `make test` passes. `make lint` stays at 123 or lower.

## Comments

2026-10-22: The finder is `find_win_wins` in `src/cornerstone/finder.py`, with `candidates` and `rank` as its two inner seams. A handcuff on his own roster now is out of the pool, through `is_handcuff`. A trade that makes a player a handcuff on the roster that gets him is out of the candidates, through `trade_handcuffs`. Both use one depth chart test in `adjusters.py`. `cornerstone find` prints the as-of lines, then each trade with its two sides and the fairness lines of `analyze`.

With chart rows for every player of both rosters, the slowest pair, rosters 5 and 9, has 2,197 candidates and takes about 3 seconds. That is inside a few seconds, so the candidate pool has no cap and `FINDER_POOL` is not in the tunable table. `FINDER_TOP` is in the tunable table. The timing test has a bound of 5 seconds.

Three rules changed after the first count. An unlisted player is never a candidate, so no kicker and no defense is a candidate either. The rank uses the net sum of the steps, up and down. The three trades share no player. The reason: the fixture chart lists 25 players, so the first count of 33 of 66 pairs measured the fixture, not the quality of the trades.

With unlisted players out, the 66 week 6 pairs give no win-win on the fixture. The count tests give chart rows to the players they need. The live chart is the real test after the merge.
