# 09 notes: why the target step of the Finder wants QBs for roster 6

Ticket: `09-research-qb-targets.md`. Map: `../MAP.md`. Frame of a fix: `05-grill-jev-trees-and-backtest.md`.
Worktree: `.claude/worktrees/deadline-week`, branch `deadline-week`. Each source is a file of this repo, read on 2026-11-18.
Each line number is the line in that file now. Each team is its roster id. The notes name no manager and no team name.

## Summary

- **The QB slot of roster 6 is weak by the code rule, and the rule is right by its own terms.** A one-player slot is weak past rank `team_count` x 1 = 12. Rodgers projects QB19, so "QB: Aaron Rodgers (QB19)" is a weak slot. Goff and Mahomes are an upgrade, but a small one: about +3.0 and +2.6 points a week.
- **Jev wanting Goff or Mahomes is not the error.** With the points in the state, Jev says Goff would start over Rodgers (0.67). A person says the same.
- **The error is the give side.** No question in the chain asks what roster 6 loses. "Zay Flowers for Goff" drops the lineup of roster 6 from 110.0 to 103.8 points a week. The Shortlist still ranks it high, because `need.6` and `need.7` are about 0.86 and the low `fair` only scales the product.
- **The target question under-rates every player of roster 7, not only the QBs.** The "or" question gives 0.35 to 0.51 to players who would start, such as Nabers. The QBs sit at the top of a flat, low list, so a small change in the live state moved them over `TARGET_AT` 0.6 and left the others under it. That is why the live run gave only QBs.
- **Recommendation, for Brian to decide:** fix the give side first, with the Spares rule of decision 05 on the targets of the asker and a "gain" question with a lineup-points fact. Then split the target question with points in the state, to get more than QBs.
- Spend: $0.0016, all Jev. No Advisor call ran.

## 1. The chain in code

1. The target question asks one Noul per pool player: "Would {team} want {player} from {owner}?". The yes criterion is "{name} would start for {team} or fill a weak spot on its roster." (`packages/analyzer/python/src/analyzer/finder_search.py:60-63`).
2. A player is a target at 0.6 or more, at most 4 per side (`finder_search.py:71-72`, `_pick_targets` at `finder_search.py:227`).
3. The state is `_pair_state`: for each team, `weak_starting_slots`, `depth`, and `players` (`finder_search.py:145-155`). Each player line shows the Season rank (`finder_search.py:140`). Each weak slot line shows the projected rank. So one player can have two ranks in one state, such as Breece Hall RB42 in `players` and RB18 in `weak_starting_slots`. The state has no points.
4. The Shortlist asks `fair`, `need.<asker>`, and `need.<partner>` of each offer, and ranks by their product, with no floor (`finder_search.py:491`, `finder_search.py:495`).
5. The NEED yes criterion reads only what a team gets: "A player {team} gets would start over a weak starter in `teams.{path}.weak_starting_slots`." (`packages/analyzer/python/src/analyzer/trade_jev.py:24-27`). No question of the Shortlist asks what a team gives up.
6. The target of the asker side asks if the partner wants a player of the asker. It does not ask if the asker can spare him. The Partner filter asks "spares" once per pair, not per player (`finder_search.py:41-56`).

## 2. Method

- Data: the saved CPC week 10 raw folder, `clients/cpc/data/2026/week-10/raw/`. Its rosters are from 2026-11-17, so they are the rosters of week 11. No newer saved folder exists, in the main checkout or in any worktree. No fetch ran.
- Code: a throwaway script in the session scratchpad. It loaded the snapshot as `advisor-eval` does, with `_saved_snapshot` of `apps/pipeline/src/cornerstone/cli.py:166`. It called `search(6, 7, snapshot, jev)` as `_find_one` of `apps/pipeline/src/cornerstone/advisor_eval.py:322` does. It wrapped Jev to keep each state, question, and answer, and it used `Meter` and `MeteredJev` (`advisor_eval.py:215`, `advisor_eval.py:242`) for the cost. The script is deleted.
- Keys: `TYPESAFE_API_KEY` from `~/.secrets`, read by `league/jev.py`.
- The comparisons put each wording as a separate question in one request, over the same state, per the TypeSafe skill. Each change of the state is its own request.
- Gaps of the replay against the live run of 02:51 UTC on 2026-11-19:
  - The live API builds a live week 11 snapshot (`apps/api/src/cornerstone_api/sources.py:60`). The saved snapshot is week 10, with the projections and injuries of 2026-11-17.
  - In the saved snapshot, Kenneth Walker III is Out with no return week, so he is not in the pool. The live run had him as a target of the asker side, so his status changed.
  - The saved week has no chart read. The target state holds no chart value, so this does not change the target step.

## 3. Part 1: the weak slots of roster 6

Code alone, no API call. Source: `weak_slot_rows` and `_weak_limit` (`trade_jev.py:53-80`).

| Slot | Starter | Projected rank | Weak past | Weak |
| --- | --- | --- | --- | --- |
| QB | Aaron Rodgers | QB19 | 12 | yes |
| RB1 | Kyren Williams | RB11 | 12 | no |
| RB2 | Blake Corum | RB26 | 24 | yes |
| WR1 | Matthew Golden | WR7 | 12 | no |
| WR2 | Zay Flowers | WR10 | 24 | no |
| TE | Trey McBride | TE2 | 12 | no |
| FLEX1 | Parker Washington | WR16 | 36 | no |
| FLEX2 | Antonio Williams | WR71 | 36 | yes |

- QB is weak because the rule for a slot with no number is `team_count * 1` (`trade_jev.py:62`). In a 12-team 1QB league, that is QB12. Rodgers projects QB19.
- Lamar Jackson is on IR, and Fernando Mendoza projects QB49. So `depth.QB` is 1, and no bench QB covers.
- By the same rule, Goff (QB14) is a weak starter of roster 7, and Mahomes (QB15) is his backup. Rosters 6, 7, and 9 each have a weak QB slot.
- The rule reads rank, not points. The lineup values of the snapshot show how small the QB gap is:

| Rank | QB | RB | WR |
| --- | --- | --- | --- |
| 12 | 18.6 | 15.6 | 12.9 |
| 14 | 18.4 (Goff) | 15.0 | 12.6 |
| 19 | 15.4 (Rodgers) | n/a | 11.5 |
| 26 | n/a | 9.8 (Corum) | n/a |

- Goff over Rodgers is +3.0 points a week. Mahomes over Rodgers is +2.6. The Playbook says the same in words: QBs are worth the least in this league.

## 4. Part 2: the Jev answers of the target question for each player of roster 7

Replay of `search(6, 7)`, then three more requests over the same pair state. Answers are the probability of yes that roster 6 wants the player.

- The first replay stopped at the Partner filter: `asker_spares` 0.69. A second run passed it at 0.73. This is the coin flip that research 01 found. To replay the target step, the script set the pass line of the filter to 0 in its own copy of the module only.
- The target step of the replay picked no player of roster 7. Mahomes got 0.54 and Goff 0.36, both under 0.6. So the replay gave the wider pass: Mike Washington Jr. for Mahomes, `fair` 0.16. The live run had both QBs at 0.6 or more.
- The partner side wants four starters of roster 6: McBride 0.84, Golden 0.79, Flowers 0.77, Kyren Williams 0.64.

Wordings, as separate questions in one request:

- A, the live question: "Would {team} want {player} from {owner}?", yes "would start for {team} or fill a weak spot".
- B, the start half, in the form of the Spares tree of decision 05: "Would {player} start over {weak starter} of {team} for the rest of the season?". Code asks it only for a player at a weak position, against the weak starter at it: Rodgers, Corum, or Antonio Williams.
- C, the start half alone: "Would {player} start for {team}?"
- D, the weak-spot half alone: "Would {player} fill a weak spot on the roster of {team}?"
- E, the size of the gain: "Would {player} be a big upgrade over {weak starter} for {team}?"

States: S0 is the live pair state, asked twice. S1 is S0 plus a `facts` list that code writes: the lineup format, and per player "X projects N points a week, and the weak starter projects M: +D a week".

| Player | Pos | Pts a week | A S0 | A S0 again | A S1 | B S0 | B S1 | C S0 | C S1 | D S0 | E S0 | E S1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Jared Goff | QB | 18.4 | 0.35 | 0.36 | 0.57 | 0.51 | 0.67 | 0.23 | 0.59 | 0.43 | 0.33 | 0.77 |
| Patrick Mahomes | QB | 18.0 | 0.50 | 0.49 | 0.71 | 0.48 | 0.67 | 0.44 | 0.57 | 0.56 | 0.65 | 0.73 |
| Malik Nabers | WR | 12.8 | 0.51 | 0.52 | 0.49 | 0.78 | 0.74 | 0.48 | 0.63 | 0.48 | 0.86 | 0.94 |
| Ryan Flournoy | WR | 7.5 | 0.48 | 0.48 | 0.47 | 0.73 | 0.73 | 0.24 | 0.35 | 0.60 | 0.72 | 0.65 |
| KC Concepcion Jr. | WR | 7.8 | 0.44 | 0.41 | 0.38 | 0.65 | 0.64 | 0.14 | 0.19 | 0.50 | 0.66 | 0.61 |
| Breece Hall | RB | 11.9 | 0.35 | 0.34 | 0.42 | 0.43 | 0.68 | 0.33 | 0.42 | 0.63 | 0.32 | 0.71 |
| Rhamondre Stevenson | RB | 11.2 | 0.37 | 0.39 | 0.46 | 0.45 | 0.70 | 0.23 | 0.36 | 0.55 | 0.53 | 0.56 |
| Braelon Allen | RB | 10.5 | 0.40 | 0.41 | 0.40 | 0.42 | 0.56 | 0.25 | 0.34 | 0.45 | 0.33 | 0.19 |
| Harold Fannin Jr. | TE | 9.3 | 0.15 | 0.14 | 0.09 | n/a | n/a | 0.12 | 0.10 | 0.11 | n/a | n/a |
| Ashton Dulin | WR | 3.4 | 0.18 | 0.18 | 0.11 | 0.21 | 0.09 | 0.08 | 0.08 | 0.21 | 0.15 | 0.04 |
| Zonovan Knight | RB | 2.8 | 0.17 | 0.19 | 0.08 | 0.12 | 0.05 | 0.09 | 0.08 | 0.18 | 0.09 | 0.03 |

Kyle Pitts Sr. (TE) gets 0.07 to 0.12 in each form. Run to run, the same question on the same state moves by 0.05 at most.

What the table shows:

1. A gives 0.34 to 0.52 to each player who would start for roster 6. It does not split them from the bench players, who get 0.08 to 0.19 under B and E in S1. Mahomes is the highest of roster 7 under A, so a small shift puts the QBs, and only the QBs, over 0.6.
2. In S0, C says Goff would not start for roster 6 (0.23). The state shows him as QB13 and Rodgers as QB19, so this answer is wrong. Jev does not compare ranks well. With the points in S1, C goes to 0.59 and B to 0.67.
3. B, the Spares form, finds the WRs that A misses: Nabers 0.78, Flournoy 0.73. With S1, it also finds the RBs: Hall 0.68, Stevenson 0.70.
4. E with S1 ranks the gain the right way: Nabers 0.94 (+6.9 over Antonio Williams), Goff 0.77, Mahomes 0.73, Hall 0.71, Allen 0.19.
5. With the points, the QBs rise, they do not fall. Goff is a real upgrade over Rodgers, so a fix of the target step alone does not stop "Flowers for Goff".

## 5. Part 3: the cause

The target question, the weak-slot rule, and the state each play a part. The main cause is that no step asks what the asker gives up.

1. **The give side, the main cause.** The asker side of the target step lists the four best starters of roster 6, because roster 7 would want them. No question asks if roster 6 can spare them. The NEED question reads only what a team gets (`trade_jev.py:26`). The Shortlist product has no floor, so `need.6` and `need.7` near 0.86 carry an offer with `fair` near 0.3. The live log shows the same: `fair` 0.29 to 0.39 and a need near 0.9.
2. **The target question, a contributor.** The "or" in "would start or fill a weak spot" gives a flat, low answer for each starter. It does not make QBs wanted on its own. It makes the pick of targets a near coin flip, and the QBs won that flip in the live run. So the live Shortlist had only QB trades.
3. **The state, a contributor.** The state has no points, and it shows two ranks per player. Jev then judges "would start" wrongly, as for Goff under C in S0.
4. **The weak-slot rule, not a bug.** QB19 in a 12-team 1QB league is a weak starter by any rank rule. The rule ignores the size of the gap, but a change to the weak rank is a threshold change, out of the frame of decision 05.

The cost side of the two live offers, from the trade state that the Shortlist reads (`trade_jev_state`, `trade_jev.py:112`). T0 is that state. T1 adds, for each team, `weak_starting_slots_after` and `lineup_points_a_week` before and after, which code counts. Two new questions:

- `hole.6`: "Does {team} open a hole in its lineup by giving {player}?"
- `gain.6`: "Does the lineup of {team} get better in this trade?"

| Offer | Lineup of 6, before to after | State | fair | need.6 | need.7 | hole.6 | gain.6 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Zay Flowers for Goff | 110.0 to 103.8 | T0 | 0.38 | 0.86 | 0.86 | 0.68 | 0.24 |
| Zay Flowers for Goff | 110.0 to 103.8 | T1 | 0.29 | 0.75 | 0.75 | 0.70 | 0.09 |
| Kyren Williams for Mahomes | 110.0 to 101.0 | T0 | 0.48 | 0.90 | 0.72 | 0.73 | 0.22 |
| Kyren Williams for Mahomes | 110.0 to 101.0 | T1 | 0.28 | 0.63 | 0.48 | 0.91 | 0.08 |
| Kenneth Walker III for Mahomes | 110.0 to 112.6 | T0 | 0.24 | 0.85 | 0.84 | 0.65 | 0.15 |
| Kenneth Walker III for Mahomes | 110.0 to 112.6 | T1 | 0.31 | 0.72 | 0.49 | 0.66 | 0.80 |

- Kyren Williams for Mahomes stands in for the live Walker offer, because Walker cannot play now in the saved snapshot. That also explains the Walker rows: code counts his loss as 0 points, so `gain.6` goes up. The live state can differ.
- With the lineup-points fact, `gain.6` gives a clear no to both bad offers (0.09, 0.08), and a yes where the lineup gains.
- `hole.6` stays unsure in T0 (0.65 to 0.73). It reads better with the slots after (0.91 for Kyren Williams), but not for Flowers (0.70).
- `need.6` stays high in T0 for each bad offer. The NEED question does its own job well. It just does not cover the cost.

## 6. Part 4: the fix options, in the frame of decision 05

Each option keeps `YES_AT`, `NO_AT`, and `TARGET_AT` as they are. None cuts an offer by a score. Each needs the bar of decision 05, with "Zay Flowers for Goff" as a new Backtest mark of roster 6.

1. **Code logic: the Spares rule on the give side.** Decision 05 already has code list only a player "with a backup above the line behind him". Apply the same list to the targets of the asker side, in place of the open target question. For roster 6 to roster 7, no bench WR is above the line, so Flowers, Golden, and Parker Washington are not listed. McBride is not listed either, because roster 7 has no weak TE. This is a count, which code does, and it fits the Spares tree that decision 05 builds. One wrinkle: `depth` counts Walker above the line while he is Out (`finder_search.py:150`), so the count must read "can play now" as `lineup_now` does.
2. **A split question with a better state: "gain" on the Shortlist.** Add `weak_starting_slots_after` and the lineup points before and after of each side to the trade state, as code facts. Ask `gain.<asker>` beside `fair` and `need`. Code stops an offer only on a clear no, below `NO_AT`, as decision 05 stops a side. In this replay, that stops both bad offers (0.09, 0.08). Decision 05 says Jev compares no numbers. So the fact must state the change, such as "the lineup of roster 6 loses 6.2 points a week", not two totals.
3. **A split target question with a better state.** Replace the "or" question with B, the Spares form, and put the points of the player and of the weak starter in the state as facts. Show one rank per player, the projected rank, in `players` and `weak_starting_slots`. In this replay, this gives roster 6 seven players of roster 7 over 0.6, with WRs and RBs beside the QBs. It adds variety. It does not stop the bad offers, because the QBs stay wanted.
4. **Code logic: leave the weak-slot rule.** A rule that weighs the QB gap by points would be a cut by a score, or a threshold change. Option 3 gives Jev the gap as a fact.

**Recommendation, not a decision:** options 1 and 2 together, because the bad trades come from the give side. Option 1 rides on the Spares tree of Deadline week. Option 2 is one more question and two state fields on the Shortlist. Option 3 belongs with the later split of the target question that decision 05 puts out of scope, unless Brian wants more than QBs in this spec. Brian decides.

## 7. Spend

- Total: $0.0016, measured by the `Meter` of `advisor_eval.py`. 14 Jev requests. No Claude call ran.
- The Advisor pick did not run, because parts 1 to 4 need only the Jev answers.
