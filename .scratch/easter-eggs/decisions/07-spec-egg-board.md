# 07: Where the egg board sits and what it shows

Map: `.scratch/easter-eggs/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** done

## Question

Decide the route of the egg board, its place in the menu, and its layout: the letters of each manager in each egg word, the count of eggs left, and the winner of each egg word. The choice is small, so the spec records it.

Brian set the design tool on 2026-11-06: Claude Design, the Design artifact type built into Claude, makes the design of the claim form, the egg, the animations, and the egg board.

## Design input

Brian approved these choices with ticket 08 on 2026-11-06. The board and banner artboards of the canvas https://claude.ai/artifact/2pe6Z3X2vAiTVAfEwbHSJF show them. The spec records the route.

- The way in: an egg button in the top band, beside the theme button, on every page. Its red badge is the count of eggs left to find. The dock keeps its five items.
- The egg banner: a slim strip, 52px tall, edge to edge under the top band of the home page. It reads "6 new eggs · 7 left" with a link to the egg board and a button that hides it.
- The hero: three counts, left to find, found, and to drop, over a grid of all 54 eggs, one column per week from 9 to 17. A found egg is white, an egg still out glows red, and a future egg is dashed.
- One card per egg word with its gift card value and its leader, the top 5 managers with their tiles, and "Show all 11". A won word turns into a hero card with a WON stamp.
- A "Latest claims" feed names the manager, the letter, and the egg word, never the page or the spot. Brian likes it.
- The board shows no block. The found count still counts each block.
- A short "How the hunt works" card ends the page.

## Decision

Brian approved the spec on 2026-11-06. The egg board is the route `/eggs/`, rendered in the client from the egg board route of the API. The way in is the egg button in the top band, not a menu item. The layout is the hero, one card per egg word, "Latest claims", and "How the hunt works". See Implementation Decisions of `.scratch/easter-eggs/PRD.md`.
