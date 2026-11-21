# 06: Which issues of the trade tools does the polish fix?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

The polish has a fixed list, not an open end. Brian walks each trade tool of CPC on the phone: the analyzer, the trade ideas, the sell high Topic, and the trade check. He names each issue. Decide which issues the spec fixes and which wait.

## Decision

Brian walked the trade tools on the phone on 2026-11-18 and found two issues. "Other than that overall solid." The polish list is these two items, and no more.

1. **A slow first call, then a fast retry.** A trade Topic sometimes fails on the first call, and a retry answers fast. The cause is not found yet:
   - A Fly machine always runs (`min_machines_running = 1`), so it is not a cold start.
   - The site has no timeout, and any failed stream shows the retry line.
   - The retry is fast because the API keeps a cached Answer.
   - Decision 02 measured a press of about 42 s, with 18 to 21 s from the Advisor id retry bug. A long stream that drops is the likely cause.

   The spec finds and fixes the cause. Each failed stream gets one log line with its cause and its time, so the next failure shows its cause.
2. **Bad trade ideas.** The front door already runs the Finder, whatever the `finder` flag says. Brian saw "Kenneth Walker for Mahomes" and, as the best one, "Zay Flowers for Goff". The Fly log of one run of roster 6 at 02:51 UTC on 2026-11-19 shows the cause upstream of the Advisor:
   - The target step marked Mahomes and Goff as players that roster 6 wants. The need of roster 6 read 0.9.
   - So code built only QB trades. Every offer of the Shortlist had `fair` from 0.29 to 0.39.
   - The Advisor picked the least bad one. Walker for Mahomes is most likely a near idea, which the page shows with a "Why not" line. Decision 04 already hides the trades that the Advisor would not send.

   The spec fixes the trade ideas. The two trades are the first two Backtest marks. Research ticket 09 replays the press and traces why the target step wants QBs. If the cause is the target question, its split moves back into this spec from OUT OF SCOPE.
