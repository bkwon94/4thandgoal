# 02: The known-games week

Spec: `.scratch/known-games/PRD.md`, "The known-games week", "A failed week N fetch", "The Tuesday roll".
Glossary: "Known games". Decision record: ADR 0002.

**What to build:** A live grade reads the week N games that have a stat line. The live raw fetch already holds
the week N stat lines from Sleeper. When week N has at least one stat line, the snapshot parses it with the same
parse as a saved week and adds it to the history for player stats. The player stat bound becomes N. The standings
bound stays N-1. Lineup value, recent points per game, target share, red zone touches, and the trend adjuster
then read the week N game of any player who played. The stamp gains a known-games block: the week, the count of
week N games read, the count in progress, and the pending counts by name. This ticket fills the games-read count
and leaves in-progress at zero and pending empty; tickets 03 and 04 fill them. The result document and the finder
document carry the block. A week N fetch with no stat lines, or an empty one, leaves the bound at N-1 and names
the stats as stale. A saved week grades exactly as today. The Tuesday roll and the history save do not change.

**Blocked by:** 01 (Two bounds in the stamp).

**Status:** done

- [ ] A live raw with week 7 stat lines for 26 teams and a history through week 6 gives a player stat bound of 7, a standings bound of 6, and a known-games block with 13 games read.
- [ ] A player with a week 7 line of 30 points has a recent points per game that counts it, and his roster's best lineup moves with it.
- [ ] The trend adjuster reads the week 7 target share of a player who played, and its reason names week 7 in the weeks.
- [ ] A player with no week 7 line yet keeps the points per game of weeks 1 to 6, and nothing reads his missing week as a zero game.
- [ ] The standings and the standing adjuster count the games of weeks 1 to 6 only.
- [ ] A live raw with no week 7 stat lines stamps the bound at 6, an empty known-games block, and names stats as stale.
- [ ] A saved week 6 fixture grades the same letters and reasons as before this ticket.
- [ ] On the Tuesday after the cutoff the raw week still joins the history as today and the known-games week is the new trade week with zero games read.
- [ ] The finder reads the same bound as the grader with no edit of its own.
- [ ] Real-data check: on a game day, `make analyze` with a player who played that day shows the block and a reason that quotes his game.

## Comments

- 2026-11-02: `main` holds the merge 67f1a4d. Status set to done by the state-file sweep of agent-habits 02.
