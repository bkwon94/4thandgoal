# 02: The War chest look

Spec: `.scratch/waiver/pipeline/PRD.md` in the pipeline repo. The look is option D in
`.superpowers/brainstorm/` there, `look-faab.html`.

**What to build:** The waiver page is a black card. Under the masthead sits the budget ring: twelve
avatars with a bar each in budget order. Under the ring, five tabs, one per bucket. Under the tabs, the
drift field: the top 6 of the open bucket as headshots that drift in slow motion, sized by rank, each
with its price. Under the field, the sheet: the open player's name, his three facts, his research
claims with source links, the bid to win, the last like him, and a line that the experts are missing
when the flag says so. Under the sheet, the list of the whole bucket in order. A tap on a headshot or a
list row fills the sheet. The sheet keeps its player when the tab changes. The drift stops under
reduced motion and when the tab is hidden. At 390 pixels no headshot covers another.

The positions in the field are a fixed layout per rank, never random. New sizes and colors go in the
global stylesheet as tokens. Motion goes through the one reduced-motion switch.

**Blocked by:** 01 The route behind the flag.

**Status:** ready-for-agent

- [x] The ring renders twelve bars in budget order from the fixture, none red with no pick.
- [x] The tabs switch the bucket, and the sheet keeps its player across a switch.
- [x] The field shows the top 6 with the size from the rank and the price on each.
- [x] A tap on a headshot or a row fills the sheet with the facts, the claims as links, the price, and the last like him.
- [x] The missing-experts line shows when the file flag is set.
- [x] The drops bucket rows name the roster and the pool player who beats him.
- [x] The reduced-motion test shows the drift off; a hidden tab stops it.
- [x] No two field slots overlap at 390 pixels, checked in a test on the layout table.
- [x] A missing headshot swaps to the default once.
