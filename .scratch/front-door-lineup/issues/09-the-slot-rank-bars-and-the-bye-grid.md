# 09: The slot rank bars and the bye grid

Spec: `.scratch/front-door-lineup/PRD.md`. Acceptance tests AT-30, AT-31.

**App:** both

**What to build:** How you stack up shows the slot rank bars: exactly QB, RB, WR, and TE, each with a bar from the league middle and a rank, with the roster grade and its read in the header. Weak spots shows the bye grid: a dot matrix of the players against the next weeks, with a red dot for a starter on a bye. The byes come from the Sleeper schedules of the API snapshot.

**Blocked by:** 01

**Status:** done

- [x] The stream of How you stack up carries the slot rank bars with four rows only (AT-30).
- [x] The stream of Weak spots carries the bye grid, and its red dots match the bye weeks of the starters (AT-31).
- [ ] Site screenshots show both blocks.

## Comments
- Closes with the squash merge of the spec PR.
