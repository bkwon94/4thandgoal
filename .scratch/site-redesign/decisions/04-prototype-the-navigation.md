# 04: How does a reader move across the routes?

Map: `.scratch/site-redesign/MAP.md`.

**Kind:** prototype

**Blocked by:** 03

**Status:** done

## Question

The redesign may change the navigation. Settle the masthead, the menu, the compact bar, the theme button, and the week picker, at phone and desktop width. The spec needs one model of the navigation for every route.

## Decision

The phone uses model 1, the dock. The desktop uses the pill bar and the chapter rail of model 2. Brian chose this on 2026-11-05, from the boards "Nav 1 · Dock" and "Nav 2 · Pill rail" on the canvas https://claude.ai/artifact/4cFaYVh4Sm9Cw68G7FEds8.

- **Phone:** a dock floats at the bottom of the viewport, with an icon and a label for each destination: Home, Week N, Rankings, Managers, and Trade. It stays on screen at every scroll. The top band holds the brand mark, the week chip, and the theme button.
- **Week chip:** a "WK 08" control in the top band. A tap opens a strip of the weeks of the season. The current week has the brand edge.
- **Desktop:** the top band holds the brand mark, a pill bar of the destinations with full labels, the week chip, and the theme button. The week page adds the chapter rail on the left, which marks the chapter in view.
- **The client menu:** the `layout` key of `[menu]` in `client.toml` goes away, because the look owns the navigation. A client keeps only its list of items and their labels. The `hamburger`, `bar`, and `tabs` layouts of `packages/design/site/shell/masthead.tsx` go with it.
- The labels of the dock are 10px. Ticket 13 decides if a dock label counts as body text.

The prototype lives on the canvas, not in the repo, so no prototype code needs a delete.
