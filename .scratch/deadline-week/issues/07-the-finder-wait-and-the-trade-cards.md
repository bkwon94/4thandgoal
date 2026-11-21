# 07: The Finder wait and the trade cards

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-12, AT-32, AT-36, AT-37, AT-38, AT-39, and AT-40.

**App:** both

**What to build:** In Find mode, a press shows the same wait as the grade. `StageLines` gets one change: a list of one line holds until the caller sends the next line, then swaps with the same motion. The Finder feeds it the real step lines of the stream. The avatars of the teams light up in turn as the stream reports each team read. The switch locks during the wait. Up to 3 trades land as cards in one list under the hero: the Lean, a Case of at most 3 lines with the condition first, the Bullets folded, and no headline. A tap on a card opens the trade in Grade mode, already graded with the read that the find route sent, with no second grade. A failed find shows the error line and Try Again. The copy names no Jev, no Advisor, no Finder, and no Brian.

**Blocked by:** 05, 06

**Status:** done

- [x] The wait shows one real step at a time in `StageLines`, and each line holds until the next step ends.
- [x] A tap on a card makes no analyze request, and the analyzer shows the read of the card.
- [x] The switch stays on Find during a wait.
- [ ] The text of each page, in each state of Deadline week, has none of the banned words of AT-12.

## Comments

The merge: `d008b926` merged `deadline-week-07` into `deadline-week` on 2026-11-19; review fixes and the Judge fix round followed on the same branch.
The proof: `make check-fast` passed at each merge, and the Judge gave PASS to all 72 tests, AT-1 to AT-73 with AT-42 retired, after one fix round.
Read at least 5 files: AGENTS.md, .scratch/deadline-week/PRD.md, .scratch/deadline-week/ACCEPTANCE.md, docs/agents/issue-tracker.md, .scratch/deadline-week/issues/07-the-finder-wait-and-the-trade-cards.md.
Closes with the squash merge of the spec PR.
