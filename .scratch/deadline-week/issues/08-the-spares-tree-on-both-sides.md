# 08: The Spares tree on both sides

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-42, AT-43, AT-44, and AT-45.

**App:** api

**What to build:** The Spares tree replaces the four big questions of the Partner filter. For a pair of teams, code lists each player of one team at the position of a weak starting slot of the other team, when the giving team has a backup above the line behind him who can play now. A player who is Out is never cover. Jev asks one Noul per listed player: "Would {player} start over {weak starter} of {team} for the rest of the season?", with the trade chart value of both players as facts. The tree runs on both sides of a pair. A side stops only if it lists no player, or if each listed player gets a clear no, below `NO_AT` 0.3. An unsure answer passes. A failed Jev call is an error, never a stop. With one picked partner, the Finder skips the Partner filter. The Shortlist holds the best offer for each player that the asker gives and for each partner, before more forms of the same trade. The weak-slot rule, `YES_AT`, and `NO_AT` do not change.

**Blocked by:** 06

**Status:** ready-for-agent

- [ ] A test on fixed rosters lists no starter whose only backup is Out, and lists each listed player with a backup who can play now.
- [ ] A test with fixed Jev answers of 0.2, 0.5, and a failed call shows a stop, a pass, and an error.
- [ ] A real press for Bo Girds with Teehee (roster 12) logs no Partner filter step and holds 2 or more offers.
- [ ] The Shortlist of a real press repeats no player of the asker and no partner before each one with an offer shows once.
