# 36: A search with no offers runs a wider pass, so every trade ask gives an idea

Spec: `.scratch/front-door/PRD.md`. Source: H15, H18, H21 of `.scratch/front-door/HANDS-ON.md`.

**App:** analyzer and API

**What to build:** "what can i get for kenneth walker" and "id rather not trade a WR" built 0 offers, because the target question found no player on any partner. Ticket 35 shows ideas only when the search builds offers. When a search builds 0 offers, it now runs one wider pass: each partner offers its best player at the asker's need (or near the anchor's value for an anchored search), with the limit of ticket 31 kept. The pick ranks those as ideas with reasons, through the near ideas of ticket 35.

**Blocked by:** 35

**Status:** done

- [x] A search that builds 0 offers runs one wider pass in finder_search.py, with no Jev target question.
- [x] The wider pass gives at most one 1-for-1 idea per partner, at most 12, by a plain rule.
- [x] The wider pass keeps the limit of ticket 31 and the anchor side of ticket 27, and skips a partner whose request failed.
- [x] The offers of the wider pass go to the pick of ticket 35, so the near ideas give reasons.
- [x] The step lines "Looking wider for ideas" and "Looked wider for ideas" tell the manager.
- [x] The 0-offer line of ticket 35 shows only when the wider pass also builds 0 offers.
- [x] `DOCUMENT_VERSION` is 27, so no empty list stored before this ticket serves.
- [x] Live on port 8136, fresh cache, Bo Girds: the Walker ask, and the tap then "id rather not trade a WR", each twice.

## Build 2026-11-11

The rule of each partner, in `wider_offers`:

- The asker gets the anchor of a "gets" search. Else one player at the position to get of the limit. Else, for a
  "gives" anchor, one player at the position of the anchor, with the Season rank nearest his: a like-for-like swap.
  Else one player at a weak slot of the asker, or at any position when the asker has no weak slot.
- The asker gives the anchor of a "gives" search. Else his player at a weak slot of the partner, or his spare at any
  position when none fits.
- A player off the lineup now comes first, because a team gives up a spare more easily. Then the best Season rank.

Why: the rule is short and the manager can follow it. Each idea fills a need of a side, or swaps like for like. It
is a candidate set for the pick to judge, not a filter that decides a trade. One idea per partner keeps the pick sheet
at 11 offers in a league of 12.

## Live run 2026-11-11

The second run of each ask served the kept Answer.

- "what can i get for kenneth walker": the targets built 0, and the wider pass built 11. The pick kept 1 and gave 2
  near ideas. The pick: Walker for Jahmyr Gibbs. Near 1: Walker for Christian McCaffrey, "McCaffrey's snap share is 60
  percent and falling, so you swap a steady workload for a shrinking one." Near 2: Walker for James Cook III, "Cook's
  target share is 6 percent, so you give up a better player for a back with a thinner role."
- The tap: 4 built, no wider pass. The pick: Matthew Golden for Josh Allen, with 2 near ideas.
- The tap then "id rather not trade a WR" (limit `keep_positions: ["WR"]`): the targets built 1 this run, so no wider
  pass ran. The pick kept 0 and gave 1 near idea: McBride for Drake Maye, "You give up TE1 McBride and are left with no
  TE in the top 24, while you already have a QB in the top 24 to cover Jackson's absence."

## Comments
- Closes with the squash merge of the spec PR.
