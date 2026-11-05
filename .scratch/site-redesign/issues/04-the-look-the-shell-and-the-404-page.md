# 04: The look, the shell, and the 404 page

Spec: `.scratch/site-redesign/PRD.md`. Acceptance tests AT-7, AT-8, AT-9, AT-10, AT-11, AT-13, and AT-32.

**App:** site

**What to build:** Every page gets the shell of the look: the top band, the dock on a phone, the pill bar on a desktop, the week chip with the strip of weeks, and the theme button. The parts of the look exist for the pages: the hero, the card, the tile, the round photo frame, and the motion. The 404 page is the first page in the look.

**Blocked by:** 01, 02, 03

**Status:** in-review

- [x] The dock stays at the bottom at every scroll on a phone, with Home, Week N, Rankings, Managers, and Trade. Each label is 11px or more.
- [x] The top band stays on screen at every scroll on a desktop, with the pill bar of full labels. The current destination is marked.
- [x] A tap on the week chip opens the strip of weeks, with the brand edge on the latest week. A tap on a week opens it.
- [x] The `layout` key of `[menu]` is gone from both `client.toml` files, and a `layout` key fails the build.
- [x] The hero shows the grid, the brackets, the glow, and one scan line. Content rises in a stagger. Reduced motion turns all motion off.
- [x] The 404 page shows the hero, "404", and the buttons "Go to Week N" and "Go Home". It is on the full floor, and the floor passes.
- [ ] The local dev server runs for Brian after the build.
- [ ] The evidence of AT-7, AT-8, AT-9, AT-10, AT-11, AT-13, and AT-32 is recorded in `EVIDENCE.md`.
