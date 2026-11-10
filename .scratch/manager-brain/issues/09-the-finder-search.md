# 09: The Finder search

Spec: `.scratch/manager-brain/PRD.md`. Acceptance tests AT-25, AT-27, AT-28, AT-29, and AT-52.

**App:** pipeline

**What to build:** The Finder searches as a manager does, with no math filter. Jev runs the partner filter on every other team, with four questions: does he have your need, can he spare it, do you have his need, and can you spare it. Code counts the depth, and only a partner with four yes answers gets a full search. Jev picks the targets on each side at p 0.6 or more, at most 4 per side. Code builds every 1-for-1, 2-for-1, and 1-for-2 offer from the targets only, with the hard rules: no kicker, no defense, no player out with no return week, and no handcuff. Jev makes the shortlist of the 10 offers with the highest product of the fair and need answers. Jev requests go in waves under the rate limits. The find request makes the partner optional, and a picked partner keeps the search to that partner.

**Blocked by:** 02

**Status:** in-review

- [x] A Find for Maye d'force B with U with no partner logs the partner filter on all 11 other teams and no 429 response.
- [x] With The Blue Tent as the partner, every offer is with The Blue Tent.
- [x] No offer holds a kicker, a defense, a player out with no return week, or a handcuff.
- [x] Every offer is 1-for-1, 2-for-1, or 1-for-2, and none is 2-for-2 or larger.
- [x] `make check-fast` passes.
