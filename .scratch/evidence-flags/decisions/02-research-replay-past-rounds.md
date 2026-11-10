# 02: Which past labels count as a real evidence gap, and how well does Jev flag them?

Map: `.scratch/evidence-flags/MAP.md`.

**Kind:** research

**Blocked by:** 01

**Status:** done

## Question

Git holds 16 rounds of `VERDICTS.md` with their `EVIDENCE.md` and `ACCEPTANCE.md`. Easter-eggs has four rounds with a FAIL or BLOCKED, and manager-brain has one. Sort each FAIL and BLOCKED into one of two groups: an evidence gap, such as missing data or still shots for motion, or a defect in the product. Then replay Jev on the evidence of each round, with draft questions. Report the hits, the misses, and the false flags on PASS tests. Keep the questions, the criteria, and the thresholds in one module, per the `typesafe:typesafe-ai` skill. Write no product code into `main` or the Spec branch. The replay script lives in the notes folder or the scratchpad.

## Decision

The replay ran on 2026-11-10 against `jev-1.14.0`, for about $0.05. The notes are in `decisions/02-research-replay-past-rounds.notes.md`. The scripts and raw results stay in the session scratchpad.

- The 12 FAIL and BLOCKED results of five rounds hold 7 evidence gaps and 5 defects.
- The gaps have three kinds: a fact that no file shows (2), motion with only still shots (2), and an Observation that claims more than the files show (3).
- Question (a), the facts, catches 1 of 2 at a cut of 0.7, with 2 false flags in 44 PASS tests. Jev took the Observation text as proof.
- Question (b), motion, catches 2 of 2 at 0.7 with 0 false flags in 44, after code finds the video or timed frames. The draft was tuned on the same cases, so the result is optimistic.
- Question (c), cut-off text, catches AT-41 at 0.98. It flags real cut text that the test does not ask about, so it must ask only about the text that the Then line names.
- No draft question catches the third kind of gap. Ticket 06 takes it.
- One image costs about one input token per 380 px. A shot is scaled, then cut into tiles of 1568 px, at most 2 per shot and 4 shots per test.

The research agent found it. The bar is the choice of Brian in ticket 03.
