# 05: The raw color rule fails a color literal

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-3.

**App:** site

**What to build:** A plugin rule fails a hex, `rgb()`, `hsl()`, or `oklch()` literal in a `.tsx` file of the site code. It reads style objects and class strings.

**Blocked by:** 01

**Status:** done

- [x] A fixture with a hex color in a style object and `rgb(0 0 0)` in a class string fails once for each line.
- [x] The lint of all site code exits 0.

## Comments

The merge: `887d6456` on `design-checks-speed` on 2026-11-20; review fixes on fix branches a to n; Judge fix round on AT-13 (evidence only).
The proof: `make check-fast BASE=main` passed at each merge, 3 green CI runs on 4d5f4d13 gave a median of 315 s, and the Judge gave PASS to AT-1 to AT-39.
Read at least 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/design-checks-speed/PRD.md, .scratch/design-checks-speed/ACCEPTANCE.md, .scratch/design-checks-speed/issues/05-the-raw-color-rule.md.
Closes with the squash merge of the spec PR.
