# 01: The floor reads hero text by pixels

Spec: `.scratch/analyzer-stage/PRD.md`. Acceptance test AT-22.

**App:** site

**What to build:** The readability floor reads the contrast of hero text over the art layer. A pixel scan hides the text of each hero, takes a screenshot, finds the brightest pixel under the box of each text, and compares it with the text color. An axe "incomplete" result passes to the pixel scan only when its node sits inside a hero and its reason is a background image, a gradient, or an overlap. Every other incomplete result still fails. The plate still exists in this ticket, so the floor stays green. The prototype script in `~/plans/analyzer-stage-prototype/plate-05/` is a reference for the method; rewrite it properly.

**Blocked by:** none

**Status:** in-review

- [x] The floor runs the pixel scan on each hero of each page that it scans, in both clients, at 390 and 1280 px.
- [x] A unit test shows that an axe "incomplete" result outside a hero still fails the floor, and the failure names it.
- [x] A unit test shows that a hero where the pixel scan finds no text fails the floor, and the failure names it.
- [x] The floor passes in `cpc` and in `norcal` with the plate still on.
