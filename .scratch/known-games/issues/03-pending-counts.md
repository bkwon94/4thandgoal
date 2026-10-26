# 03: Pending counts

Spec: `.scratch/known-games/PRD.md`, "Pending counts". Glossary: "Pending".

**What to build:** A week N stat line with a game played and no snap count is pending for snaps. The snap share
reader skips that game and reads the games before it. Target share, points, and red zone touches use the line.
The WOPR window reads the week N row of the nflverse player file when the file has it, and ends at N-1 when it
does not, with WOPR named as pending. The known-games block names each pending count with the number of games
it is pending for. The trend reason names the weeks each share read, so a snap share from weeks 4 to 6 beside a
target share from weeks 5 to 7 reads as two spans, as the reason does today when the weeks differ.

**Blocked by:** 02 (The known-games week).

**Status:** ready-for-agent

- [ ] A week 7 line with targets and points but no snap fields leaves the snap share at its weeks 1 to 6 window and never reads the game as zero snaps.
- [ ] The same line moves the target share and the points per game.
- [ ] The known-games block names snaps as pending for the count of such games.
- [ ] With a player file that lacks week 7, the WOPR window ends at week 6 and the block names WOPR as pending.
- [ ] With a player file that has week 7, the WOPR window reads it and WOPR is not pending.
- [ ] A week 7 line with snaps present is pending for nothing and the snap share reads it.
- [ ] Every rubric test for a saved week passes unchanged.
