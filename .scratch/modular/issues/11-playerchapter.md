# 11: `PlayerChapter`

**What to build:** One part takes an id, a title, an empty text, and the items, and renders the chapter with the label and the player rows. Best adds and top performers call it with their own data and words. This closes manager-pages site ticket 13.

**Blocked by:** 07

**Status:** done

- [ ] Best adds and top performers are each under ten lines and hold only their words and their data pick.
- [ ] The manager page tests pass with no change to what they read.
- [ ] `out/` has no diff against `main`.

## Comments

- 2026-10-31: merged into `main` from branch `modular-11-player-chapter`, commit 5f2f4c0. 539 tests. `PlayerChapter` sits in `managers/`, since only the two manager chapters call it. The export is byte-identical. Two reviewers passed it.
