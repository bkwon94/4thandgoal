# 18: Quiet rows, tags, and controls

Spec: `.scratch/midseason-report/PRD.md`. Acceptance tests AT-55, AT-56, AT-57, and AT-58.

**App:** site

**What to build:** The rows of the report match the R1 Quiet text board of the Design canvas, row "Ticket 15 · rows and tags". A tag has no box and no fill. "Free agent" sits in the second line of a row, and any other tag is a small mono caps word, muted, with the accent color for "just bad" and "hurt on arrival". Cards have 8 px corners, and the report has no full pill. The position switch is text segments with a 2 px accent underline that slides. "Show all" is a mono text control with a chevron and no border, which changes to "Show top 5". The awards are lines, "MVP — player, team — fact". Player points show 1 decimal place, and team scores show 2.

**Blocked by:** 15, 17.

**Status:** done

- [x] No tag in the report has a fill or a border, and the DEF #3 row reads "Free agent" in its second line.
- [x] Cards have 8 px corners, and no element of the report is a full pill.
- [x] The position switch and "Show all" match the board, with keyboard focus and reduced motion.
- [x] Each award is one line, and no award is a card.
- [x] The DEF #3 shows 77.8, and the highest score shows 158.96.

## Comments
- Closed by the merge of PR #13.
