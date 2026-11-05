# 01 notes: what Sleeper gives for the season data

Summary: Sleeper gives every draft pick with its roster, the CPC auction price, and every won and lost FAAB claim with its bid. Neither league has a keeper or a traded pick, and no source gives an injury date: the best resolution is the NFL week.

Calls ran on 2026-11-05 against `https://api.sleeper.app/v1`. CPC is `1386167364424318976`, draft `1386167364436901888`. NorCal is `1402948824305049600`, draft `1402948826377031680`. Docs: https://docs.sleeper.com ("Get a specific draft", "Get all picks in a draft", "Get transactions").

## 1. Draft picks

Each league has one draft, `status: complete`, for season 2026 (`/league/{id}/drafts`).

- CPC: `type: auction`, `settings.budget: 200`, 12 teams, 168 picks, 14 picks per roster.
- NorCal: `type: snake`, `settings.rounds: 15`, 12 teams, 180 picks, 15 picks per roster.

The fields of a pick (`/draft/{id}/picks`) are `draft_id`, `draft_slot`, `is_keeper`, `metadata`, `pick_no`, `picked_by`, `player_id`, `reactions`, `roster_id`, `round`.
The `metadata` holds `player_id`, `first_name`, `last_name`, `position`, `team`, `number`, `years_exp`, `status`, `injury_status`, `news_updated`, `sport`, `team_abbr`, `team_changed_at`.
CPC picks also carry `metadata.amount` (the price, a string) and `metadata.slot`. NorCal picks have no `amount`.

Keepers: `is_keeper` is `null` on all 348 picks. Each league has 0 keepers. Both leagues have `settings.type: 0` (redraft) and `max_keepers: 1`, the Sleeper default (`/league/{id}`).

Map to a roster: each pick carries `roster_id` directly. The draft also carries `draft_order` (user id to slot) and `slot_to_roster_id` (slot to roster id). For all picks, `picked_by` equals the `owner_id` of the pick's `roster_id` in `/league/{id}/rosters`, and each roster has one `draft_slot`.

- In the CPC auction, `roster_id` is the buyer, and `pick_no` is the order of the sale. `round` is only `ceil(pick_no / 12)`, so it means nothing in an auction.
- The CPC spend per roster is 191 to 200 of the 200 budget. Roster 12 spent 191, the lowest.
- The auction does not record who nominated each player. The draft `metadata.nominating_slot` holds only the last nomination.

Example, CPC: `pick_no 1, draft_slot 10, roster_id 10, player_id 4866, RB, amount "58"`. NorCal: `pick_no 1, round 1, draft_slot 1, roster_id 10, player_id 9221, RB`.

## 2. Traded draft picks

A trade row carries `draft_picks` and `waiver_budget` (Sleeper docs, "Get transactions"). In weeks 1 to 8, CPC has 20 trades and NorCal has 2. Each has `draft_picks: []` and `waiver_budget: []`.
`/league/{id}/traded_picks` and `/draft/{id}/traded_picks` return `[]` for both leagues. Both leagues have `settings.pick_trading: 0`.

Traded picks do not matter for the 2026 draft. The draft was before any trade, and no trade includes a pick or FAAB.

Example, CPC leg 6: `roster_ids [7, 8]`, 7 players each way, `draft_picks: []`, `settings: {is_counter: 1}`.

## 3. FAAB

Both leagues have `waiver_type: 2` (FAAB), `waiver_budget: 100`, `waiver_bid_min: 0` (`/league/{id}`).
`/league/{id}/transactions/{week}` exists for each week, and the rows carry `leg` (the week). Counts from the live API, weeks 1 to 8:

| League | waiver complete | waiver failed | lost to another bid | free_agent | trade |
| --- | --- | --- | --- | --- | --- |
| CPC | 110 | 135 | 108 | 209 | 20 |
| NorCal | 51 | 55 | 45 | 125 | 2 |

- Each of the 351 `waiver` rows carries `settings.waiver_bid` and `settings.seq`. A few carry `settings.priority`.
- No `free_agent` row carries a bid: `settings` is `null` on all 334 rows.
- A failed row gives its cause in `metadata.notes`. The causes are "This player was claimed by another owner.", "Unfortunately, your roster will have too many players after this transaction.", and once "One of the players you are trying to drop has already started playing."
- The data shows who bid on a player and lost. Match a failed "claimed by another owner" row to the complete row that adds the same player. Each of the 153 matched winners bid at least as much as the loser.
- Match on `status_updated` (the time of the waiver run), not on `leg`. In five NorCal pairs the two rows have a different `leg` but the same `status_updated`: legs 1 and 2, and legs 8 and 7.
- A claim that a manager cancels before the run leaves no row.
- The sum of complete bids agrees with `settings.waiver_budget_used` of `/league/{id}/rosters`: CPC 751 now, and 692 in the week 8 raw `rosters.json`.

Example, CPC leg 3: roster 1 bid 36 on player 12495 and lost. Roster 11 won the player with a bid of 40.

The repo fetch: `fetch_week` saves `transactions.json` of week N and `transactions_prev.json` of week N-1 (`packages/league/python/src/league/provider/sleeper.py`, lines 213 to 241). `save_week_to_history` copies the week N file into `history/week-NN/` (`packages/league/python/src/league/history.py`, line 340).
The week N build runs before the waiver run, so the history copy misses the late rows. `load_saved_weeks` swaps in the fresh `transactions_prev.json` of week N+1 (`history.py`, `_fresh_transactions`).

| CPC week | API rows | `history/week-NN` | `week-(N+1)/raw/transactions_prev.json` |
| --- | --- | --- | --- |
| 6 | 83 | 44 | 83 |
| 7 | 59 | 32 | 59 |
| 8 | 42 | 15 | none yet |

NorCal history weeks 1 to 8 equal the API, because a backfill wrote them. The report must read the fresh copy, or fetch each week again, or it loses the late claims.

## 4. Injuries

`history/week-NN/injuries.json` maps a Sleeper player id to the Sleeper `injury_status`, such as `Questionable`, `Out`, or `IR`. `_save_injuries` builds it at the build of week N (`history.py`, line 365):

- It reads `injury_status` from `players.json`, the current Sleeper player file. So the status is the status at build time, not on game day.
- It covers only players on a roster in that week's `matchups.json`.
- It exists only for CPC weeks 6 to 8 and NorCal week 8. The backfill writes no injury file.
- `players.json` has `injury_start_date` and `injury_notes`, but both are `null` for all 892 players with a status. `news_updated` is the time of the last news item, not of the injury.

A better source is in the repo: the nflverse injury report, `data/nfl/cache/nflverse/injuries_2026.csv.gz`, from `INJURIES_URL` in `packages/league/python/src/league/nflverse.py`.

- It has one row per player per NFL week, weeks 1 to 9 now, for every NFL player, keyed by `gsis_id`. `read_injuries` gives `{gsis_id: {week: report_status}}`.
- `report_status` is `Questionable`, `Doubtful`, or `Out`. It has no `IR` and no date column. It also has the body part (`report_primary_injury`) and the practice status.
- `read_injury_plays` reads the play by play for the first play of a week where a player "was injured during the play", with quarter and clock (`nflverse.py`, line 163).
- The weekly Sleeper stats show a missed game: `gp` is absent.
- Sleeper `players.json` holds `gsis_id` for 3,893 players. The repo joins with the ffverse id map instead.

How close: a trade has a time to the millisecond (`status_updated`). An injury has only an NFL week, plus a game play if it happened in a game. So the report can say "injured the week after the trade", or "hurt in the first game after the trade". It cannot place an injury by day.

Example, CPC: the trade of leg 4 (Sat 2026-10-03) sent player 2449, WR, to roster 3. nflverse lists him `Out` in week 5, the next week. He has a stat line in week 4 with `gp: 1` and none in week 5.

## Gaps

- An injury date. No source gives one. `injury_start_date` is always `null`, and nflverse gives a week only.
- IR status by week. nflverse has no `IR`. Sleeper `IR` exists only in the build-time snapshots from week 6 (CPC) and week 8 (NorCal).
- The injury status of a player who was not on a roster. `injuries.json` skips him. nflverse covers him.
- The nominator of each auction lot. The picks do not carry it.
- A claim cancelled before the waiver run. Sleeper keeps no row.
- Keepers and traded picks. Both are 0 in 2026, so the report needs no rule for them.

## Fetch work for the spec

1. `GET /league/{id}` gives `draft_id`. `league.json` holds it now.
2. `GET /draft/{draft_id}`: save `type`, `settings.budget`, `settings.rounds`, `settings.teams`, `slot_to_roster_id`, and `draft_order`.
3. `GET /draft/{draft_id}/picks`: save `pick_no`, `round`, `draft_slot`, `roster_id`, `player_id`, `metadata.position`, `metadata.team`, and `metadata.amount` for an auction.
4. `GET /league/{id}/transactions/{week}` for weeks 1 to N at report build time. Or read `history/week-NN/transactions.json` with the fresh `transactions_prev.json` swap, and fetch week N again.
5. From each `waiver` row, read `status`, `settings.waiver_bid`, `settings.seq`, `adds`, `drops`, `roster_ids`, `leg`, `status_updated`, and `metadata.notes`.
6. From each `trade` row, read `adds`, `drops`, `roster_ids`, `leg`, and `status_updated`. Keep `draft_picks` and `waiver_budget`, even though both are empty in 2026.
7. Read the nflverse `injuries_2026.csv.gz` for every week 1 to N, not only week N-1 as `load_slow_sources` does. Read the play by play injury plays for each week too.
8. `GET /league/{id}/rosters`: `settings.waiver_budget_used` gives a check of the FAAB spend per roster.
