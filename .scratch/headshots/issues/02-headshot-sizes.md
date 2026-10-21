# 02: Headshot sizes and the 390px check

**What to build:** The three headshot sizes read as one system: large on the Game Changer hero, medium on the award tiles, small on the leader rows. At 390px every leader row still holds on one line. The real week 6 page, rendered from the saved data on disk with no writer call, looks right at 390px and at 1024px.

**Blocked by:** 01 (Headshots, end to end)

**Status:** ready-for-agent

- [ ] Three sizes on the existing scale, no new tokens. The headshot is round or rounded to match the team avatar.
- [ ] At a 390 by 844 viewport, every leader row holds on one line with the headshot in place, measured with `agent-browser`.
- [ ] The tile keeps its label, name, points, and sub line readable with the headshot in it.
- [ ] Screenshots of the hero, the tiles, and the boards at 390px, and of the boards at 1024px, saved for Brian's review.
- [ ] `uv run pytest -q` passes.
