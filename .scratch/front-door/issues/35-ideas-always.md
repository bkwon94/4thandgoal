# 35: Trade ideas always give ideas

Spec: `.scratch/front-door/PRD.md`. Source: H21 of `.scratch/front-door/HANDS-ON.md`.

**App:** API, analyzer, and site

**What to build:** trade ideas are ideas. When the search builds offers but the final pick would send none, the Answer still shows the best ideas it weighed, at least one and at most 3, each with the reason it fell short, in plain words. When the pick keeps offers, the Answer can also list the near misses with their reasons. Only a search that builds 0 offers shows no idea, and it says why (for example, no team has a player who fits).

**Blocked by:** 33

**Status:** in-review

- [x] The pick call returns up to 3 near ideas, each with an offer, a reason, and its one fact, in the same call.
- [x] With no pick and a shortlist, the pick must give at least one near idea, or the call retries once.
- [x] A near reason gets the guards of a Bullet and the Jev check of a Bullet (log only). A failed one drops.
- [x] No pick and no near idea that stands gives the shortlist fallback, so a list with offers always shows one.
- [x] A search with 0 offers says why: no team passed the filter, or no player fits the ask.
- [x] The site shows the near ideas with the offer rows, a quieter style, and the reason under each.
- [x] The label is "Ideas, none a clear win" with no pick, and "Also weighed" after the picks.
- [x] The trade turn of the chat context names each near idea and its reason.
- [x] `DOCUMENT_VERSION` is 26.
- [x] Live on port 8135, fresh cache, Bo Girds: the tap, the Walker ask, and the tap then "id rather not trade a WR".

## Live run 2026-11-11

The second run of each ask served the kept Answer.

- The tap: 14 built, 1 kept, 2 near. The pick: Zay Flowers for Drake Maye. Near 1: Matthew Golden for Maye, "Giving
  up Matthew Golden for Drake Maye leaves your lineup scoring less." Near 2: Parker Washington for Maye, "Parker
  Washington alone is not enough for Drake Maye, so the other manager would likely say no."
- "what can i get for kenneth walker": Jev found Walker (gives). 0 built, so no idea and the line "No team has a player
  who fits this ask, so no trade came up." Each partner gave no target to take the place of Walker.
- The tap then "id rather not trade a WR": the limit kept WR. 0 built, with the same line.

Open for Brian: the Walker ask built 0 offers this week, where ticket 27 built 4 to 41. The anchor target question now
answers no for each player of each partner. That is the search, not the pick, so this ticket leaves it.
