# 03: Where does the live feed of trades get its data?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

The event shows the trades of the league as Sleeper accepts them. The site is a static export, and transaction history comes from the weekly build. The spec must choose the data path and the refresh time.

Find out if the Sleeper transactions endpoint lets a browser read it across origins, and its rate limit. Compare a browser read with a read through the API on Fly, for cost and for load. Find which fields show a trade: the teams, the players, the time, and its status. Write the findings at `decisions/03-research-trade-feed-source.notes.md`.

## Decision

None yet.
