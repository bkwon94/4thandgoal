# 01: The Tour: four Stops, their controls, and the seen key

Spec: `.scratch/front-door-tour/PRD.md`. Acceptance tests AT-2, AT-3, AT-4, AT-7, AT-8, AT-9, AT-10, AT-11, AT-12, AT-13, AT-23, AT-24, AT-25, AT-26, AT-29, AT-30, AT-33, AT-35, AT-36, AT-37, and AT-39.

**App:** site

**What to build:** A league mate whose browser has Your team and no seen key opens the front door and sees the Tour. The page dims, and a hole and a Stop card show on each of the four Stops in order: the Suggestions, the ask box, the team switch, and the menu button or the pill bar. Each Stop shows its header, its line, "n of 4", the dots, Skip, and Next, and Stop 4 shows Done. Next and a tap on the dim go to the next Stop. Skip, Escape, and Back end the Tour. The real controls do not respond during the Tour. The Stop card is a new `stop-card` wrapper of the ui-sdk Popover in the design `ui` folder. The hole jumps from Stop to Stop in this ticket. Ticket 03 sets the final look, and ticket 04 adds the glide. Stop 1 writes the seen key `cpc.tour-seen`, so the Tour shows once per browser.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] A browser with Your team and no seen key sees Stop 1 on load (AT-2).
- [ ] The four Stops show the copy of the PRD table word for word, with "n of 4" and four dots (AT-3).
- [ ] Stop 4 aims at the menu button at 375 and 768 px, and at the pill bar at 1280 px (AT-4).
- [ ] Next, a tap on the dim, Skip, Escape, `back`, and Done each do what AT-7 to AT-12 say.
- [ ] A tap on a Topic in the hole opens no Answer and no passphrase sheet (AT-13).
- [ ] A tap on the menu button in the hole at Stop 4 opens no menu sheet (AT-35).
- [ ] Stop 1 writes `"1"` to `cpc.tour-seen`, and a second visit or a reload shows no Tour (AT-23, AT-24, AT-25).
- [ ] A throw on the read of `localStorage` gives no Tour, and the Suggestions still render (AT-26).
- [ ] The card has the name of its header and the description of its line, and Tab stays inside the card (AT-29, AT-30).
- [ ] A 2 s hold on the dim or the card sends no egg check (AT-33).
- [ ] The Stop card has role `dialog` and `aria-modal="true"` while the Tour shows (AT-39).
- [ ] The `ui` README names the `stop-card` wrapper, and the ui-sdk rule test passes.
- [ ] No `driver.js` in any `package.json` or the lock file, and no change under `apps/pipeline/` or `apps/api/` (AT-36, AT-37).
