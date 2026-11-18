# 03: How live are the inputs of the What-if, and does a season-ending injury lower the level of a team?

Map: `.scratch/season-sim/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

The injuries reach the sim only through the projections. The level of a team comes from its season average, which holds the weeks a now-injured star played. The build reads the injuries once, on Tuesday.

Brian decides:

1. Does the API run the What-if on the Tuesday inputs, or refetch the injuries and the projections from Sleeper when a manager opens the page?
2. Does a season-ending injury of a starter also lower the level of the team, and by how much?

3. Does the API machine move from `shared-cpu-1x` to a size with a full CPU, or does the What-if run fewer runs? At the baseline quota of the shared CPU, one call can take 11 to 15 s.

Ticket 01 found that Sleeper blanks each week of an expected absence, so the projections already see a long injury. The level of the team still holds the weeks the star played.

## Input from 07

Decision 07 measured one call with the split and set results at 0.90 to 1.10 s on the Mac, at 6 weeks left. Fly is about 1.2 to 2.2 s, an estimate. Weigh this when you size the machine.

## Decision

Brian, 2026-11-18.

**1. The What-if runs on the Tuesday inputs.** The API uses the same injuries and projections as `sim.json`, and never refetches from Sleeper. So a What-if with no set result gives the numbers of the file, and only a set result moves the odds. The page and its text agree, as decision 02 asks. An injury from Wednesday to Sunday shows in the next Tuesday build.

**2. A season-ending injury does not change the level.** The projection carries the loss: Sleeper blanks each week of the absence, so the projected best-lineup total drops, and `PROJECTION_WEIGHT = 0.5` counts half of the gap. Example: a team that averages 120 loses a 20-point star to an 8-point bench player. Each week moves by about −6, and the level still holds the weeks the star played. A rule for the full gap or a lower level adds a Sleeper status test and a second rule, with 4 regular weeks left. If the odds of such a team look wrong after the release, open it as its own ticket.

**3. The API stays on `shared-cpu-1x`, 1 GB, at 10,000 runs.** Brian wants no extra cost, because this is a personal project. `performance-1x` costs $33.00 a month in `ewr`, against $6.70.

Why the shared machine is enough. A shared vCPU gets 5 ms of each 80 ms, 6.25 % of a core. Unused time builds a burst balance of up to 500 s, and the CPU runs at 100 % while it lasts. One call needs about 0.7 to 1.4 s of CPU. With an empty balance, it takes 11 to 22 s. An idle machine refills about 225 s of CPU an hour. A full balance covers 350 to 550 calls in a row, and a day of refill covers about 4,000 to 7,000 calls. The two leagues have about 24 managers. The one gap: a new machine starts with a 5 s balance. The Fly docs do not say if a deploy resets it.

**For the spec.**

- An acceptance test times real What-if calls on Fly, also just after a deploy. If they are slow, the spec decides then.
- The server stops the work of a call that the page cancelled. A new pick cancels the call before it, so fast taps otherwise burn CPU on answers that nobody reads.
