# 01: What does Sleeper give for the season data of the report?

Map: `.scratch/midseason-report/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The report needs data that the pipeline does not fetch yet. The stage 1 grill found these facts:

- The pipeline fetches no draft picks. `league.json` holds the `draft_id`, and Sleeper has `/draft/{id}` and `/draft/{id}/picks`.
- CPC ran an auction: $200 budget, 12 teams, 168 picks, with `metadata.amount` on each pick. NorCal ran a snake: 15 rounds, 12 teams, 180 picks.
- The `waiver` rows of `transactions.json` carry `settings.waiver_bid`. The `free_agent` rows carry no bid.
- `history/week-NN/injuries.json` holds the injury status of each week.

Find out, for both leagues: the fields of a pick, the keeper flag if any, a trade of a draft pick, the FAAB bid on each won and failed claim for weeks 1 to 8, and how close to a trade date the injury data can place an injury. Write the notes at `decisions/01-research-sleeper-season-data.notes.md`.

## Decision

Sleeper gives all the data of the report except an injury date. The notes are `decisions/01-research-sleeper-season-data.notes.md`. Decided by the research, checked by the orchestrator against the live API.

- Draft: each pick carries `roster_id`. The CPC auction price is `metadata.amount`, and `round` has no meaning there. Neither league has keepers. No 2026 trade moved a draft pick.
- FAAB: each `waiver` row carries `settings.waiver_bid`. CPC has 110 won and 135 failed claims in weeks 1 to 8, and NorCal has 51 won and 55 failed. A lost bid pairs with the winning claim on `status_updated`, so the report can name who bid and lost.
- The stored history is incomplete. For example, CPC week 8 holds 15 of 42 rows. So the report fetches `/league/{id}/transactions/{week}` again for each week.
- Injuries: the report reads the nflverse weekly injury status, not `injuries.json`. The finest step is the NFL week, so "hurt right after the trade" means "out in the first week after the trade".
