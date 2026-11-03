# 01: The week file, thin

Spec: `.scratch/waiver/PRD.md`.

**What to build:** The Tuesday build writes `waiver.json` beside `page.json` in the week folder, and
`cornerstone publish` ships it with the week. The file holds the schema version, the build time, one
bucket, best adds, with the per-position cap, and the budget table with each team's budget left and
waiver order. Best adds ranks by board score, here the projection score ranked within the position, with
rest of season projection as the tiebreak. A manager who reads the file sees the top free agents
with a week projection and a rest of season projection, and every team's FAAB left. No usage, no price,
no research yet. Those tickets fill the same file.

The projections ahead fetch lifts its roster filter, so the raw file holds every player with a
projection. The board engine module exists as one function with no network and no Claude. Its score is
projection alone for now. The three-score shape and the tunables for the weights and the bucket sizes
land here, so the next tickets only add scores.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] The pool is every active player with a team and a position of QB, RB, WR, TE, K, or DEF on no roster in this league.
- [x] Rest of season projection is the sum of weeks N+1 to 17 from the unfiltered projections ahead file, with the bye as 0.
- [x] The best adds bucket holds at most `BUCKET_SIZE` players and at most `PER_POSITION` per position.
- [x] The budget table holds every roster with budget left and waiver order from the raw files.
- [x] The build writes the file in the facts step, and a rewrite reads the saved file and never reruns the engine.
- [x] The publish copies the file with the week folder, with no new publish path.
- [x] The engine test on the week 6 fixture checks the cap, the pool filter, the rest of season sum, and that two runs give the same file.
- [x] The fetch test checks the projections ahead file holds an unrostered player.
- [x] Glossary gains **Waiver pool**, **Bucket**, and **Board score**.

## Comments

2026-10-23: the real week 6 `projections_ahead.json` is the old filtered file, so a week 6 board shows zeros until a fresh fetch, and week 7 is the first real board.
