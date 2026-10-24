# 06: The price

Spec: `.scratch/waiver/PRD.md`.

**What to build:** Every player in every bucket but drops carries a price: the bid to win, a whole
dollar, as a fact with its inputs in the numbers. The file also carries, per player, the last like
him, the most recent winning claim of the same position and bucket tier this season with the team and
the week, and the outbid counts per budget level, so the site can say "8 teams can outbid you" for any
viewer with no engine call.

The bid to win is the smallest whole dollar above the highest expected rival bid. A rival's expected
bid is his budget left times `NEED_SHARE`, 0.35 when he has fewer healthy starters at the position
than the lineup needs and 0.12 otherwise, capped at his budget left. A past winning claim for the
position this season raises the floor to that bid plus one. The price never exceeds the highest
budget left among the rivals. The bid history reads every waiver claim in the season's history with
the bid, the player, the position, the week, and whether it won.

**Blocked by:** 01 The week file, thin.

**Status:** ready-for-agent

- [x] The bid history across the saved weeks holds every claim with its bid and its result.
- [x] A rival with a positional need raises the price more than a rival without one.
- [x] A past winning claim at the position raises the floor to that bid plus one.
- [x] The price never exceeds the highest rival budget left, and it is a whole dollar.
- [x] The last like him names the team and the week, and it is empty when the history has none.
- [x] The outbid count per budget level is right for a viewer at 51 and at 9 on the week 6 budgets.
- [x] Every price is a fact with its inputs in the numbers. `NEED_SHARE` is a tunable.
- [x] Glossary gains **Bid to win** and **Last like him**.

## Comments

- The last like him matches on position alone, because a past claim has no bucket tier.
- The rival list holds every roster, the viewer's too, so a viewer's own need can raise his own price. This is a known limit.
