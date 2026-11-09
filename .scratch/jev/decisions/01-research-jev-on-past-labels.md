# 01: How well do Jev answers agree with past Claude verdicts?

Map: `.scratch/jev/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

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

None yet.
