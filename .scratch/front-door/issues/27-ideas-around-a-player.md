# 27: Trade ideas around one named player

Spec: `.scratch/front-door/PRD.md`. Source: H15 (and the H6 follow-up) of `.scratch/front-door/HANDS-ON.md`.

**App:** API and analyzer

**What to build:** "trade ideas for kenneth walker" routes to Trade ideas, but `TradeIdeasRequest` carries no player and `FindRequest` has no field for one, so the search aims at the weakest slot again. The typed question now reaches the route. Jev picks the named player of the asker's roster or of another roster, and the direction: the manager gives him, or gets him. The find search keeps only offers with that player on that side. A tap of the Suggestion sends no question and works as now.

**Blocked by:** 25

**Status:** in-progress

- [x] `TradeIdeasRequest` takes an optional typed question; the site sends it for a typed route.
- [x] Jev picks the named player and the direction from the real rosters, one request.
- [x] `FindRequest` takes an optional anchor player and side; each offer of the search holds that player on that side.
- [x] An unsure pick falls back to the weakest-slot search, with a step line that says so.
- [x] The kept-Answer key holds the anchor, so a player search never serves the plain list.
- [ ] Live: "trade ideas for kenneth walker" for Bo Girds gives offers that send Walker away.

## Live run 2026-11-11

"trade ideas for kenneth walker" for Bo Girds: the pick is sure (gives 0.96, Kenneth Walker III 0.98). The step says
"Found Kenneth Walker III". The search built 41 offers, and each one sends Walker away. The pick step kept none: "No
offer on the list helps your lineup enough to send." Each partner target is a QB, because the target question aims at
the weakest slot of Bo Girds. A `trades_away` fact in the state did not move the targets. The live box stays open.
