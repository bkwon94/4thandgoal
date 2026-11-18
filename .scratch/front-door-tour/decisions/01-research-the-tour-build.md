# 01: Which parts build the Tour

Map: `.scratch/front-door-tour/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

The spec must name the parts that build the spotlight, the Stop card, and the motion between Stops. Brian prefers ui-sdk first. Use transitions.dev or a scrolltide item if one fits. `framer-motion` is fine, and the front door already uses it.

Find out:

1. Which ui-sdk parts help: a popover, a positioner, a focus trap, a dismissable layer, or an overlay. Check the version that the site uses.
2. Which transitions.dev transitions fit a Stop card and the move of a spotlight from one control to the next.
3. Which scrolltide items show a tour or a spotlight. Use search results only. Fetch no prompt.
4. How the spotlight follows its control on a resize, on a scroll, and under the keyboard lift of the Drawer.
5. How the Tour sits with the Sheet, the passphrase modal, and the easter eggs, so that no two layers fight.
6. What a tour library such as `driver.js` gives, as a baseline only.

Write the findings at `.scratch/front-door-tour/decisions/01-research-the-tour-build.notes.md`.

## Decision

None yet.
