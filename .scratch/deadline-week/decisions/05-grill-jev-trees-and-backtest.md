# 05: Which Jev questions and decision trees does the Finder use, and what bar must the backtest pass?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

Jev does not reason. It answers tiny yes or no questions well, and code combines the answers in a decision tree. In manager-brain prototype 04, Jev atomic scored 16 of 24 trades, below Claude at 20. The questions were not small enough, and no backtest loop existed.

Decide, from the cut that research 01 finds:

1. Which steps of the Finder get a Jev decision tree, and the questions of each tree.
2. The backtest set: the 28 labelled trades of manager-brain, plus each bad Finder trade Brian finds.
3. The bar: the score that a change to a tree must keep or beat before it merges.

## Decision

Brian decided on 2026-11-18, after the Rivet post on Jev: Jev answers tiny questions, code decides, and the cases that a person marks wrong drive each change.

**1. The steps.** One Jev tree for Deadline week: the Spares tree.

- Code lists each player of one team at the position of a weak starting slot of the other team, with a backup above the line behind him. That is a count, so code does it.
- Jev asks one Noul per listed player: "Would {player} start over {weak starter} of {team} for the rest of the season?"
- Code puts the trade chart value of both players in the state as a fact, such as "the chart has Pacheco at 31 and the RB2 at 22". Jev compares no numbers, because code knows them exactly.
- Code decides. A side stops only if it lists no player, or if each listed player gets a clear no (below `NO_AT` 0.3). Any yes or unsure passes, as decision 01 set. A failed Jev call is an error, never a stop.
- The Spares tree replaces the four big questions of the Partner filter. The two "has" questions fold into the per-player Nouls.
- The Deadline board uses the same tree for the spares of each team. One tree feeds both.

Not now: the Accept tree and the split of the target question (later, see OUT OF SCOPE), and a tree for fair (out: a tree that combines fair answers ranks trades by a score, against `no-math-filters`). A 2-for-1 value rule, such as "the pair is worth 15 to 20% more", is a fact in the state, never a cut. Brian keeps `no-math-filters`.

**2. The backtest set.** Brian's marks, not the chart. The chart is a consensus score, and the post grades a tree against what a person marked wrong.

1. One run of the Spares tree on every cpc pair of week 11, about $0.01 in Jev.
2. A list of about 30 lines for Brian. Each line is one stop or pass with the answer that decided it, such as "Stopped Team B: Jev says Pacheco would not start over your RB2."
3. Brian marks the wrong lines, in about 10 minutes. Each wrong line, with his fix, is a Backtest mark.
4. Each bad Finder trade that Brian finds later becomes a Backtest mark at the Jev answer that let it through.

**3. The bar.** A change to the tree merges only if it passes all three rules:

1. No Backtest mark that the old tree got right breaks.
2. The count of right marks stays the same or rises.
3. The change does not touch `YES_AT` 0.7 or `NO_AT` 0.3, and no question names a player of a mark. A change improves the state, splits a question, or changes the code logic.

No held-out set yet: 30 marks are too few to split. Each later bad trade is a mark that the tree never saw. The backtest calls the live Jev, so `make check-fast` does not run it. It runs as one command, and its result goes into `EVIDENCE.md` for the Judge.
