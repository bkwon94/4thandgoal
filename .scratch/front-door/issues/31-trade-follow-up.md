# 31: A follow-up to trade ideas routes to trade ideas, with its limit

Spec: `.scratch/front-door/PRD.md`. Source: H18 of `.scratch/front-door/HANDS-ON.md`.

**App:** API and site

**What to build:** after a Trade ideas Answer, "id rather not trade a WR" routed to the free answer, which listed depth and made no new offer. The router reads the turns of the Thread, but the trade turn held only its offer count, and the Trade ideas wording takes no limit. Jev now routes a follow-up that refines the earlier ideas to Trade ideas, from the context of the Thread. Jev reads the limit from the follow-up (a position or a player to keep, or to aim at), and trade ideas runs again with it. The limit is the manager's own hard rule, so code drops each offer that breaks it.

**Blocked by:** 27, 30

**Status:** in-review

- [x] The Trade ideas wording covers a follow-up that refines the earlier ideas.
- [x] The route eval holds at least 6 follow-ups, each after a trade ideas turn, and each routes to Trade ideas; the bar holds.
- [x] "what's the weather" after a trade ideas turn still does not route to Trade ideas.
- [x] Jev reads the limit from the follow-up in one request; the search drops each offer that breaks it.
- [ ] Live: Trade ideas for Bo Girds, then "id rather not trade a WR", gives offers with no WR sent away.

## Build 2026-11-11

The limit folds into the pick of ticket 27: one Jev request asks the 4 pick questions and 8 limit questions, with the
turns of the Thread in the state. The limit has the positions and the player to keep, and one position to get. A player
to get stays the anchor of ticket 27. The search asks no target question of a player that the limit keeps, and drops
each offer that breaks the limit. `DOCUMENT_VERSION` is 24.

The route eval: 50 of 54, bar 48. All 7 follow-ups route to Trade ideas, and "what's the weather" is a miss.

## Live run 2026-11-11

Bo Girds, Trade ideas (3 offers, each sends a WR), then "id rather not trade a WR" with that turn. The route was Trade
ideas (`fits_topic` 0.94, then 0.95). The limit was `keep_positions: ["WR"]`. The search built 32 offers, and none sends
a WR: each sends Walker, Kyren Williams, or McBride for a QB. The pick kept none, with the empty line "No offer on the
list helps your lineup enough to send, since each one gives up a top starter at a thin spot for a quarterback you do
not need." The second run served that kept Answer under the key of the limit. The live box stays open: the rule holds,
but no offer shows. Brian decides if the empty line is the right answer.
