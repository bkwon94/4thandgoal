# 06: Moves

**What to build:** the Moves chapter lists the team's adds with the bid, the drops, and the trades per week, newest first. A week with no moves reads "No moves." The season totals of adds, drops, and trades sit at the top of the chapter. Both repos.

**Blocked by:** 03 The routes, the index, the hero, and the menu

**Status:** ready-for-agent

- [ ] The move model gains the drops, read from the saved transactions. Existing readers of the model do not change.
- [ ] Each entry carries the moves per saved week: the adds with the bid, the drops, and the trades with both sides and the players each gave. Plus the season totals.
- [ ] The managers module tests cover a roster with no moves, a free agent add with no bid, and a trade.
- [ ] The chapter lists the weeks newest first. An empty week shows one quiet line.
- [ ] A trade row shows both sides with headshots, as the Trades chapter of the week page does.
- [ ] The page tests read the order, the empty line, and the totals. All checks pass in both repos.
