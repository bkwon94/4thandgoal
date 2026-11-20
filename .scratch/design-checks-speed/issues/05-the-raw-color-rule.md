# 05: The raw color rule fails a color literal

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-3.

**App:** site

**What to build:** A plugin rule fails a hex, `rgb()`, `hsl()`, or `oklch()` literal in a `.tsx` file of the site code. It reads style objects and class strings.

**Blocked by:** 01

**Status:** ready-for-agent

- [x] A fixture with a hex color in a style object and `rgb(0 0 0)` in a class string fails once for each line.
- [x] The lint of all site code exits 0.
