# 02: Where does the Finder spend its time?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

A search of every team takes too long, by Brian's test. The spec must choose: make it fast enough, or stream each partner's result as it finishes, or both.

Time each step of a search of every team on the CPC week 11 data: the Partner filter, the targets, the offers, the Shortlist, and the Advisor pick. Find the cuts that keep the judgment of each step, such as more parallel Jev calls or one Advisor call per partner. Find whether the find route of the API can stream, as the front door stream does. Write the findings at `decisions/02-research-finder-speed.notes.md`.

## Decision

Brian agreed on 2026-11-18. The findings are in `decisions/02-research-finder-speed.notes.md`.

A press takes about 42 s now. The id retry of the pick call adds 17 to 21 s to it. With the id fix, a press takes about 22 to 26 s, and the free cuts take off 2 to 3 s more. Decisions 01 and 04 add some time back, so the estimate is about 25 s.

The spec does these four things:

1. It makes the four free cuts:
   - Each offer gets a short label, `A` to `J`, and code maps it back to its offer id. The id retry goes away.
   - The offer sheets build at the same time.
   - The Jev waves pace by a count per second, not by a fixed 1 s wait.
   - The log-only Jev checks run after the answer goes out.
2. One pick call stays, so the Advisor picks the best 3 across all partners, in one voice.
3. The progress streams, not the results. The analyzer page reads the same stream as the front door, with one step line as each step ends. Prototype 07 designs how the wait looks.
4. No prewarm of the result cache, because each roster change costs $0.85 to $1.70 more.

Out: a stream of results per partner. It shows the first trade at about 13 s, but it loses the one pick across partners and costs about a day more. Out: a lower effort for the pick, because it gave no pick.
