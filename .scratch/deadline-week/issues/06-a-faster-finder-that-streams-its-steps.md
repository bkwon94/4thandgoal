# 06: A faster Finder that streams its steps

Spec: `.scratch/deadline-week/PRD.md`. Acceptance tests AT-41.

**App:** api

**What to build:** A press of the Finder takes about 25 s, not about 42 s. Each offer of the Shortlist gets a short label from A to J in the pick prompt, and code maps the label back to its offer, so the id retry goes away. The offer sheets build at the same time. The Jev waves pace by a count per second. The log-only Jev checks run after the answer goes out. One pick call picks the best 3 across all partners and writes a Lean and a Case of at most 3 lines for each, and the find route sends that read with each trade. The route streams one step line as each step ends, such as "Read 11 teams", "Found 18 players who fit", "Built 42 offers", "Made a shortlist of 9", and "Picked the best 3". The step lines name no internal tool. No prewarm of the cache.

**Blocked by:** none

**Status:** in-review

- [ ] Three real presses for Bo Girds (roster 6) and every team on the week 11 snapshot each end in 30 s or less, with one pick call and no id retry in the log.
- [x] A route test shows the step lines in order and the Lean and the Case sent with each trade.
- [x] Only Send it, Lean yes, and Gut call come back as trades.
