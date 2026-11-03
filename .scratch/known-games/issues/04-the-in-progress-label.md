# 04: The in-progress label

Spec: `.scratch/known-games/PRD.md`, "Final or in progress", "The in-progress label in reasons". Glossary: "In
progress".

**What to build:** A week N game is in progress when now is past its kickoff by less than 4 hours 30 minutes.
The kickoff comes from the nflverse schedules file, already a refreshed source, matched by season, week, and NFL
team. A game with no schedule row counts as final. The label changes no number and no step. The known-games
block counts the games in progress. Every reason that quotes a week N number of an in-progress game adds "game in
progress" to that player's sentence: the trend and usage reason and the roster fit reason at least. The clock is
an input, so a test can set it.

**Blocked by:** 02 (The known-games week).

**Status:** done

- [ ] With a clock 2 hours after a 1 pm kickoff, the game is in progress and the block counts it.
- [ ] With a clock 5 hours after kickoff, the game is final and the block counts zero in progress.
- [ ] A game with no schedule row is final.
- [ ] The trend reason for a player whose week 7 game is in progress ends his sentence with "game in progress".
- [ ] The adjuster steps are the same with the label on and off.
- [ ] The words "live", "partial", and "current week" appear in no reason and no stamp.
- [ ] The prose checks of the analysis pass on a reason with the label.

## Comments

- 2026-11-02: `main` holds the merge 4ff0564. Status set to done by the state-file sweep of agent-habits 02.
