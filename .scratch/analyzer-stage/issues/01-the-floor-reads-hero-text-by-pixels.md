# 01: The floor reads hero text by pixels

Spec: `.scratch/analyzer-stage/PRD.md`. Acceptance test AT-22.

**App:** site

**What to build:** The readability floor reads the contrast of hero text over the art layer. A pixel scan hides the text of each hero, takes a screenshot, finds the brightest pixel under the box of each text, and compares it with the text color. An axe "incomplete" result passes to the pixel scan only when its node sits inside a hero and its reason is a background image, a gradient, or an overlap. Every other incomplete result still fails. The plate still exists in this ticket, so the floor stays green. The prototype script in `~/plans/analyzer-stage-prototype/plate-05/` is a reference for the method; rewrite it properly.

**Blocked by:** none

**Status:** done

- [x] The floor runs the pixel scan on each hero of each page that it scans, in both clients, at 390 and 1280 px.
- [x] A unit test shows that an axe "incomplete" result outside a hero still fails the floor, and the failure names it.
- [x] A unit test shows that a hero where the pixel scan finds no text fails the floor, and the failure names it.
- [x] The floor passes in `cpc` and in `norcal` with the plate still on.

## Comments

The merge: `a5d2b101` merged into `analyzer-stage` on 2026-11-16; review fixes `a8f2b48d` and `4eb5bef2`; Judge fix round `7b1d09c7`.
The proof: `make check-fast` passed at each merge, the full check passed on 2026-11-17, and the Judge gave PASS to AT-1 to AT-34 after one fix round.
Read at least 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/analyzer-stage/PRD.md, .scratch/analyzer-stage/ACCEPTANCE.md, .scratch/analyzer-stage/issues/01-the-floor-reads-hero-text-by-pixels.md.
Closes with the squash merge of the spec PR.
