# 03: Out for the season

**Repo:** `cornerstone-fantasy-sleeper-weekly-report`

**What to build:** The commissioner writes the word `season` in place of a return week in the returns file, and the analyzer reads that player as out for the season. The side that gets him counts zero chart value for him in the start letter. The side that gives him counts his full value. The injury adjuster steps the side that gets him down with the reason "Name is out for the season.", before the no-near-return check. The Sleeper IR status alone is not the mark. The rule is ADR 0013, which sits in the main checkout with the five upside glossary terms; this ticket commits both from its worktree.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] The returns loader reads `season` and the snapshot exposes the players out for the season
- [x] A player out for the season counts zero chart value for the side that gets him only, tested at the rubric seam
- [x] The injury adjuster steps that side down with the plain reason, tested at the rubric seam
- [x] A player on IR with no mark is not out for the season, tested at the rubric seam
- [x] ADR 0005 and the glossary terms are committed
- [x] The pipeline test suite passes

## Comments

- 2026-10-27, Truckasaurus Tina: Done in the pipeline commit 69b851b, merged in dc02eb2. `Snapshot.out_for_season` holds the set. A season player's lineup value is zero too, per ADR 0005.
