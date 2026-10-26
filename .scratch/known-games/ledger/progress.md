# SDD ledger — plan: .scratch/known-games/PRD.md (tickets .scratch/known-games/issues/01-08)

Base: main 3656433. Worktrees ../cornerstone-fantasy-sleeper-weekly-report.known-games-NN, branch known-games-NN.
Flow: Opus builder with TDD per ticket -> task reviewer (spec + quality, Opus) -> fix rounds, 5 max, scoped re-review -> rebase on main, merge --no-ff, suite on main, push after Brian's word.
Reports: .scratch/known-games/ledger/NN-build.md. Review packages: .superpowers/sdd/PRD/.

## Pre-flight scan
| Pair | Produces / consumes | Finding |
| 01 -> 02 | 01 splits the stamp into a player bound and a standings bound; 02 moves the player bound to N | consistent |
| 02 -> 03, 04, 06, 08 | 02 defines the known-games block shape (games read, in progress, pending); 03 and 04 fill fields; 06 hashes the lines; 08 renders | consistent, 02 must define all fields |
| 05 alone | widens the due-back rule in the adjusters; touches no bound | no overlap with 01 |
| 07 alone | per-source max age in the refresh; touches no bound | no overlap with 01 or 05 |
| 01 vs 05 | 05 reads the standings bound via the due-back rule (back_inside uses stats_through) | merge order 01 then 05 may conflict on the field name; rebase 05 on main after 01 |
Ruling: 01, 05, 07 build in parallel in separate worktrees; 05 and 07 rebase onto main after 01 merges — cost if wrong: one rebase conflict to resolve by hand.

## State
- 2026-10-26 10:04: worktrees 01, 05, 07 from main 3656433. Three builders dispatched (01 opus, 05 opus, 07 sonnet).
- 07: built 774bf2d, test_live 27 pass, full suite 1088 before a line wrap. Reviewer out (opus).
- 05: NEEDS_CONTEXT. The week 6 fixture has 26 rostered players out with no returns row, so the rule changes 3 real week 6 trades, the finder fixture, and 12 tests. Ruling: the spec rule stands; the ticket's "every rubric test unchanged" criterion was wrong and is replaced. Form: widen lineup value, the fit note, and the gain time only; the trend and the gap keep the returns file. Tests whose subject is lineup value, fit, or injury pin the new grade, old and new value named in the report. Tests whose subject is unrelated get a setup fix. Cost if wrong: a test that guarded something else is weaker, and a week 6 grade Brian hand-checked moves. Sent to the builder.
- 07: review Approved, 0 Important, 6 minors. Ruling: fix minors 1, 2, 3, 4, 6 in one round; minor 5 (end to end through live_snapshot) deferred to the final review. Fix round 1/5.
- 01: built 0dda83d, 1085 pass, ruff clean, DONE_WITH_CONCERNS. Concern 1 (four tests gain one field): accepted, the document shape grows by one field. Concern 2: _due_back and _report_weeks read the fixed bound, which is right, but "standings_through" is the wrong name for a bound three rules read. Ruling: rename it to completed_through, the last completed week, and widen the glossary "Before the trade" line to name the due-back rule and the injury report. Cost if wrong: one rename to undo. Concern 3: the standings comment is ticket 02's to change; carried into 02's dispatch. Fix round 1/5.
- 01: fix round 1/5 done 55600d6 (rename to completed_through, glossary widened), 1085 pass. Task reviewer out (opus) on 3656433..55600d6.
- 07: fix round 1/5 done 2813fd2 (5 minors), 1088 pass. Scoped re-review out (sonnet) on 774bf2d..2813fd2.
- 07: re-review all 5 addressed. Minor (deferred): sources.py:55 passive line and a literal "6 hours"; out of scope: "now" in live.py:22 and sources.py:48 comments. Task 07: complete (commits 3656433..2813fd2, review clean). Merged --no-ff into main, suite on main below.
