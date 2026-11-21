# 05: The strip motion, access, and fit

Spec: `.scratch/trade-block/PRD.md`. Acceptance tests AT-24, AT-25, AT-26, and AT-27.

**App:** site

**What to build:** A pick moves to the front of the strip with a spring of 0.4 s and no bounce, and with no motion when the reader turns motion off. A screen reader and a keyboard can build a block. The strip fits a phone in Safari, a tablet, and a desktop.

**Blocked by:** 03

**Status:** done

- [x] A pick moves to the front with a spring of 0.4 s and no bounce, and at once with reduced motion on.
- [x] Each item reads as a toggle with the player name, the position, and the pressed state.
- [x] Tab reaches the strip, the arrow keys move through it, and Space toggles a player.
- [x] At 390x660 in iPhone WebKit, iPad WebKit at 810x980 and 1080x740, and desktop at 1280x800, no text box overlaps another, no fixed bar covers content, and the strip fills the width of the hero.
- [x] The design bar holds: `transitions-dev`, `apple-design`, `critique`, and `polish` ran on the strip before the merge.

## Comments

The merge: `e2af53e9` on `trade-block-05`, merged into `trade-block` on 2026-11-21.
The proof: The full check of the Spec branch passed on 2026-11-21, with 1911 site unit tests and 1757 pipeline tests, and the Judge gave PASS to all 32 acceptance tests. AT-24 to AT-27 show the motion with motion off, the accessibility tree, the keyboard path, and the fit at four sizes in WebKit and Chromium.
The notes for a later ticket: the focus ring defect `outline-none focus-visible:outline-2` with no `outline-solid` is also in segmented-control.tsx, announcement.tsx, and sim-stage.tsx.
Read at least 10 files: AGENTS.md, apps/site/AGENTS.md, .scratch/trade-block/PRD.md, .scratch/trade-block/ACCEPTANCE.md, .scratch/trade-block/issues/05-the-strip-motion-access-and-fit.md, packages/analyzer/site/form/trade-block.tsx, packages/analyzer/site/form/trade-block.test.tsx, apps/site/playwright.config.ts, apps/site/e2e/finder-ledger.spec.ts, apps/site/e2e/grade-bar.spec.ts.
Closes with the squash merge of the spec PR.
