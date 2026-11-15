# 10: Do we pay the bundle cost of the Drawer on every page?

Map: `.scratch/ui-sdk-sheet/MAP.md`.

**Kind:** grill

**Blocked by:** 07

**Status:** done

## Question

The `Drawer` adds about 43 KB gzip to each page that imports it (decision 07). The menu sheet sits in `TopBand`, so a direct import adds it to every page. The move removes no library to offset it. The spec must choose:

1. A direct import: every page pays about 43 KB gzip, and the sheet opens with no wait.
2. A lazy import on the first tap of the menu button, or on hover and focus: pages pay nothing until a reader opens the menu, but the first open may wait for the chunk.

A later ui-sdk component may share part of the cost. Decision 07 did not measure that share.

## Decision

Only the front door pays the cost of the `Drawer`, and it imports the `Drawer` directly. Brian decided it in the grill of 2026-11-14.

1. **Only the front door pays.** `door-page.tsx` is the only page with `nav="sheet"`. The other 11 pages with `TopBand` show the dock and never show the menu sheet. Now `top-band.tsx` imports `MenuSheet` statically, so a direct import there puts about 43 KB gzip on all 12 pages. A dock page must get no `Drawer` code. The spec picks the method, for example a sheet that `door-page.tsx` gives to `TopBand` as a prop.
2. **A direct import on the front door.** The front door pays about 43 KB gzip, and the first tap opens the sheet with no wait. Decision 02 puts the feel first, and our code rule prefers the simple path. A lazy import may make the first tap wait on a slow network. A later sheet on another page shares the cost.
3. **One acceptance test guards the dock pages.** The JS of one dock page, such as `/rankings/`, does not grow. The evidence is the gzip sum of decision 07, before and after. No standing check of the bundle size goes into CI. That is its own feature.
4. **The dock stays.** It is no sheet: it stays on screen and never opens or closes. Each page is one tap away, and the menu sheet takes two taps.
