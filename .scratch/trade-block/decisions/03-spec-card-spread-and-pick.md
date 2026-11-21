# 03: How the cards spread across the block players

Map: `.scratch/trade-block/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** done

## Question

With two or three block players, the up to five cards must not all send the same player. The Shortlist already puts the best offer of each player that the asker gives near the top. The spec records how the Shortlist and the pick spread the cards across the block players, and what the Advisor pick gets told about the block. It also records if the code keeps the name `Anchor` or changes to `trade_block`.

## Decision

`varied` counts only block players in its tier of "the best offer of each player that the asker gives", so the best offer of each block player comes first. The pick gets the names of the block players, and one prompt rule: when the shortlist holds a fair offer for a block player, at least one pick sends him. The code names the field `trade_block`; `Anchor` stays only for the "gets" ask. Recorded in `PRD.md`, which Brian approved on 2026-11-21.
