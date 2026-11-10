# 09: Does the Jev route pick the right Topic?

Map: `.scratch/front-door/MAP.md`.

**Kind:** prototype

**Blocked by:** 01, 03

**Status:** done

## Question

Run the Jev route on about 30 real questions from managers. Check the Topic it picks and the answer to "Can the facts of the week answer this?". Decision 12 widened a free answer to this season, so test the second question as "Can this season's data answer this?". Test also a Jev question for the team that a question names, and one for off-topic or abuse. Load `typesafe:typesafe-ai` first. Brian reads the results. The spec needs a known hit rate before the ask box goes live.

## Decision

Brian, 2026-11-10, after the prototype ran the Jev route on 43 questions with `jev-1.14.0`. 15 questions are real, from Brian. 28 are written by Claude and marked as such. One request per question had 7 typed questions: a Choice of the 13 Topics, a Choice of the 12 teams, and Nouls for "a Topic fits", "this season's data can answer", "about the league", "abuse", and "names a team". Code made the route at 0.7 for yes and 0.3 for no.

1. When "a Topic fits" is unsure and "this season's data can answer" is yes, the route gives a free answer. The top Topic shows under it as a Suggestion. Reason: a stat lookup such as "highest scoring team this season" sits halfway between a Topic and a free answer. An open of the top Topic costs nothing but is often wrong: that question opened the playoff race. Brian chose the free answer, and it counts toward the cap of 25 a day.
2. The hit rate was 29 of 40 with no rule for the unsure band. With rule 1, it is about 35 of 40. The 3 judgment questions ("worst move all year", "most overated team?", "most underated team?") have no fixed answer and are not in the count.
3. What passed: the Topic pick when a Topic fits, 11 of 13, and each of the 5 real Topic questions. The honest miss, 4 of 4, each with 3 close Topics. The team named, 4 of 4 at 1.00, with "the fridge" and "t mac". Abuse and rule breaks, 2 of 2. "This season's data can answer" gave a clear yes on each free question and a clear no on each miss.
4. The state of the route must say that a Topic Answer covers only the latest week. Without it, "week 1 results" went to the week recap at 0.97.

What the prototype also showed, for the spec:
- "write me a poem about my kicker" got 0.39 on "about the league", in the unsure band. The spec sets the route for an unsure "about the league".
- The judgment questions got an unsure "this season's data can answer", from 0.35 to 0.68. The spec sets the route for that band.
- "who would trade me a WR1" got 0.63 on "a Topic fits". Under rule 1 it gets a free answer, with trade ideas as the Suggestion.
- Questions were answered on their own. The Choice and the Nouls share one request, and the request had about 2,200 input tokens.

The prototype code is deleted from the repo. A copy for the spec sits in the session scratchpad, outside the repo, with the question set and the exact payloads.
