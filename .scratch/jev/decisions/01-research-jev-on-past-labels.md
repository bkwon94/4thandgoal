# 01: How well do Jev answers agree with past Claude verdicts?

Map: `.scratch/jev/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The cascade is safe only if Jev passes almost no sentence that the Claude check failed.
The saved `verify.json` files of past weeks hold the Claude verdict of each sentence, with its blurb and its facts.

Run live probes with `TYPESAFE_API_KEY` from `~/.secrets`, and use the `typesafe:typesafe-ai` skill. Find out:

1. The agreement of Jev answers with the Claude verdicts, by week. Count the sentences that Claude failed and Jev passed.
2. Which question text works best: one Noul per sentence, or atomic Nouls per sentence, such as "a cause no fact states" and "a rank no single fact states".
3. Which state works best: all chapter facts, or only the cited facts of each sentence.
4. The cost and the latency per blurb and per week.
5. The week 8 failures of implied meaning, such as "hoarded the rest of the hardware". Find out whether Jev catches them.

Write the findings to `decisions/01-research-jev-on-past-labels.notes.md`. Keep the names of managers out of tracked files (ADR 0021).

## Decision

The research agent ran on 2026-11-09. The findings are in `decisions/01-research-jev-on-past-labels.notes.md`. The spend was $0.348.

1. **The labels are weak.** `verify.json` keeps only `index`, `supported`, and `reason` per sentence, and `blurbs.json` keeps only the final attempt. No text of a failed sentence survives. The agent rebuilt 22 failed cases from the reasons, as set R, and used 247 passed blurbs, as set P.
2. **The best design** is one Noul per sentence, one request per blurb, with all chapter facts and the vocabulary in the state. Atomic Nouls flag too many true sentences. With only the cited facts in the state, fewer blurbs skip Claude for the same escapes.
3. **The vocabulary matters most.** With it, about twice as many blurbs skip Claude at 0.8 and 0.9, with no more escapes.
4. **The numbers.** An escape is a failed case that Jev passes. With a code check for the word "drop", the escapes of 22 are 4 at 0.8, 2 at 0.9, and 0 at 0.95. The share of blurbs that skip Claude is 43%, 17%, and 3%.
5. **The week 8 implied meanings** never pass at 0.7 or more.
6. **The cost** is about $0.0002 per blurb and under $0.003 per week. The median latency is 0.088 s per blurb.

Twenty-two cases give only a rough escape rate, about 5% to 40% at 4 of 22. Ticket 02 sets the bar with Brian.
