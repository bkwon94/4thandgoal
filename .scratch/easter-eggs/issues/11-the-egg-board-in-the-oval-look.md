# 11: The egg board in the oval look

Spec: `.scratch/easter-eggs/PRD.md`. Acceptance tests AT-42, AT-43, AT-44, and AT-50.

**App:** site

**What to build:** Brian approved the oval look of ticket 08 and wants the egg board in the same look. The hero of `/eggs/` shows dark plate boxes behind its text: the counts, their labels, the week numbers, and the legend. The letter tiles of each egg word card touch, so two dashed borders read as one doubled line.

**Blocked by:** none

**Status:** done

- [x] The text of each hero of the board sits on the flat band color with no plate. The grid and the glow show only where no text sits.
- [x] Each tile of a letter row of an egg word card has the same width, with a visible gap, inside its card at 340 px and 390 px.
- [x] The readability floor and the axe checks pass on `/eggs/` at 340 px and 390 px in both themes.

## Comments
- Closed by the merge of PR #19.
