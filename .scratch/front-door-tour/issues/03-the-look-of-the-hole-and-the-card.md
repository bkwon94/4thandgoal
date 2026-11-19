# 03: The look of the hole and the card

Spec: `.scratch/front-door-tour/PRD.md`. Acceptance tests AT-14, AT-16, AT-17, AT-18, AT-19, and AT-22.

**App:** site

**What to build:** The Tour gets the look that Brian chose in decision 02. The hole sits on the visual box of its control with an even pad: 6 px, or 10 px for a box under 28 px tall. The menu button gets a circle, and each other control gets a pill. The card places itself beside the hole and never covers its control. The card header holds the name and the count on one line, and the card keeps one height at all four Stops. Next and Done use the brand accent in both themes. Before each Stop, the Tour scrolls its control into view. The hole and the card follow their control on a resize, a turn of the phone, a zoom, and a scroll.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] The hole pad is even on all four sides to 1 px, with a circle on the menu button and a pill on each other control (AT-14).
- [ ] The card does not overlap its control on the four viewports of the iPhone rule (AT-16).
- [ ] The card height is the same at all four Stops to 1 px, at 375 and 1280 px (AT-17).
- [ ] At 390x660, each control is inside the visual viewport when its Stop shows (AT-18).
- [ ] After a resize from 390x660 to 660x390 at Stop 2, the hole center is within 2 px of the ask box center (AT-19).
- [ ] Next and Done fill with the `accent` token and use the `on-dark` text in both themes (AT-22).
- [ ] The ticket uses the design bar: `transitions-dev`, scrolltide, `apple-design`, `animate`, `critique`, and `polish`.
