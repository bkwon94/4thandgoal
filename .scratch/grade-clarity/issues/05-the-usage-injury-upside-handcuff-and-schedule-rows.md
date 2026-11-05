# 05: The usage, injury, upside, handcuff, and schedule rows

Spec: `.scratch/grade-clarity/PRD.md`. Acceptance tests AT-24, AT-25, AT-26, and AT-36.

**App:** pipeline

**What to build:** The other rows read as decision 03 says. Usage gives one clause for each player with the shares of the position. The injury row gives the return week and the weeks on the injury report. The upside row and the handcuff row use plain words. The schedule row names each playoff opponent with its rank at the position.

**Blocked by:** 04.

**Status:** ready-for-agent

- [ ] Usage gives the snap share, the target share, and the air yards per target for WR and TE, and the snap share, the carry share, and the target share for RB. QB gets no usage row. No week and no route share show.
- [x] The injury row reads in the form "Cooper is out until week 11. He was on the injury report in 5 of 8 weeks."
- [x] The handcuff row reads in the form "Spears backs up your RB, Pollard, on the Titans depth chart." The upside row reads in the form "Spears gets more work while Pollard is out."
- [x] The schedule row names each playoff opponent with its rank in points allowed at the position, such as "TEN (3rd most points to WRs)". The sentence "The schedule leans for this side" is gone.
- [x] `make check-fast` passes at the root.

## Comments

- Box 1 stays open for Brian. A QB has no usage clause, but the trend step still reads the snap share and the target share of a QB, because the letter math must not change. So a QB whose share moved gets a clause with that share only, such as "Jackson plays 76% of the snaps (down).", and a QB with flat shares gets none. A trade of QBs with flat shares has no usage row. The rest of box 1 holds: WR and TE give the snap share, the target share, and the air yards per target, RB gives the snap share, the carry share, and the target share, and no week and no route share show.
- The usage clause puts "(up)" or "(down)" after a snap share or a target share that moved, because the step reads those moves. The carry share and the air yards per target have no mark. The carry share and the air yards per target read the same weeks as the target share.
- When every share is flat and a tie break makes the step, the usage row ends with a plain clause: "the shares are flat, and the players you get have more red-zone use", or "the shares are flat, and the receivers you get gain WOPR, a mix of target share and air yards share". Brian checks these words.
- The injury row names each player it gets who is out now, with his return week, even with no step, because AT-36 asks for the return week. A player out with no returns row reads "is out with no return week on file." The count reads "in 5 of 8 weeks", where 8 is the last completed week.
- The upside row with no return week on file reads "Hampton is a top RB, out now with no return week on file." Brian checks it.
- The handcuff row of a backup with too many carries reads "Henderson backs up your RB, Stevenson, on the Patriots depth chart, but he takes 38% of the carries, so he is no handcuff."
- The schedule row names only the players the side gets, so each side card names its own players. The lean, and so the mark, still compares them with the players it gives. A bye in the trade week or the next week is the Week line's fact, so the row names only a later bye. A side that gets no player with a schedule, and has an even lean, hides the row. The playoff weeks are `PLAYOFF_WEEKS` in `league/nflverse.py`, 15 to 17. No client sets other weeks now.
- The opponent-rank helper for ticket 06: `opponent_rank(allowed, opponent, position)` and `most_points_text(rank, position)` in `packages/league/python/src/league/points_allowed.py`. `most_points_text(3, "WR")` gives "3rd most points to WRs". `ordinal` of `league/numbers.py` gives the short form "8th".
- The team nicknames are in `packages/league/python/src/league/nfl_teams.py`, from the 32 team defenses of the Sleeper players file.
- The fairness line: a side with no step up now shows its deal row, such as "You get far more than you give.", in place of the start reason with "trade value". `deal_reason` moved from `routes.py` to `rubric.py`, so the fairness and the deal row share it. The finder cards show the same words, and their look does not change. A test checks the fairness reasons of each one-for-one trade of three roster pairs for inner words.
- `DOCUMENT_VERSION` goes to 15. The API and site fixtures now hold the row text of a real run.
- A real run on the saved week 8 data and the shared nflverse cache, with roster 4 sending Spears to roster 12 for Emanuel Wilson, gives the handcuff row "Spears backs up your RB, Pollard, on the Titans depth chart." and the injury row "Spears is out with no return week on file. He was on the injury report in 5 of 8 weeks." Trade A gives the usage row of AT-24 and the schedule row "Washington faces HOU (5th most points to WRs), DAL (7th), and WAS (14th) in weeks 15 to 17."
