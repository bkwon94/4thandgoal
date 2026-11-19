# 05: The replay from the menu sheet and the "?" button

Spec: `.scratch/front-door-tour/PRD.md`. Acceptance tests AT-27, AT-28, AT-31, and AT-34.

**App:** site

**What to build:** On a phone and a tablet, the menu sheet of the front door shows a "Show the tour" link. On desktop, a "?" icon button with the name "Show the tour" sits beside the theme button. A tap on either one closes the menu sheet if it is open, then starts the Tour at Stop 1. After the Tour, focus goes back to the control that had it before. The front door passes the link and the button into the shell through slots, so the shell names no Tour. The other pages show no Tour and no replay control.

**Blocked by:** 01

**Status:** ready-for-agent

- [x] At 375 px, "Show the tour" in the menu sheet closes the sheet, then shows Stop 1 (AT-27).
- [x] At 1280 px, the "?" button beside the theme button shows Stop 1, and its name is "Show the tour" (AT-28).
- [x] After a keyboard replay from the "?" button, Done puts focus back on the "?" button (AT-31).
- [x] `/analyze/` and the week 10 report show no Tour and no replay control, and do not set the seen key (AT-34).
