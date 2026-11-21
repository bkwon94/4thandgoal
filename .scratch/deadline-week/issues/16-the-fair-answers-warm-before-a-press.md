# 16: The fair answers warm before a press

Spec: `.scratch/deadline-week/PRD.md`. Decision 19. Acceptance tests AT-55 to AT-62 still cover the answers.

**App:** api

**What to build:** The API keeps a fair cache in its process. The key is the chart week and the player ids of each side, in the side order, and the value is the fair Noul answer of that order. A worker in the background builds the Value offers of all 66 team pairs at API start and asks each fair question that the cache does not hold. A changed roster or a new chart week gives new keys, and the worker asks only the new ones. The warm-up shares the one pacer and waits while a press is live. A press reads the cache first, asks each missing key live, and stores the answer. A miss is never an error. Step 2 and the pick stay live (decision 19).

**Blocked by:** 13

**Status:** done

- [x] A real test shows that the mean of the two side orders does not move when the labels `asker` and `partner` swap, or the fair state names no asker.
- [x] A test shows that a press of team A and a press of team B read the same cached answers for the offers between them.
- [x] A test shows that a moved player gives new keys only for the offers that hold him.
- [x] A test with a fixed clock shows that the warm-up sends no request while a press is live.
- [x] A real press for Bo Girds on a warm local API asks no fair question live and gives a Shortlist of 10.

## Comments

- Brian chose CPC only on 2026-11-20, because a warm-up of CPC costs about $1.46 per deploy and Norcal adds $1.72.

The merge: `deadline-week-16` merged into `deadline-week` as a fast-forward before `ca56f5e3` on 2026-11-20; review fixes and the Judge fix round followed on the same branch.
The proof: `make check-fast` passed at each merge, and the Judge gave PASS to all 72 tests, AT-1 to AT-73 with AT-42 retired, after one fix round.
Read at least 5 files: AGENTS.md, .scratch/deadline-week/PRD.md, .scratch/deadline-week/ACCEPTANCE.md, docs/agents/issue-tracker.md, .scratch/deadline-week/issues/16-the-fair-answers-warm-before-a-press.md.
Closes with the squash merge of the spec PR.
