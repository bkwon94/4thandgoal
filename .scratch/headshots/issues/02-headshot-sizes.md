# 02: Headshot sizes and the 390px check

**What to build:** The three headshot sizes read as one system: large on the Game Changer hero, medium on the award tiles, small on the leader rows. At 390px every leader row still holds on one line. The real week 6 page, rendered from the saved data on disk with no writer call, looks right at 390px and at 1024px.

**Blocked by:** 01 (Headshots, end to end)

**Status:** done

- [ ] Three sizes on the existing scale, no new tokens. The headshot is round or rounded to match the team avatar.
- [ ] At a 390 by 844 viewport, every leader row holds on one line with the headshot in place, measured with `agent-browser`.
- [ ] The tile keeps its label, name, points, and sub line readable with the headshot in it.
- [ ] Screenshots of the hero, the tiles, and the boards at 390px, and of the boards at 1024px, saved for Brian's review.
- [ ] `uv run pytest -q` passes.

## Comments

2026-10-20: sizes landed in `25e68a2`, review fixes in `3cdb7e7`. Brian then asked for a fused hero and a grey blend. A four-variant prototype ran in the session scratchpad; Brian picked A, "Bleed", with the text block under the label. Folded in as `6180ec6`: the Game Changer headshot bleeds off the card with a red glow and a gradient, and every headshot rule lost its disc background so the image sits on the card. The headshot PNG has its own transparency, so no knockout step is needed.
