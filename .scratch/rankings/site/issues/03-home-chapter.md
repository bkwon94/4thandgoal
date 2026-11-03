# 03: The home chapter

**What to build:** The home page gets a chapter labelled "Power rankings" below Tools and above Weekly reports: the top three teams with their ranks, the biggest mover with its arrow and count, and a link to `/rankings`. The analyzer stays first and nothing pushes it down. A missing season file hides the chapter. The chapter uses the existing reveal and stagger, with the Weekly reports rows staggered after it.

Spec: pipeline repo `.scratch/rankings/pipeline/PRD.md`, section "The site".

**Blocked by:** 01 The reader and the route.

**Status:** ready-for-agent

- [ ] The home page renders the chapter with the top three, the biggest mover, and the link, in a test on the fixture.
- [ ] The chapter sits after Tools and before Weekly reports. The analyzer is the first item in the page.
- [ ] A missing file hides the chapter and the home page still renders, in a test.
- [ ] The stagger continues into the Weekly reports rows with no repeat delay.
- [ ] At 390 the chapter fits with no sideways scroll. Checked with agent-browser at 390 by 844.
- [ ] Every test passes and the static export builds.

## Comments

- 2026-10-22: built on `rankings-home` at `746a5d0`, two Opus reviews, one fix pass. Awaits Brian merge with `--no-ff`.
