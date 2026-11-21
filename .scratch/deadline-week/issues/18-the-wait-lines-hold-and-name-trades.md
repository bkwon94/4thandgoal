# 18: The wait lines hold and step 5 names real trades

Spec: `.scratch/deadline-week/PRD.md`. Decision 20. Acceptance tests AT-36 and AT-73.

**App:** both

**What to build:** Each step line of the Finder wait stays on screen at least about 1.5 s, and holds until the next step starts. The stream sends the trades of the Shortlist at step 5, by the names of their players. On step 5, the line changes about every 3 s, and each line names one Shortlist trade, such as "Weighing Walker for Lawrence, Pollard, Moore". The lines stop when the first card shows. Copy names no internal tool and states no time. Use the design bar of the repo: transitions-dev, apple-design, critique, and polish.

**Blocked by:** 17

**Status:** done

- [x] A site test with a fixed clock shows each step line on screen at least 1.5 s, even when the steps end faster.
- [x] A test shows that the stream sends the Shortlist trades at step 5, by the names of their players.
- [x] A site test with a fixed clock shows at least 3 step 5 lines, each held about 3 s, each naming a Shortlist trade.
- [x] A real press on a local build shows two step 5 lines that name real Shortlist trades, at 375 px, in both themes.

## Comments

The merge: `deadline-week-18` merged into `deadline-week` as a fast-forward before `6b985711` on 2026-11-20; review fixes and the Judge fix round followed on the same branch.
The proof: `make check-fast` passed at each merge, and the Judge gave PASS to all 72 tests, AT-1 to AT-73 with AT-42 retired, after one fix round.
Read at least 5 files: AGENTS.md, .scratch/deadline-week/PRD.md, .scratch/deadline-week/ACCEPTANCE.md, docs/agents/issue-tracker.md, .scratch/deadline-week/issues/18-the-wait-lines-hold-and-name-trades.md.
Closes with the squash merge of the spec PR.
