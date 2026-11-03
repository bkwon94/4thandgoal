# 06: The cache key hashes the week N stat lines

Spec: `.scratch/known-games/PRD.md`, "The cache key". Prior art: nflverse ticket 13, the cache key hashes the
projections and the returns.

**What to build:** The grade cache key and the finder cache key add a hash of the week N stat lines of the
players on the two rosters: points, games played, snaps, team snaps, targets, red zone targets, and red zone
rushes. A new fetch with a new number for a rostered player is a new key. A stat line of a player on neither
roster changes nothing. The document version bumps, so every result cached under the old version never serves.

**Blocked by:** 02 (The known-games week).

**Status:** done

- [ ] A repeat grade in the cache window with the same week N lines is a cache hit with one Claude call.
- [ ] A week N line of a rostered player that gains 6 points gives a new key.
- [ ] A week N line of a player on neither roster gives the same key.
- [ ] No week N lines and empty week N lines give the same key as each other and a different key from any line.
- [ ] The finder key changes the same way.
- [ ] The document version is 6 and a result cached under 5 never serves.

## Comments

- 2026-11-02: `main` holds the merge b348170. Status set to done by the state-file sweep of agent-habits 02.
