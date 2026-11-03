# 02: The expandable blurb row

**What to build:** A tap on a row opens the team's blurb under it, and a second tap closes it. On a phone the four component ranks sit inside the open row above the blurb. A row with an empty blurb list still opens on a phone to show the components, and on a wide screen has no control. The open and close use the motion helper: with motion off there is no transition. The rows reveal with the existing stagger. The control is a button with an accessible name and the open state on it.

Spec: pipeline repo `.scratch/rankings/pipeline/PRD.md`, section "The site".

**Blocked by:** 01 The reader and the route.

**Status:** ready-for-agent

- [ ] A tap opens the blurb, a second tap closes it, in a component test.
- [ ] The blurb sentences render in order from the row's list.
- [ ] With motion off the open state has no transition class, tested like the reveal test.
- [ ] Rows reveal with the existing stagger.
- [ ] The control is a button with an accessible name and `aria-expanded`.
- [ ] At 390 the open row shows the components above the blurb. Checked with agent-browser at 390 by 844.
- [ ] Every test passes and the static export builds.

## Comments

- 2026-10-22: built on `rankings-blurb` at `a68024d`, two Opus reviews, one fix pass. Awaits Brian merge with `--no-ff`.
