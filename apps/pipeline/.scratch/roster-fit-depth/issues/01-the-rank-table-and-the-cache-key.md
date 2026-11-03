# 01: The rank table and the cache key

Spec: `.scratch/roster-fit-depth/PRD.md`, "The rank table", "The cache key". Glossary: "Position rank".
Decision record: ADR 0003.

**What to build:** The snapshot ranks every player with a stat line in the known games at QB, RB, WR, and TE,
once per snapshot, by lineup value, with the position order as the tie rule and the player id last. Rostered and
unrostered players are in the pool. A rostered player due back ranks by his projection ahead. A player with no
game in the window ranks last. Any reader asks the snapshot for a player's rank and gets it with no second pass.
The points-per-game fact for each traded player names his rank in plain words, so "Spears, RB38 by points per
game" reaches Claude and the analysis today. The grade key and the finder key hash the inputs the rank table
reads for unrostered players: the position and the fields that give lineup value, per week in the window. The
document version bumps to 8. The finder reads the table and never rebuilds it per side.

**Blocked by:** None (can start immediately).

**Status:** done

- [ ] The week 6 fixture snapshot gives a named RB a rank that matches a hand count of lineup values at RB.
- [ ] A player with no game in the window ranks after every player with a game.
- [ ] A rostered player due back ranks by his projection ahead, not his recent points.
- [ ] A free agent with a stat line ranks in the pool, so the rank is a league rank.
- [ ] The live snapshot and the saved snapshot give the same table for the same raw.
- [ ] The points-per-game fact of a traded player names his rank, and the analysis checker accepts a sentence that quotes it.
- [ ] A changed stat line of an unrostered RB changes the grade key and the finder key.
- [ ] A changed stat line of an unrostered K changes neither key.
- [ ] The document version is 8.
- [ ] Every existing rubric test passes unchanged.

## Comments

- 2026-11-02: `main` holds the merge 84d9349. Status set to done by the state-file sweep of agent-habits 02.
