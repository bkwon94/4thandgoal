# 02: Which reason shows when the steps of a side cancel?

Map: `.scratch/uneven-trade/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

The fairness reason of a side names what moved its letter. A side with one up step and one down step does not move. The deal row then shows, such as "about even".

With a superstar step, Teehee in the week 9 trade starts at B, gets the superstar step up and the roster-fit step down, and ends at B. The deal row hides the RB loss, which is close to the first bug Brian reported. The spec needs one rule for this case: the deal row, both steps, or the down step.

## Decision

Brian decided it in a grill on 2026-11-05.

The fairness reason of each side comes from the net sum of its adjuster steps, before the clamp. "First" means first in rubric order.

1. A net above zero shows the first up step.
2. A net below zero shows the first down step.
3. A net of zero, with steps, shows the first up step, then "but", then the first down step.
4. No steps at all shows the deal row.

The net sum decides, not the change of the letter. A side at A with one up step does not move, but it still shows its gain.

With this rule, Teehee in the week 9 trade reads: "Walker is a top-8 player this week, but you go from 2 RBs in the top 36 to 1 and keep 4 WRs in the top 36." The spec sets the exact text of the superstar step.
