# 01: Remove the Butterfingers award

**What to build:** The Awards section shows four tiles: Top Scorer, MVB, Underperformer, and Overachiever. No tile, fact, vocabulary entry, or test names Butterfingers. The drop note under Awards is gone. The drop lines, the drop facts, the drop swing, and the nflverse drop fetch stay, so the matchup chapters still cite them.

**Blocked by:** None (can start immediately)

**Status:** done

- [ ] The award key leaves the award model, the award computation, the award titles, the tile keys, and the render context.
- [ ] The Awards chapter cites no `AW.butterfingers` fact and no rank or history fact for that award. `W.drops` stays in the chapter.
- [ ] The writer vocabulary has no Butterfingers entry. The drop and drop value entries stay.
- [ ] The page shows no drop note for any drop source.
- [ ] A bundle with drops still has its drop facts and its drop swing facts.
- [ ] Tests at the bundle seam and the render seam cover the four tiles, the missing note, and the kept drop facts. Tests that covered the award are removed or rewritten.
- [ ] `uv run pytest -q` passes.
