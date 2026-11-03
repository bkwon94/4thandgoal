# 13: One component for best adds and top performers

**What to build:** `best-adds.tsx` and `top-performers.tsx` share one shape: a chapter, a label, `PlayerRows`, and a map to `PlayerRow`. Consider one component for both. Low priority.

**Blocked by:** none

**Status:** done

- [ ] Read both files and list what differs, such as the id, the label, and the row detail.
- [ ] Build one component only if the diff is smaller than the two files it replaces. Otherwise close this ticket with a comment.
- [ ] The chapter ids still match `MANAGER_CHAPTERS`.
- [ ] No change in the rendered HTML. `pnpm check:export` still passes.

## Comments

- 2026-10-31: closed by modular site ticket 11. One `PlayerChapter` holds the body; best adds and top performers each hold only their words and their data pick. The diff is three lines larger than the two files it replaces, and the PRD chose one body over the smaller diff.
