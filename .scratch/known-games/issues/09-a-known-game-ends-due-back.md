# 09: A known game ends due back

Spec: `.scratch/known-games/PRD.md`, "Out with no return week" and "The known-games week". Found in the ticket 02
real-data check on 2026-10-26: the returns file had Jacobs due back in week 7, and he played in week 7, so his
lineup value was still his projection ahead after his real game.

**What to build:** A player with a known game in the trade week is back, whatever the returns file or his injury
status says. The due-back rule reads the known games first: a player with a week N stat line with a game played
is not due back, so his lineup value is his recent points per game, which count the week N game. A player with no
week N line keeps the rule of ticket 05. The fit note for a player who played says nothing about a return. The cache
key reads the same rule, so a first game after a return is a new key.

**Blocked by:** 02 (The known-games week), 05 (Out with no return week), 06 (The cache key hashes the week N stat lines).

**Status:** done

- [ ] A player with a returns row of week 7 and a week 7 stat line with a game played takes his recent points per game, which count week 7, and the fit note has no return week for him.
- [ ] A player with a returns row of week 7 and no week 7 line takes his projection ahead from week 7, as ticket 05 gives.
- [ ] A player tagged Out with no row keeps the rule of ticket 05 even with a week 7 line with a game played, because that is the player hurt in his game; a known game ends due back only for a player whose returns row is week 7 or earlier.
- [ ] The trend adjuster's due-back exemption, the return bet, and the credited return bets end for a player who played in week 7, because `_due_back`, `_return_bet`, and `_credited_return_bets` read the same known game.
- [ ] The trend adjuster reads his week 7 share, because the known game ends the exemption the trend gives a due-back player.
- [ ] The cache key changes when his first week 7 line arrives.
- [ ] The finder no longer leaves him out of a trade once he has a known game.

## Comments

- 2026-11-02: `main` holds the merge 0c0418b. Status set to done by the state-file sweep of agent-habits 02.
