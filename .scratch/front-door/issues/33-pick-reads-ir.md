# 33: The pick reads a starter on IR as out now, and an anchored search skips the partner filter

Spec: `.scratch/front-door/PRD.md`. Source: the live run of ticket 31, trade ideas for Bo Girds with the follow-up "id rather not trade a WR".

**App:** API

**What to build:** Bo Girds has Lamar Jackson on IR, so Fernando Mendoza QB50 plays QB now. Weak spots names QB as the weakest spot. The final pick kept no offer and wrote "a quarterback you do not need". Two parts.

1. The cause is in the measured facts of the pick sheet, not in the Jev state. The Jev state reads `lineup_now` and holds "QB: Fernando Mendoza (QB50)". The roster fit and the standing Measures read the season ahead, with Lamar at his projection, so for Walker for C.J. Stroud the sheet said "your lineup scores less" and "this trade gives some up". `6.depth.qb` said "go from 1 to 2" and counted Lamar. Only the Week line said "Jackson is on IR". The season horizon of `lineup_change` stays, because it is a deliberate rule with its own tests. The pick sheet now holds `<asker>.now`, from `weak_starting_slots` and `cannot_play_now`: the weak slots now and each starter who cannot play now, with his return. The depth fact adds the count of the players who can play now when it differs. The pick prompt has one neutral line on how to weigh `.now` beside the season facts. Claude makes the call.
2. An anchored search, such as "trade ideas for kenneth walker", skips the partner filter. The filter asks about the weakest slots, and the anchor names the player the trade turns on, so every partner goes on to the targets. The plain search keeps the filter.

`DOCUMENT_VERSION` is 25, so no list stored before this ticket serves.

**Blocked by:** 31

**Status:** in-review

- [x] The pick sheet of a Bo Girds offer holds `6.now`, with the weak QB slot now and Lamar Jackson as a starter who cannot play now, with his return week.
- [x] The depth fact reads "Of them, the QBs who can play now go from 1 to 2" when a QB above the line cannot play now.
- [x] The roster fit and the standing Measures keep the season horizon, and their tests do not change.
- [x] An anchored search asks no partner filter question, and every partner goes on. The plain search keeps the filter.
- [x] `DOCUMENT_VERSION` is 25.
- [x] Live on port 8133: the tap and the follow-up for Bo Girds, and "trade ideas for kenneth walker", each run twice.
