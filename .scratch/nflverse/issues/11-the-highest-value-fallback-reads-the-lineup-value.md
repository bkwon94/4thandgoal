# 11 — The highest-value fallback reads the lineup value

Spec: `.scratch/nflverse/PRD.md`, "The trade rubric". Found in the ticket 10 review on 2026-10-24.

**What to build:** `_highest_value_player` in `src/cornerstone/rubric.py` picks the top player by trade value. When
the week has no chart, or a traded player is unlisted, it falls back to recent points per game. A player due back
has no recent games, so the fallback counts him as 0 and never picks him. Ticket 10 gave the roster fit his
projection ahead as his lineup value. The fallback reads that same lineup value, so a player due back can be the
highest-value player when the chart is missing.

**Why:** A grade with no chart otherwise treats a star due back as the least valuable player in the trade.

**Blocked by:** None.

**Status:** open

- [ ] With no chart, a trade of a player due back with a projection of 18 a game for a player at 10 a game names the due-back player as the highest-value player.
- [ ] With a chart that lists every player, the grade does not change.
- [ ] Every existing rubric test passes unchanged.
