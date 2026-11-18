# 02: The page card of a site question

Spec: `.scratch/site-answer/PRD.md`. Acceptance tests AT-1, AT-4, AT-5, AT-6, AT-7, AT-10, AT-11, AT-12, AT-14, AT-15, AT-16, AT-17, AT-19, AT-21.

**App:** site

**What to build:** A manager asks "where is the trade analyzer" and gets the page card in the Thread. The site builds the page list from the Menu that the client shows, with no Home. It adds the midseason report and the sim as a Tool by the rules of the spec. Each package gives its Tool mark and its fixed blurb. The site sends the list as `pages` with each ask. The route `site` with a page key becomes a kept Thread item that holds only the key. The site builds the links when it shows the item. The page card is the B card of decision 02: the lead line, the icon box and the name, the blurb, one "Open the <label>" button, and the "All pages · N" fold. The Tool tone works in both themes. Each target is at least 44 px, and reduced motion keeps only the fades.

**Blocked by:** 01.

**Status:** in-review

- [x] "where is the trade analyzer", "how do I use the sim", "take me to the weekly reports", "midseason report?", and "wheres the trade thing" each show the right card on the live API (AT-1, AT-4, AT-5, AT-6, AT-7).
- [x] The address stays `/` until a tap on "Open" (AT-10).
- [x] The fold shows the other 5 pages of CPC (AT-11).
- [x] A reload shows the same card with no new ask request (AT-12).
- [x] A Menu link of the sim wins over `#sim` (AT-19). A kept key that the client lacks shows the none rows (AT-21).
- [ ] The card has the Tool tone, 44 px targets, fades only with reduced motion, and no internal name (AT-14, AT-15, AT-16, AT-17, card half).
