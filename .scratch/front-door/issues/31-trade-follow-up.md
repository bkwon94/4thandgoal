# 31: A follow-up to trade ideas routes to trade ideas, with its limit

Spec: `.scratch/front-door/PRD.md`. Source: H18 of `.scratch/front-door/HANDS-ON.md`.

**App:** API and site

**What to build:** after a Trade ideas Answer, "id rather not trade a WR" routed to the free answer, which listed depth and made no new offer. The router reads the turns of the Thread, but the trade turn held only its offer count, and the Trade ideas wording takes no limit. Jev now routes a follow-up that refines the earlier ideas to Trade ideas, from the context of the Thread. Jev reads the limit from the follow-up (a position or a player to keep, or to aim at), and trade ideas runs again with it. The limit is the manager's own hard rule, so code drops each offer that breaks it.

**Blocked by:** 27, 30

**Status:** open

- [ ] The Trade ideas wording covers a follow-up that refines the earlier ideas.
- [ ] The route eval holds at least 6 follow-ups, each after a trade ideas turn, and each routes to Trade ideas; the bar holds.
- [ ] "what's the weather" after a trade ideas turn still does not route to Trade ideas.
- [ ] Jev reads the limit from the follow-up in one request; the search drops each offer that breaks it.
- [ ] Live: Trade ideas for Bo Girds, then "id rather not trade a WR", gives offers with no WR sent away.
