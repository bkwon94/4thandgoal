# 07: Which sim model runs the rest of the season?

Map: `.scratch/midseason-report/MAP.md`.

**Kind:** research

**Blocked by:** 01

**Status:** done

## Question

`packages/rankings/python/src/rankings/odds.py` already runs playoff odds, with the head-to-head game and the median game. The sim chapter needs more: the odds of the title, of each seed, of the bye, and of each final record, plus the most likely final table. Find out: how `odds.py` draws a team score, which inputs it reads, and which more inputs help, such as `projections_ahead.json`, injuries, byes, and the bracket. Also find the cost of 10,000 runs per client, and what a run must store for a replay in the browser. Write the notes at `decisions/07-research-the-sim-model.notes.md`.

## Decision

The research decided it, and Brian gave the bracket fact on 2026-11-05. The notes are `decisions/07-research-the-sim-model.notes.md`.

- The sim keeps the draw of `odds.py`: a level per team shrunk to the league mean, a normal weekly score, and the pull toward the projected best lineup. It already reads the projections ahead, the byes, the rosters, and the injury return weeks.
- The sim adds the playoff bracket for weeks 15 to 17 and full counts: the title, each seed, the bye, and each final record. CPC reseeds after round 1, as Brian confirmed. NorCal has a fixed bracket.
- The projected totals extend past week 14 to the playoff weeks.
- The report runs 10,000 runs per client. A run takes under 1 second per client.
- No single final table is "most likely". The page orders the teams by mean final wins and shows a heat map of team against seed.
- The build stores a sample of about 200 runs and the model parameters, under 5 KB. So ticket 08 can choose a replay or a live sim in the browser.
