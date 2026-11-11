# 44: The weak spots facts hold one hole scale, and "weakest" means the worst slot rank

Spec: `.scratch/front-door/PRD.md`. Source: the evidence round of 2026-11-11 (AT-8, AT-18, AT-20). 4 of 7 live weak spots runs of Lil Fridge ended as the honest miss.

**App:** api

**What to build:**

- In `apps/api/src/cornerstone_api/personal_facts.py` (`topic_facts`, weak spots only), keep only the rows of `weak_starting_slots` that `starters` does not show: an empty slot, or a player who is not among the starters, such as the stand-in for a starter on IR. Change the meaning of `weak_starting_slots` in `FACT_MEANINGS` to say so. The slice then has one hole scale, the projected scale of the data block.
- In `apps/api/src/cornerstone_api/personal_wording.py`, make `TOPIC_ASKS["weak_spots"]` say that the weakest position is the one with the worst `rank` in `slot_ranks`, the same order as the block.

Cause: `starters` takes the projected rank of the roster grade. `weak_starting_slots` (`trade_jev.weak_slot_rows`) takes the points-per-game rank. Both name it `projected_rank_at_position`. So "no hole" is true by one list and false by the other, and Jev fails it.

**Blocked by:** none

**Status:** in-review

- [x] Red first: `test_weak_spots_slice_has_one_hole_scale` in `apps/api/tests/test_personal_topics.py`. Each weak row with a player names a player not in `starters`.
- [x] `test_each_weak_starting_slot_of_weak_spots_is_a_row` reads the IR fixture. `test_weak_spots_read_a_starter_on_ir_as_out_now_as_trade_ideas_do` stays green.
- [x] The weak spots ask defines "weakest" as the worst slot rank.
- [ ] Live: weak spots of Lil Fridge passes the check on the first text in at least 4 of 5 runs.

## Notes

- Trade ideas keep the points-per-game scale. Brian chose to log that as a follow-up, not to change it here.
- Raw Jev probes of the diagnosis: `/private/tmp/claude-503/-Users-brian-kwon-repos-cpcfantasyfootball/4d723efb-48cd-4a3b-af4f-6d2df841dc1d/scratchpad/weak-spots-checks.jsonl`.
- The check reads `FACT_MEANINGS`, not `TOPIC_ASKS`. So `FACT_MEANINGS` holds `weakest_position` too: the position with the worst `rank` in `slot_ranks`. A probe on the live slice: "Your weakest position is QB, which ranks 7th of 12" went from 0.63 to 0.98, and the false "RB" claim went from 0.20 to 0.06.
- Live after the fix: 3 of 5 runs pass on the first text, and 5 of 5 end as checked. The two first-text fails sit at 0.69 and 0.70. One drops "inside the starter count" from `depth_means`. One adds "so they are not a worry". Neither is the hole scale.
