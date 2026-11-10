# 02: Which glossary terms go, change, or arrive

Map: `.scratch/manager-brain/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

With no letter and no step, these analyzer terms of `GLOSSARY.md` go or change meaning: Rubric, Grade, Start letter, Adjuster, Breakdown, Factor, Deal row, Roster row, Silent row, Factor lean, and the rank of the Finder. Decide each term, and name the new terms: the fact sheet of the judge, the manager bullet, the partner filter, the shortlist. Decide if the change needs an ADR, because it reverses the rubric design.

## Decision

Brian decided each term on 2026-11-09. The glossary changes sit in `GLOSSARY.md` on the Spec branch.

1. **Advisor** names the part that makes the call. "Judge" is the Workflow subagent, so the analyzer may not use it.
2. **Grade** stays, with a new meaning: the whole read of the Advisor, with no letter. "Grade the Trade" and the Grade limit keep their names.
3. **Lean** replaces Verdict, Decision, and Answer: Send it, Lean yes, Gut call, Lean no, or Pass, one word in code and on the page. **Case** is the advice under it. The analyzer no longer uses "verdict", so the word stays with the Test verdict.
4. **Bullets** are 3 to 5 sentences per side, each on a fact, each with a **Mark**: for, against, or even. Factor, Deal row, Roster row, Standing row, Silent row, and Factor lean go.
5. Rubric, Start letter, Breakdown, and Highest-value player go. **Adjuster** becomes **Measure**: it turns raw data into a fact and moves nothing. **Consolidation** keeps its word and loses its margins. **Playbook** is new.
6. Contender, Seller, and Middle team go. The Advisor reads the race group (In, Bubble, Out) and the playoff odds. In firms up, Bubble takes risks, Out by odds takes the biggest swings, and an eliminated team hears so plainly. A bye in the trade week is now a fact for every side, not a hole for a middle team.
7. Inner words keep the code words and "trade value" and "return bet". "Star", "opportunity", and "win-now move" are free.
8. **Fairness** is set by the Advisor. **Finder**, **Partner filter**, and **Shortlist** follow the Stage 1 decisions.
9. ADR 0030 "The Advisor judges, and code measures" records the change, as proposed until the spec merges. It supersedes ADR 0003 and ADR 0004 in part. ADR 0029 on `main` is the Jev vendor ADR.

The race group is a term of the site language today. The spec must give the pipeline the same term.
