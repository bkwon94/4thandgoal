# 01: Headshots, end to end

**What to build:** A reader sees a headshot on each award tile, each leader row, and the Game Changer hero. The build fetches each one from the Sleeper CDN through the avatar fetch hook, saves it under `headshots/` in the week directory, and falls back to a default silhouette when the fetch fails. A DEF shows its NFL team logo. Markup is correct; the size pass is ticket 02.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] A headshot URL comes from the player ID. A DEF line maps to the team logo URL with a lowercase abbreviation.
- [ ] The render step fetches every headshot on the tiles, the rows, and the hero, once per player, through the same `fetch_bytes` hook as the avatars, and saves each as `headshots/{player_id}.png` in the week directory.
- [ ] A fetch that returns `None` gives the default path to a new `static/headshot-default.svg`.
- [ ] The context carries a `headshots` map from player ID to a page-relative path. One template macro renders `img.headshot` with `alt=""`.
- [ ] The tile, the hero, and the row each carry the image. Trade cards and matchup cards do not change.
- [ ] Render seam tests cover the map, the DEF URL, the fallback, the saved file, the no-duplicate fetch, and the three sections.
- [ ] `uv run pytest -q` passes.
