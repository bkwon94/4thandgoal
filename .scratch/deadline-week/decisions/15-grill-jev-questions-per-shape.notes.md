# 15 notes: a live probe of the fair question with chart facts in the state

Ticket: `15-grill-jev-questions-per-shape.md`. Rulings: decision 14 and Brian's rulings of 2026-11-19.
Worktree: `.claude/worktrees/deadline-week`, branch `deadline-week`, head `7637759e`. Probe run on 2026-11-19.
These notes give facts only. Brian picks.

## Summary

- 54 offers of Bo Girds (roster 6) on the live CPC snapshot of week 11. Two wordings of `fair` went in the same request, over the same state.
- Spares tree offers and Backtest marks 1 and 2: both wordings give a clear no to all 10. The largest answer is 0.18.
- Value offers: A gives 9 yes, 21 unsure, 4 no. B gives 17 yes, 12 unsure, 5 no.
- Offers just outside the screen: A gives 1 yes, 4 unsure, 5 no. B gives 1 yes, 2 unsure, 7 no.
- A and B agree on the word (yes, unsure, no) for 39 of 54 offers (72%).
- Both wordings read the direction of a trade. When Bo Girds gets more players, Value offers read as fair (B mean 0.78). When Bo Girds gives more players, the same screen reads as less fair (B mean 0.46).
- Spend: 11 requests, 49,310 input tokens, $0.0021.

## Method

- Snapshot: the live CPC snapshot, built through `_live_snapshot` (`apps/pipeline/src/cornerstone/cli.py:264-273`). The script printed `week 11 chart values 126`. The chart reader raised if called. No Claude call ran.
- Asker: Bo Girds, roster 6. Tradeable players: `in_pool` and a week 11 chart value, as in decision 13.
- Value screen, as decision 14 states it:
  - Shapes 1-for-1, 2-for-1, 1-for-2, 3-for-1, 1-for-3, 3-for-2, 2-for-3. "2-for-1" means Bo Girds gives 2 and gets 1.
  - Uneven shapes: the sum of the side that gets more players is 100% to 125% of the other sum.
  - 1-for-1: the larger sum is at most 110% of the smaller sum. This reads "within 10% either way" as a ratio.
  - Each player on a side of 2 or 3 has at least 5 chart points.
  - The handcuff rule of `build_offers` did not run. Decision 13 found that it dropped 0 candidates.
- Sources:
  - `value`: 34 offers that pass the screen. 5 per shape, 4 for 2-for-3, each from a different partner where possible. Seed 15.
  - `outside`: 10 offers with a ratio of 130% to 160%, in the same direction as the screen. 2 per shape for 1-for-1, 2-for-1, 1-for-2, 3-for-2, and 2-for-3. The floor still applies.
  - `spares`: 8 Spares tree offers from `preview-api.log` lines 154 to 219 (the press of line 153). Each player is still on the same roster. 7 have chart values for every player. 1 holds Justin Herbert, who has no chart value.
  - `mark1` and `mark2`: Backtest marks 1 and 2 of `.scratch/deadline-week/backtest-marks.json`.
- Requests: one per partner, 11 in all, each 3,202 to 6,149 tokens. Client `TypeSafeJev` (`packages/league/python/src/league/jev.py`), model `jev-latest`. Every answer came from `jev-1.14.0`.
- Words: `yes` above 0.7, `no` below 0.3, `unsure` between. These are `YES_AT` and `NO_AT` of `trade_jev.py`.

### The state

The state of each request is today's pair state, `_pair_state` (`finder_search.py:148-149`), with two changes:

1. Each player line under `teams.asker.players` and `teams.partner.players` gets `chart_value`. A player with no chart value has `null`.
2. A new key `offers.<n>` per offer holds `sides`. Each side has `team`, `gives`, and `chart_sum`. Each player in `gives` has `name`, `position`, `nfl_team`, `season_rank`, `status`, and `chart_value`.

The state holds no gap, no ratio, and no lineup points. It holds team names and player names, and no manager names.

Example, `offers.2` of the request with Lil Fridge (roster 3):

```json
{"sides": [
  {"team": "Bo Girds", "gives": [
    {"name": "Trey McBride", "position": "TE", "nfl_team": "ARI", "season_rank": "TE1", "status": null, "chart_value": 18.5},
    {"name": "Parker Washington", "position": "WR", "nfl_team": "JAX", "season_rank": "WR10", "status": null, "chart_value": 28.5},
    {"name": "Zay Flowers", "position": "WR", "nfl_team": "BAL", "season_rank": "WR12", "status": null, "chart_value": 23.0}],
   "chart_sum": 70.0},
  {"team": "Lil Fridge", "gives": [
    {"name": "Christian McCaffrey", "position": "RB", "nfl_team": "SF", "season_rank": "RB2", "status": null, "chart_value": 64.0}],
   "chart_sum": 64.0}]}
```

### Wording A: today's `FAIR`, unchanged

`{gives}` uses the same words as `trade_jev_questions` (`trade_jev.py`).

- Text: `Is this trade close to fair for both teams: {gives}?`
- Yes: `Each team gives about as much as it gets, by points, rank, and trade value.`
- No: `One team gives clearly more than it gets.`

Example text: `Is this trade close to fair for both teams: Bo Girds gives Trey McBride, Parker Washington, and Zay Flowers and Lil Fridge gives Christian McCaffrey?`

### Wording B: the chart facts by their state path

- Text: ``Is the trade in `offers.{n}` close to fair by chart value: {gives}?``
- Yes: ``Each team gives about as much chart value as it gets, by the sums in `offers.{n}.sides`.``
- No: ``One team gives a clearly larger chart sum in `offers.{n}.sides` than it gets back.``

Neither wording names the consolidation premium of decision 14. B asks only whether the sums are close.

## Counts per wording and per source

| Source | Offers | A yes | A unsure | A no | A mean | B yes | B unsure | B no | B mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| value | 34 | 9 | 21 | 4 | 0.58 | 17 | 12 | 5 | 0.65 |
| outside | 10 | 1 | 4 | 5 | 0.38 | 1 | 2 | 7 | 0.29 |
| spares | 8 | 0 | 0 | 8 | 0.08 | 0 | 0 | 8 | 0.05 |
| mark1 | 1 | 0 | 0 | 1 | 0.08 | 0 | 0 | 1 | 0.04 |
| mark2 | 1 | 0 | 0 | 1 | 0.15 | 0 | 0 | 1 | 0.07 |

### Value and outside offers by direction

| Source | Direction | Offers | A yes / unsure / no | A mean | B yes / unsure / no | B mean |
| --- | --- | --- | --- | --- | --- | --- |
| value | 1-for-1 | 5 | 4 / 0 / 1 | 0.71 | 4 / 1 / 0 | 0.85 |
| value | Bo Girds gets more players (1-for-2, 1-for-3, 2-for-3) | 14 | 5 / 9 / 0 | 0.68 | 11 / 3 / 0 | 0.78 |
| value | Bo Girds gives more players (2-for-1, 3-for-1, 3-for-2) | 15 | 0 / 12 / 3 | 0.45 | 2 / 8 / 5 | 0.46 |
| outside | 1-for-1 | 2 | 0 / 1 / 1 | 0.28 | 0 / 1 / 1 | 0.26 |
| outside | Bo Girds gets more players | 4 | 1 / 3 / 0 | 0.59 | 1 / 1 / 2 | 0.46 |
| outside | Bo Girds gives more players | 4 | 0 / 0 / 4 | 0.22 | 0 / 0 / 4 | 0.14 |

### Value offers by shape

| Shape | Offers | A yes / unsure / no | B yes / unsure / no |
| --- | --- | --- | --- |
| 1-for-1 | 5 | 4 / 0 / 1 | 4 / 1 / 0 |
| 1-for-2 | 5 | 1 / 4 / 0 | 2 / 3 / 0 |
| 1-for-3 | 5 | 1 / 4 / 0 | 5 / 0 / 0 |
| 2-for-3 | 4 | 3 / 1 / 0 | 4 / 0 / 0 |
| 2-for-1 | 5 | 0 / 3 / 2 | 2 / 0 / 3 |
| 3-for-1 | 5 | 0 / 4 / 1 | 0 / 4 / 1 |
| 3-for-2 | 5 | 0 / 5 / 0 | 0 / 4 / 1 |

The screen rule is the same in both directions: the team that gets more players gets the larger sum. Jev still reads the two directions differently. In the 1-for-3 rows, Bo Girds gets 109% to 117% and B gives 5 yes. In the 3-for-1 rows, Bo Girds gives 108% to 124% and B gives no yes. The probe does not show the cause. Two possible causes are the order of the sides (Bo Girds is always first) and a lean toward the asker. A probe with the sides swapped can test the first.

### Clear no on Value offers (a drop in step 1)

| Offer | Sums | A | B |
| --- | --- | --- | --- |
| Trey McBride for Emeka Egbuka (Puka Deez...) | 18.5 / 17.0 | 0.29 | 0.61 |
| Blake Corum and Trey McBride for Chase Brown (NFC Least) | 35.5 / 29.5 | 0.24 | 0.18 |
| Trey McBride and Kenneth Walker III for Jahmyr Gibbs (Maye d'force B with U) | 81.0 / 68.0 | 0.29 | 0.18 |
| Blake Corum, Trey McBride, and Zay Flowers for Chuba Hubbard (Puka Deez...) | 58.5 / 49.0 | 0.29 | 0.30 |
| Matthew Golden and Kyren Williams for Amon-Ra St. Brown (Teehee) | 67.5 / 54.0 | 0.32 | 0.21 |
| Blake Corum, Matthew Golden, and Kyren Williams for Jahmyr Gibbs (Maye d'force B with U) | 84.5 / 68.0 | 0.33 | 0.18 |
| Trey McBride, Parker Washington, and Zay Flowers for Christian Watson and Brock Purdy (The Blue Tent) | 70.0 / 60.0 | 0.42 | 0.28 |

The first sum is what Bo Girds gives. A drops 4 Value offers. B drops 5. Both drop 2 of the same offers. All but the first are offers where Bo Girds gives more players.

## Backtest marks 1 and 2

Both marks expect `drop`. Both wordings give a clear no.

| Mark | Offer | State facts | A | B |
| --- | --- | --- | --- | --- |
| 1 | Bo Girds gives Kenneth Walker III, To Infinity and Bijan gives Patrick Mahomes | Walker RB, KC, RB3, Questionable, chart 62.5. Mahomes QB, KC, QB9, chart 9.5. | 0.08 | 0.04 |
| 2 | Bo Girds gives Zay Flowers, To Infinity and Bijan gives Jared Goff | Flowers WR, BAL, WR12, chart 23.0. Goff QB, DET, QB12, chart 9.0. | 0.15 | 0.07 |

In decision 13, the state held no chart value and the fair question gave no "yes" to 41 offers inside the 10% band. With chart values in the state, A now gives 9 yes and B gives 17 yes on 34 Value offers.

## Agreement and disagreement

A and B give the same word for 39 of 54 offers (72%). Of the 15 disagreements, 13 are in `value` and 2 are in `outside`. B is the higher answer in 10 of the 15.

Five disagreements, with the state facts:

1. **Trey McBride for Emeka Egbuka, 1-for-1, Puka Deez...** McBride TE, ARI, TE1, chart 18.5. Egbuka WR, TB, WR46, chart 17.0. Sums 18.5 and 17.0. A 0.29 (no), B 0.61 (unsure). The sums are close, but the Season ranks are far apart. A's yes names "rank".
2. **Trey McBride for Ryan Flournoy and Harold Fannin Jr., 1-for-2, To Infinity and Bijan.** McBride TE1, chart 18.5. Flournoy WR, DAL, WR26, chart 8.5. Fannin TE, CLE, TE5, chart 11.5. Sums 18.5 and 20.0. A 0.54 (unsure), B 0.82 (yes).
3. **Parker Washington and Zay Flowers for Bucky Irving, 2-for-1, The Blue Tent.** Washington WR, JAX, WR10, chart 28.5. Flowers WR, BAL, WR12, chart 23.0. Irving RB, TB, RB10, chart 48.5. Sums 51.5 and 48.5. A 0.61 (unsure), B 0.76 (yes).
4. **Matthew Golden and Kyren Williams for Amon-Ra St. Brown, 2-for-1, Teehee.** Golden WR, GB, WR6, chart 40.5. Williams RB, LAR, RB11, chart 27.0. St. Brown WR, DET, WR5, chart 54.0. Sums 67.5 and 54.0, a ratio of 1.25 at the edge of the screen. A 0.32 (unsure), B 0.21 (no).
5. **Blake Corum and Trey McBride for Quinshon Judkins, Deebo Samuel Sr., and Nico Collins, 2-for-3, behold the lamb. Outside.** Corum RB, LAR, RB17, chart 17.0. McBride TE1, chart 18.5. Judkins RB, CLE, RB21, chart 13.5. Samuel WR, SF, WR29, chart 11.5. Collins WR, HOU, WR15, chart 29.0. Sums 35.5 and 54.0, a ratio of 1.52. A 0.59 (unsure), B 0.26 (no).

## Spend

- Jev: 11 requests, 49,310 input tokens, at $0.042 per million input tokens: $0.0021. Output tokens are free.
- Claude: none.
- The budget was $0.05.

## Files

The scripts and payloads are in the scratchpad of the session `3dbfc16b-eee4-42b7-bf32-73ec67e52312`. A reboot can clear it.

- `build_probe.py` builds the offers and writes `payloads.json` (one state and its questions per partner) and `cases.json`.
- `send_probe.py` sends each payload with `TypeSafeJev` and writes `responses.json`.
- `analyze.py` joins them into `results.json` and prints the counts.

A rerun of `send_probe.py` sends the exact same payloads. A rerun of `build_probe.py` reads the live rosters again, so its offers can change.

## What this means for decision 15

These are options, with no pick.

1. **Keep A and add the chart facts to the state.** A rises from no "yes" in decision 13 to 9 of 34 yes, with 4 drops. It still reads Season rank, so a close chart sum with far ranks can drop (case 1).
2. **Use B.** B gives more yes on Value offers (17 of 34) and more no just outside the screen (7 of 10). It drops 5 Value offers, 4 of them where Bo Girds gives more players.
3. **Either wording drops every Spares tree offer of today and both marks.** Under the step 1 rule, all 8 Spares tree offers and both marks drop. In these offers, one side has 2.6 to 10.8 times the chart sum of the other. One offer holds Justin Herbert, who has no chart value. This matches the marks. It also means step 1 removes the need-first offers of today.
4. **Settle the direction first.** Both wordings read 2-for-1, 3-for-1, and 3-for-2 as less fair than the mirror shapes. Options:
   - Ask the consolidation premium as its own question, as item 2 of the ticket asks.
   - Probe again with the sides of each offer in the other order, to test whether the order causes it.
   - Accept it. A clear-no drop at 0.3 then removes about 3 to 5 of 15 offers where the asker gives more players.
5. **Keep step 1 at a clear no only.** Most Value offers land between 0.3 and 0.7 under A (21 of 34). An "unsure" passes step 1, so A and B drop about the same count of Value offers (4 and 5).

## Side order re-run

Brian chose wording B. This re-run tests whether the side order causes the direction finding. It ran only wording B.

### Method

- The same 54 offers and the same state as `payloads.json`. `swap_probe.py` writes `payloads_swapped.json`.
- Two changes only:
  1. In each `offers.<n>.sides`, the partner side is first and the Bo Girds side is second.
  2. In the question text, the trade words name the partner first. Example: ``Is the trade in `offers.2` close to fair by chart value: Lil Fridge gives Christian McCaffrey and Bo Girds gives Trey McBride, Parker Washington, and Zay Flowers?``
- The subject of B is ``the trade in `offers.{n}` ``. It names no side order, so it stays the same. The yes and no texts stay the same.
- `teams.asker` and `teams.partner` stay as before. They are not part of `offers.<n>.sides`.
- Same client and same per-partner grouping: `send_swapped.py` writes `responses_swapped.json`. `analyze_swapped.py` writes `results_swapped.json`.

### Means and words by direction

"First" is the first run, with Bo Girds first. "Swapped" is this run, with the partner first.

| Source | Direction | Offers | First: yes / unsure / no | First mean | Swapped: yes / unsure / no | Swapped mean |
| --- | --- | --- | --- | --- | --- | --- |
| value | 1-for-1 | 5 | 4 / 1 / 0 | 0.85 | 5 / 0 / 0 | 0.88 |
| value | Bo Girds gets more players | 14 | 11 / 3 / 0 | 0.78 | 7 / 7 / 0 | 0.63 |
| value | Bo Girds gives more players | 15 | 2 / 8 / 5 | 0.46 | 5 / 8 / 2 | 0.57 |
| outside | 1-for-1 | 2 | 0 / 1 / 1 | 0.26 | 0 / 1 / 1 | 0.21 |
| outside | Bo Girds gets more players | 4 | 1 / 1 / 2 | 0.46 | 0 / 0 / 4 | 0.17 |
| outside | Bo Girds gives more players | 4 | 0 / 0 / 4 | 0.14 | 0 / 0 / 4 | 0.21 |

The gap shrinks. It does not flip. On Value offers, it goes from 0.78 against 0.46 (a gap of 0.32) to 0.63 against 0.57 (a gap of 0.06). The order of the sides causes most of the gap.

### Clear-no drops per group

| Source | Direction | First order | Swapped order |
| --- | --- | --- | --- |
| value | 1-for-1 | 0 | 0 |
| value | Bo Girds gets more players | 0 | 0 |
| value | Bo Girds gives more players | 5 | 2 |
| outside | 1-for-1 | 1 | 1 |
| outside | Bo Girds gets more players | 2 | 4 |
| outside | Bo Girds gives more players | 4 | 4 |
| spares | all | 8 of 8 | 8 of 8 |
| marks | 1 and 2 | 2 of 2 | 2 of 2 |

Two Value offers drop in both orders: Trey McBride and Kenneth Walker III for Jahmyr Gibbs (0.18 and 0.18), and Matthew Golden and Kyren Williams for Amon-Ra St. Brown (0.21 and 0.28).
Backtest marks: mark 1 is 0.04 first and 0.05 swapped. Mark 2 is 0.07 first and 0.10 swapped.

### Per offer

- The word is the same in both orders for 39 of 54 offers (72%). The mean absolute change is 0.11.
- The largest changes:
  - Trey McBride, Kyren Williams, and Zay Flowers for Quinshon Judkins and Javonte Williams (3-for-2, 68.5 / 58.5): 0.33 first, 0.73 swapped.
  - Zay Flowers for Emmett Johnson and Jonah Coleman (outside 1-for-2, 23.0 / 36.5): 0.65 first, 0.16 swapped.
  - Parker Washington for Jayden Daniels and Nico Collins (outside 1-for-2, 28.5 / 37.5): 0.72 first, 0.24 swapped.
  - Blake Corum and Zay Flowers for Germie Bernard, Deebo Samuel Sr., and Drake London (2-for-3, 40.0 / 46.0): 0.80 first, 0.46 swapped.
- The pattern: in each order, an offer reads as more fair when the team named first gets the larger chart sum. With Bo Girds first, the offers where Bo Girds gets more players read best. With the partner first, the mirror offers gain and those offers fall.

### Spend

- Jev: 11 requests, 44,704 input tokens, $0.0019.
- Both runs together: 94,014 input tokens, $0.0039.

### What this means for decision 15

These are options, with no pick.

1. **Fix one side order in code.** For example, always name the team that gets more players first, or always name the asker first. The answer then has a known lean in one direction.
2. **Ask B in both orders and combine the two answers in code**, for example with the mean or the minimum. This doubles the question count of step 1. Questions are cheap, and the state is paid once per request.
3. **Accept the order effect.** With the asker first, step 1 drops 5 of 15 Value offers where the asker gives more players and none of the others.
