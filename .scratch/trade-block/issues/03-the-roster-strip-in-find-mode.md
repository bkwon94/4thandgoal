# 03: The roster strip in Find mode

Spec: `.scratch/trade-block/PRD.md`. Acceptance tests AT-10, AT-12, AT-13, AT-15 to AT-23, AT-30, AT-31, and AT-32.

**App:** site

**What to build:** Find mode of the analyzer shows a strip of the asker's QB, RB, WR, and TE under "Your team". A tap puts a player on the Trade block or takes him off, up to 3, and a press of Find a Trade sends the block. The prototype on the branch `trade-block-01-proto` at `285f2789` holds the copy and the look; the real part is new code with tests.

**Blocked by:** 01

**Status:** in-review

- [x] The strip lists only the QB, RB, WR, and TE of the asker, in that position order and then by name, each with the headshot, the last name, and the position.
- [x] A tap adds a player with a red ring and a check at the front of the strip, and a tap on a pick takes it off.
- [x] The counter reads "N of 3", and the label reads "Trade block · tap to add", or "Trade block · tap a pick to take it off" at 3 of 3.
- [x] A 4th tap adds no one, scrolls the strip back to the picks, and shows "Your block holds 3 players. Take one off to add another."
- [x] The empty block shows "No one on the block. The search can offer any of your players."
- [ ] The find body carries `trade_block`, and a real press with Walker on the block gives only cards that send Walker.
- [ ] A change of Your team clears the block, a change of the partner or the chip keeps it, the strip locks during a find, and a reload clears it.
- [x] The part is the ui-sdk `ToggleGroup` with `multiple` in a ui-sdk `ScrollArea`, through the design package wrappers (ADR 0037), and no copy says "anchor".
- [ ] The site Vitest suite passes, and the screenshots at 375, 768, and 1280 px in both themes and at 390x660 in iPhone WebKit show the strip.
