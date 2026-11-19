# 10: How can the Finder find a three-team trade, and at what cost and speed?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

Brian wants a manager to ask the Finder for a three-team trade, for example "I want an RB, in a three-team trade". The analyzer already grades trades of three and four teams (`.scratch/analyzer-multi-team/PRD.md`). That spec put a three-team Finder out of scope, and the Finder hides once a trade has a third side. The Finder of decisions 01, 02, 05, and 09 finds only two-team trades.

Find out:

1. How the Finder steps (the Partner filter, the Spares tree of decision 05, the offer build, the Shortlist with its gain Noul per side, and the one pick call) change for three sides. Name each step that must change and how.
2. The shape of a three-team offer: a ring (A to B, B to C, C to A), or one hub side. Which shape fits the request shape of the multi-team analyzer (each given player names the roster he goes to).
3. How to keep the search small. With 11 other teams there are 55 pairs of partners. Find a cut that uses hard legal rules and Jev judgments only, never a math screen (`no-math-filters`).
4. The time and the cost of one press, measured against the two-team Finder of about 25 s (decision 02). Replay one press on the week 11 snapshot if it costs $0.50 or less. Otherwise estimate from the logs.
5. The days of build, and if it can ship before the Lock (00:00 Eastern Tue 2026-11-24) without risk to the event live on Fri 2026-11-20 night.

The findings go beside this ticket, at `10-research-three-team-finder.notes.md`. The league data stays out of the repo except player names that a Backtest mark already names.

## Decision
