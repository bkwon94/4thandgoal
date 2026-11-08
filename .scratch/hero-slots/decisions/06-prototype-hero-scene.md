# 06: The art of the hero is a scene of the week's data

Map: `.scratch/hero-slots/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** done

## Question

After decision 01, Brian asked for a bold and ambitious change, not a change of type alone. What art makes the hero ambitious on a phone, and how does a reader use it?

## Decision

Brian decided on 2026-11-07, after two rounds of a prototype on a throwaway route with real `cpc` data: the Matchup of the Week of week 8 of 2026 and the manager hero of "To Infinity and Bijan". The prototype code is deleted.

1. **The scene.** The art of the hero is a scene: points of light on the dark field of the hero. On entry they start scattered, drift in, and settle into a small chart of real data. Thin lines then draw between them in x order, like a star chart. This is variant A, "Constellation". Variant B, falls with a tail, and variant C, rings from left to right, lost.
2. **What the lights mean.** On the Matchup of the Week, 12 lights, one per team, sorted from low to high by the points of the week, with a dashed line at the league median. The two teams of the Matchup flare in the brand red. On the manager hero, one light per played week at its points, bright for a win and dim for a loss, with a dashed line at the median of each week.
3. **Place.** On a phone the scene is a band of about 200px at the top of the card, above the slots. From the `tablet` tier up it fills the open middle of the two-row split of decision 01. No light sits under text.
4. **Timing.** The settle takes about 1.9 s with a strong ease-out. The lines draw after it. The scene plays again each time the hero comes back into view, after it fully left the view.
5. **Taps.** A tap anywhere in the scene selects the nearest light, so no tap misses. A horizontal drag scrubs the selection from light to light, and a vertical drag still scrolls the page.
6. **Labels.** One light shows its label at rest: the winner of the Matchup, such as "The Blue Tent · 100.31", and the latest week on the manager hero, such as "Week 8 · 118.89 · W". A label flips to the inner side of its light near an edge.
7. **Hint.** The caption "TAP OR SLIDE" sits in a corner of the scene with no light. It fades after the first touch on any scene and stays gone for that reader.
8. **Must fix in the spec.** The label of the Matchup winner covered the "+1.43" margin text. The spec places the margin text so that no label covers it.
9. **Reduced motion.** The settled chart draws at once.

Brian on round 2: "feels really good."

The scene replaces the bend of Mesh Flow. Decision 02 closes as replaced. Decision 03 still holds for the colors of the scene. Which other heroes get a scene is decision 07.

Weak spots to note in the spec: the dots look random until about the last 0.5 s of the settle, the two red lights sit close, so a slide jumps fast between them, and a tap during the settle does nothing.
