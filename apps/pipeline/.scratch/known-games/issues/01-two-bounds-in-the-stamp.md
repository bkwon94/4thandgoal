# 01: Two bounds in the stamp

Spec: `.scratch/known-games/PRD.md`, "Two bounds in the as-of stamp". A prefactor with no change in any grade.

**What to build:** The as-of stamp splits its one stats-through week into two: the player stat bound, which every
stat reader takes as its `through`, and the standings bound, which the standings and the standing adjuster take.
Both are week N-1 today. The result document carries both, and the old field stays with the same value so the
site reads as before. The cache key reads the player stat bound where it read the one week.

**Blocked by:** None (can start immediately).

**Status:** done

- [ ] A week 6 snapshot stamps a player stat bound of 5 and a standings bound of 5.
- [ ] Every stat reader, the standings, and the standing adjuster read their own bound by name, never the other.
- [ ] The result document and the finder document carry both bounds, and the old stats-through field still holds 5.
- [ ] Every existing test passes unchanged, with 1083 or more tests and ruff clean.
- [ ] The glossary entry "Before the trade" matches the code comments that cite it.

## Comments

- 2026-11-02: `main` holds the merge 820ed98. Status set to done by the state-file sweep of agent-habits 02.
