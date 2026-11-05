# 04: The fairness reason names what moved the letter

Spec: `.scratch/uneven-trade/PRD.md`. Acceptance tests AT-9, AT-10, AT-11, and AT-12.

**App:** pipeline

**What to build:** The net sum of the adjuster steps of each side, before the clamp, picks its fairness reason. A net above zero shows the first up step. A net below zero shows the first down step. A net of zero with steps shows the first up step, then ", but ", then the first down step. No steps shows the deal row.

**Blocked by:** 02

**Status:** done

- [x] A fairness test grades trade W first, test-first, and shows "Fair." Teehee's reason is the superstar reason, then ", but ", then its roster-fit reason.
- [x] Fairness tests cover a net below zero, no steps, and a side at A with a net above zero.
- [x] The down reason in a joined reason starts in lower case, unless its first word is a name.
- [x] The fairness state and the side that gives more do not change for any present fairness test.
- [x] The `analyze` target gives the fairness line of AT-9 for trade W.
