# 12: The sheet title clear of the oval

Spec: `.scratch/easter-eggs/PRD.md`. Acceptance test AT-50.

**App:** site

**What to build:** At 340 px, axe gives an incomplete on the title of the claim sheet hero in both themes: its background color cannot be read because it partially overlaps another element. The title overlaps the art oval of ticket 08. AT-50 counts an incomplete as a failure.

**Blocked by:** none

**Status:** done

- [x] No text of the claim sheet hero overlaps the oval at 340 px and 390 px.
- [ ] Axe gives 0 failures and 0 incompletes on the claim sheet before and after a team pick, at 340 px and 390 px in both themes.

## Comments

- 2026-11-07: The oval was not the cause. axe compares the stack under each line of an element, and the stack holds the page under the sheet. At 340 px the two lines of the title sit over two parts of the midseason page, so axe gave `elmPartiallyObscuring`. The title is now two block spans, one per line. The oval change stays, because it keeps the full gap between the oval and the title.
- Closed by the merge of PR #19.
