# 06: Can a fourth question catch an Observation that claims more than the files show?

Map: `.scratch/evidence-flags/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

Ticket 02 found three evidence gaps of one kind: the Observation line claims more than the files show, or misstates a file. They are AT-50, AT-54, and AT-55 of easter-eggs. AT-50 caused the hard stop and the wait overnight. No draft question of ticket 02 catches them. Question (a) also missed AT-47 of manager-brain, because Jev took the Observation text as proof. Draft a question (d) that compares the Observation with the files alone, and replay it on these cases and the 44 PASS tests of ticket 02. Report the hits and false flags at cuts of 0.5, 0.7, and 0.9. Also test a version of (a) that sends no Observation text. Keep the scripts in the scratchpad, as ticket 02 did.

## Decision

The replay ran on 2026-11-10 for about $0.05, with 0 errors. The notes are in `decisions/06-research-observation-question.notes.md`.

- Question (d), in its best draft, asks one Noul per Observation sentence. At a cut of 0.7 it catches 2 of 4 (AT-54, AT-55), with 4 false flags in 44 PASS tests. The draft was tuned on the same cases, so the rate is optimistic.
- No draft catches AT-50 or AT-47. Jev reads "no axe incomplete item" as shown at 0.82, and the tap of AT-47 as shown at 0.97.
- Question (a) with no Observation text is worse at each cut. The Observation text did not cause the miss of AT-47.
- Most false flags come from the state, not the question: a shot past the limit of 4, a file cut at 3000 characters, or a claim in the evidence of another test.

So Jev catches 5 of the 7 past gaps at a cut of 0.7, and it misses AT-50, the gap that caused the hard stop. The research agent found it. The bar is the choice of Brian in ticket 03.
