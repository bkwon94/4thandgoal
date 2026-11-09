# 07: The Matchup scene on the home page and the week page

Spec: `.scratch/hero-slots/PRD.md`. Acceptance tests AT-15, AT-16, AT-17, AT-24 to AT-34, AT-35 for the home page, AT-37, and AT-40.

**App:** site

**What to build:** A manager opens the week page of week 8, and the first hero draws the Matchup scene: 12 lights drift in and settle in about 1.9 s into a star chart, with the median line and the two teams of the Matchup in the accent color. "The Blue Tent · 100.31" shows at rest, and "+1.43" stays visible. A tap selects the nearest light, a slide scrubs, a vertical swipe scrolls, and "TAP OR SLIDE" shows once. The scene plays again on re-entry, draws the settled chart under reduced motion, and stops its loop at rest. The canvas is Canvas 2D, reads its three colors from a probe element, and works on NorCal with the orange accent.

**Blocked by:** 02 and 06

**Status:** done

- [x] The scene of AT-15 shows at 375, 768, and 1280 px, with the margin mark of AT-17 and the label at rest of AT-24.
- [x] The settle takes about 1.9 s, as the frames of AT-16 show.
- [x] A tap selects the nearest light, a slide scrubs, and a vertical swipe scrolls (AT-25, AT-26, AT-27).
- [x] The hint shows once and stays gone after a reload (AT-28).
- [x] A label at an edge shows in full (AT-29), and the scene replays on re-entry (AT-30).
- [x] Under reduced motion the settled chart shows at once (AT-31), and no animation frame runs for 3 s after the settle (AT-32).
- [x] The hero and the scene stay dark in the light theme (AT-33), and NorCal flares in `#c2410c` (AT-34).
- [ ] The home page has exactly one scene (AT-35).
- [x] A brand test holds `accent`, `on-dark`, and `on-dark-muted` equal in the light and dark sets of each client.
- [x] No 3D engine is added, and the scene asks for a `2d` context only (AT-40).
- [ ] `pnpm check:floor` passes for `cpc` and `norcal` (AT-37).
