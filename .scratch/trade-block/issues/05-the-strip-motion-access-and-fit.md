# 05: The strip motion, access, and fit

Spec: `.scratch/trade-block/PRD.md`. Acceptance tests AT-24, AT-25, AT-26, and AT-27.

**App:** site

**What to build:** A pick moves to the front of the strip with a spring of 0.4 s and no bounce, and with no motion when the reader turns motion off. A screen reader and a keyboard can build a block. The strip fits a phone in Safari, a tablet, and a desktop.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] A pick moves to the front with a spring of 0.4 s and no bounce, and at once with reduced motion on.
- [ ] Each item reads as a toggle with the player name, the position, and the pressed state.
- [ ] Tab reaches the strip, the arrow keys move through it, and Space toggles a player.
- [ ] At 390x660 in iPhone WebKit, iPad WebKit at 810x980 and 1080x740, and desktop at 1280x800, no text box overlaps another, no fixed bar covers content, and the strip fills the width of the hero.
- [ ] The design bar holds: `transitions-dev`, `apple-design`, `critique`, and `polish` ran on the strip before the merge.
