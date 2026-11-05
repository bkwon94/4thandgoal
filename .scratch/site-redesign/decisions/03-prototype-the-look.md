# 03: What is the look?

Map: `.scratch/site-redesign/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** done

## Question

The look is the base of every route. Settle the type pair, the radii, the surfaces, the grid texture, the components, and the motion, on dark first. The start point is board A, Night Broadcast, with the structure of board C, Telemetry, on the canvas https://claude.ai/artifact/4cFaYVh4Sm9Cw68G7FEds8. Show it in the CPC red and the NorCal orange, so the look holds under each brand. When it clears, write the ADR that supersedes ADR 0006 and the light default of ADR 0007.

## Decision

The look is the blend of look 1, Instrument, and look 2, Glass HUD, on the canvas https://claude.ai/artifact/4cFaYVh4Sm9Cw68G7FEds8, board "Look 1 + 2 · blend". Brian approved it on 2026-11-05, after one round of fixes.

- **Type:** Space Grotesk for text and headings. JetBrains Mono for numbers, scores, and small uppercase labels with wide tracking.
- **Radii:** 24px for the hero, 20px for a card, 18px for a tile, and a full pill for a button and a bar.
- **Surfaces:** each surface comes from the brand: the page, the card, the raised surface, and the rule. Only the hero carries the 24px grid texture, the corner brackets, the brand glow, and a scan line on entry.
- **Space:** the hero has 28px of inner space on top and bottom and 24px on the sides. A card has 16px. The page gutter is 16px. No text sits near an edge or a corner bracket.
- **Photos:** each team row shows its Sleeper avatar. A player headshot sits in a round frame on a ground of the brand glow, cropped at the shoulders, never as a loose cutout. With no image, the frame shows the initials.
- **Components:** a game card shows both avatars, both scores, and a share bar of the points. A tap opens its recap, and the open card gets a brand edge. An award tile has a fixed grid: the award name and a 44px photo on one row, then the points, the player, and the team. The standings show every team with its avatar, a playoff tick, and a brand line under the last playoff spot.
- **Motion:** content rises in a stagger, 0.7s on `cubic-bezier(.16,1,.3,1)`. The bars grow once. A recap opens in 0.3s. A tap scales to 0.98. Reduced motion turns all of it off.

The board showed two facts. First, both brands have a flat `#141414` page, so a deeper ground is a color choice for ticket 09, not part of the look. Second, NorCal has no headshot for some players, so the fallback is a real case.

The prototype lives on the canvas, not in the repo, so no prototype code needs a delete. The record is ADR 0024.
