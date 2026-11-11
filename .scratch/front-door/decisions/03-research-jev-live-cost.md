# 03: What do the Jev questions cost live, and which limits apply?

Map: `.scratch/front-door/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

Find the cost and the latency of a Jev route and of the question "Can the facts of the week answer this?" for one question. Find the rate limits of TypeSafe for a live ask box. Find also the cost of one short Claude answer with a Jev check. Write the notes at `decisions/03-research-jev-live-cost.notes.md`. The spec needs the numbers to set the caps and to keep the Thread fast.

## Decision

The notes are `decisions/03-research-jev-live-cost.notes.md`. Brian decided the open items on 2026-11-09, in a grill.

1. The facts:
   - Jev 1.14 costs $0.042 per million input tokens, and output is free.
   - A route call costs about $0.00004, and a "facts can answer" call costs about $0.00075. Each takes under 1 s.
   - One short Claude answer costs about $0.04 to $0.10, and no run has timed one. Prototype 09 times it.
   - For 2 leagues of 24 managers, the cost is about $1 to $66 each month, by use. Claude is over 95% of it.
2. The TypeSafe limits of the organization are 80 requests per second and 100,000 tokens per second, from Brian. Both are far above our use.
3. Jev picks the slice. Each Topic has a fixed list of the fact groups it needs, and the API sends Claude only that slice. A Topic about another team gets the slice of that team. A question with no Topic gets the full fact sheet of the week. Reason: the route call already names the Topic, so a personal Answer costs about $0.04, not $0.10. The spec writes the table from Topic to fact groups.
4. A new ADR in the spec covers the text that managers type. It says what goes to TypeSafe and to Anthropic. It says that the log of misses lives on Fly, never in the repo, and how long the log stays. Reason: the change is hard to undo, and ADR 0029 covers only the pipeline. The spec sets the next free ADR number, because 0030 is taken on the `manager-brain` branch.
5. The wait of a live Answer goes to decision 11.
