# 01: What does Sleeper give for the season data of the report?

Map: `.scratch/midseason-report/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

The report needs data that the pipeline does not fetch yet. The stage 1 grill found these facts:

- The pipeline fetches no draft picks. `league.json` holds the `draft_id`, and Sleeper has `/draft/{id}` and `/draft/{id}/picks`.
- CPC ran an auction: $200 budget, 12 teams, 168 picks, with `metadata.amount` on each pick. NorCal ran a snake: 15 rounds, 12 teams, 180 picks.
- The `waiver` rows of `transactions.json` carry `settings.waiver_bid`. The `free_agent` rows carry no bid.
- `history/week-NN/injuries.json` holds the injury status of each week.

Find out, for both leagues: the fields of a pick, the keeper flag if any, a trade of a draft pick, the FAAB bid on each won and failed claim for weeks 1 to 8, and how close to a trade date the injury data can place an injury. Write the notes at `decisions/01-research-sleeper-season-data.notes.md`.

## Decision

None yet.
