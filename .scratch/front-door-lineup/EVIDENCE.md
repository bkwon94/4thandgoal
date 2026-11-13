# Front door lineup: evidence

Spec: `.scratch/front-door-lineup/PRD.md`. Acceptance tests: `.scratch/front-door-lineup/ACCEPTANCE.md`.
Built from: `2adcc0c4`, on 2026-11-12. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 40 min for 32 site tests. The round ran in parts, each with one local API process and a fresh ask folder, because the API caps a team at 25 Claude Answers a day. For each test with a stream, the stream and the shots come from one run: the curl, then the shots, then a second curl; see `evidence/round.txt`.
The live week is `2026` week 10 at the time of the evidence (Sleeper `state/nfl`), and each stream file names its UTC time. The round output is `evidence/round.txt`. The site shots of the league Topics read `topics.json` version 2, rebuilt locally at 2adcc0c4 from the saved raw week 9 (see AT-40) and put back with `git restore` after the round.

## AT-1: The cpc lineup follows the Sleeper slot order

App: api, site
Then: The lineup block shows the rows QB, RB, RB, WR, WR, TE, FLEX, FLEX, DEF in that order. Each row shows the slot, the player, his NFL team, the opponent, the kickoff, and the projection.
Files: `evidence/AT-1/375-dark.png`, `evidence/AT-1/375-light.png`, `evidence/AT-1/768-dark.png`, `evidence/AT-1/768-light.png`, `evidence/AT-1/1280-dark.png`, `evidence/AT-1/1280-light.png`, `evidence/AT-1/steps.json`, `evidence/AT-1/stream.txt`
Observation: The stream (21:49:20 UTC, live week 10, one try) has one `lineup` block for team 6 with the rows QB, RB, RB, WR, WR, TE, FLEX, FLEX, DEF in that order. Each row carries `slot`, `player`, `nfl_team`, `opponent`, `kickoff` (epoch ms), and `projection`; the total is 121.2. The second curl after the shots gives the same block. The Suggestions of Bo Girds hold Weak spots, How you stack up, and Waiver targets (see AT-42), so the step list opens Start or sit from "More".
Observation of the shots: All 6 shots show the "WEEK 10 LINEUP" block of Bo Girds with "By projection 121.2" and the rows QB, RB, RB, WR, WR, TE, FLEX, FLEX, DEF in that order, from Aaron Rodgers 17.4 to Jacksonville Jaguars 7.0. Each row shows the slot, the player, a line such as "PIT vs CIN · Sun 8:20 PM", and the projection. The fixed foot with the chips More, Holes, Roster, Waivers and the ask box sits over the Answer text below the block in each shot.

## AT-2: The norcal lineup has three FLEX and no DEF

App: api, site
Then: The lineup block shows the rows QB, RB, RB, WR, WR, TE, FLEX, FLEX, FLEX in that order, and no DEF row.
Files: `evidence/AT-2/375-dark.png`, `evidence/AT-2/375-light.png`, `evidence/AT-2/768-dark.png`, `evidence/AT-2/768-light.png`, `evidence/AT-2/1280-dark.png`, `evidence/AT-2/1280-light.png`, `evidence/AT-2/steps.json`, `evidence/AT-2/stream.txt`
Observation: The norcal stream (22:28:35 UTC, one try) has one `lineup` block for team 7 with the rows QB, RB, RB, WR, WR, TE, FLEX, FLEX, FLEX in that order and no DEF row; the total is 134.0. In the first run of this test the second curl gave 134.0 against 134.1, so the test ran again; in the second run both curls give the same block. The step list opens Start or sit from "More", as in AT-1.
Observation of the shots: All 6 shots show the norcal "WEEK 10 LINEUP" of Bo Girds with "By projection 134.0" and the rows QB, RB, RB, WR, WR, TE, FLEX, FLEX, FLEX, from Trevor Lawrence 24.6 to Kaleb Johnson 7.3, and no DEF row. The fixed foot sits over the Answer text; its chips read Holes, Roster, Waivers in 375-light and both 768 shots, and Holes, Sell high, Roster in 375-dark and both 1280 shots.

## AT-3: The projection is in the points of the league

App: api
Then: The projection of that starter equals his Sleeper projected stat line scored with the scoring settings of cpc, half PPR, to 0.1 point.
Files: `evidence/AT-3/sum.txt`
Observation: `sum.txt` (fetched at 22:54 UTC on 2adcc0c4) scores the Sleeper projected stat line of Zay Flowers (WR, starter of Bo Girds, 5.79 receptions) with the cpc `scoring_settings` (`rec` 0.5): the sum is 13.523, 13.5 to 0.1 point, and Sleeper `pts_half_ppr` is 13.54. The AT-1 stream gives Zay Flowers `projection` 13.5.

## AT-4: A Swap row names the benched starter

App: site
Then: The Swap row reads "Swap over <starter name>" with the starter name struck through, and the first row with a Swap or a Q is open on arrival with its reason.
Files: `evidence/AT-4/375-dark.png`, `evidence/AT-4/375-light.png`, `evidence/AT-4/768-dark.png`, `evidence/AT-4/768-light.png`, `evidence/AT-4/1280-dark.png`, `evidence/AT-4/1280-light.png`, `evidence/AT-4/steps.json`, `evidence/AT-4/stream.txt`
Observation: No lineup of Bo Girds has a Swap in week 10, so the step list uses puurdygood (norcal roster 1). Its stream (23:01:01 UTC, one try) has one Swap row: FLEX Brenton Strange (9.9) with `swap.over` "D. Boston" (`over_projection` 10.3) and a `reason` sentence. The first row with a Swap or a Q is TE Harold Fannin Jr., a Q row with `body_part` "Groin" and a `pivot`. The block `total` is 131.5 and `swap_total` is 131.1. Before each shot the step list scrolls to the end, then to the Swap row. The second curl gives the same totals and row values; only the `reason` text of the Swap differs, because the page wrote its own Answer.
Observation of the shots: The 375 light shot shows the FLEX row of Brenton Strange at 9.9 with "Swap over D. Boston", the name D. Boston struck through, and the header total 131.1 with "With 1 Swap" selected. In each full-page shot, the fixed top band and the team bar draw once at their place on the screen, so they sit across the rows from WR down to the open Fannin Q row.

## AT-5: A Swap needs a probability of 0.7

App: api
Then: The first case marks a Swap. The second case keeps the starter.
Files: `evidence/AT-5/output.txt`
Observation: `output.txt` (22:53 UTC on 2adcc0c4) runs both cases of `test_a_bench_player_takes_the_slot_at_a_probability_of_0_70_and_not_at_0_69`, [0.7-swaps0] and [0.69-swaps1], and ends with `2 passed`.

## AT-6: The Swap candidates resolve by the highest probability

App: api
Then: The bench player at 0.85 takes the first slot. The bench player who beats two starters fills only the slot at 0.9.
Files: `evidence/AT-6/output.txt`
Observation: `output.txt` (22:53 UTC on 2adcc0c4) runs `test_the_swap_candidates_resolve_by_the_highest_probability_and_fill_each_slot_once` and ends with `1 passed`.

## AT-7: A Q row shows the risk and the Pivot

App: site
Then: The row shows the body part and the practice level, and the Pivot line reads "Start <starter> if he is active. If he is ruled out, start <bench player>."
Files: `evidence/AT-7/375-dark.png`, `evidence/AT-7/375-light.png`, `evidence/AT-7/768-dark.png`, `evidence/AT-7/768-light.png`, `evidence/AT-7/1280-dark.png`, `evidence/AT-7/1280-light.png`, `evidence/AT-7/steps.json`, `evidence/AT-7/stream.txt`
Observation: No starter of Bo Girds is Questionable in week 10, so the test uses NFC Least (cpc roster 4). Its stream (22:35:43 UTC, one try) has two Q rows. The first is FLEX Hunter Henry, with `body_part` "Foot", `practice` "No practice report yet", and `pivot` "Start H. Henry if he is active. If he is ruled out, start S. McGowan." The second is FLEX David Montgomery, with "Groin", the same practice text, and "Start D. Montgomery if he is active. If he is ruled out, start S. McGowan." No row has a Swap. The second curl gives the same block.
Observation of the shots: All 6 shots show the NFC Least lineup with "By projection 90.2", and the FLEX row Hunter Henry with a red Q tag open, with "Foot · No practice report yet" and a red-ruled line "Start H. Henry if he is active. If he is ruled out, start S. McGowan." The FLEX row David Montgomery also has a Q tag and stays closed; at 768 and 1280 the fixed foot covers the "Can't play" line, and at 1280 it also covers the DEF row in part.

## AT-8: A blank practice level reads as no report

App: api
Then: The Q tag reads "No practice report yet".
Files: `evidence/AT-8/player.txt`, `evidence/AT-8/stream.txt`
Observation: Deebo Samuel Sr. is no longer a Q starter, so the test uses Hunter Henry (3214), FLEX of NFC Least (cpc roster 4). `player.txt` (Sleeper at 22:55 UTC) shows him with `injury_status` "Questionable", `injury_body_part` "Foot", and `practice_participation` null. The 18 Questionable starters of the 24 Sleeper lineups of week 10 all have `practice_participation` null. The stream of his lineup (22:55:33 UTC, one try) gives his Q row `practice` "No practice report yet".

## AT-9: An open row does not move the other rows

App: site
Then: Each row above the open row keeps the same top position to 1 px, and the detail comes into view from a blur.
Files: `evidence/AT-9/after-375-light.png`, `evidence/AT-9/before-375-light.png`, `evidence/AT-9/positions.txt`, `evidence/AT-9/steps.json`, `evidence/AT-9/steps.txt`, `evidence/AT-9/stream.txt`
Observation: Bo Girds has no row with detail in week 10, so the test uses Teehee (cpc roster 12). Its stream (22:37:18 UTC, one try) has three Q rows: RB Bhayshul Tuten, WR Amon-Ra St. Brown, and FLEX Garrett Wilson. `positions.txt` (22:38:01 UTC) shows a tap on the closed WR row (index 3): rows 0 to 3 keep their tops (delta 0 px), and rows 4 to 8 move down 53 to 54 px. The computed filter of the opened detail reads blur(2.88px) at about 30 ms, blur(0.20px) at about 120 ms, and none at about 400 ms. The second curl gives the same block.
Observation of the shots: The before shot shows the Teehee lineup with the RB row Bhayshul Tuten open and the WR row Amon-Ra St. Brown closed; the after shot shows that WR row open with "Ribs · No practice report yet" and "Start A. St. Brown if he is active." The QB, RB, RB, and WR rows sit at the same height in both shots, and the rows below move down about 53 px, from Tee Higgins on; no blur is visible in the two still shots.

## AT-10: The players who cannot play sit in one line

App: site
Then: One line under the rows names each such player with his status, in the shape "Can't play: J. Jacobs Out (finger)".
Files: `evidence/AT-1/stream.txt`, `evidence/AT-1/375-light.png`, `evidence/AT-1/375-dark.png`, `evidence/AT-1/768-light.png`, `evidence/AT-1/768-dark.png`, `evidence/AT-1/1280-light.png`, `evidence/AT-1/1280-dark.png`
Observation: The lineup of Bo Girds (AT-1 stream, 21:49:20 UTC) has `cannot_play` [L. Jackson, IR, Thumb]. The shots are those of AT-1, the Answer of Bo Girds on arrival.
Observation of the shots: The 6 shots of AT-1 show one line under the DEF row that reads "Can't play: L. Jackson IR (thumb)", with "Can't play:" in bold. At every width the line sits just above the fixed foot and is fully visible.

## AT-11: The toggle shows what the Swaps change

App: site
Then: The total in the header changes between the two states, and the "With N Swaps" total equals the sum of the projections of the lineup with the Swaps.
Files: `evidence/AT-11/by-projection-swap-375-light.png`, `evidence/AT-11/by-projection-total-375-light.png`, `evidence/AT-11/steps.json`, `evidence/AT-11/sum.txt`, `evidence/AT-11/with-swaps-swap-375-light.png`, `evidence/AT-11/with-swaps-total-375-light.png`
Observation: The lineup of AT-4 (puurdygood, norcal roster 1) has one Swap: Brenton Strange 9.9 over Denzel Boston 10.3. `sum.txt` adds the rows with the Swap to 131.1, and the block `swap_total` is 131.1. The block `total` is 131.5, and the sum with the benched starter back in his slot is 131.5. For each state of the toggle the step list takes two shots: `-total`, scrolled to the header total, and `-swap`, scrolled to the Swap row.
Observation of the shots: `by-projection-total` shows "By projection" selected with the header total 131.5, and `with-swaps-swap` shows "With 1 Swap" selected with 131.1 and the Strange row "Swap over D. Boston" with the name struck through. In both states the rows stay the same, and only the header total changes; `with-swaps-swap` shows the fixed top band and team bar across the middle rows, as the full-page capture draws them.

## AT-12: A started game locks its players

App: api
Then: After the `start_time`, that player is neither a Swap nor a starter that a Swap replaces.
Files: `evidence/AT-12/locked-run.txt`, `evidence/AT-12/pytest.txt`, `evidence/AT-12/scores.txt`, `evidence/AT-12/stream.txt`
Observation: `locked-run.txt` runs the API over the recorded Sleeper week 10, where WAS at NYG (game 202611023) has `start_time` 1794532500000 (2026-11-13 01:15 UTC), `has_started` false, and status pre_game. The repo Jev fake answers 0.95 for Seth McGowan over Austin Ekeler (WAS) and for Eli Raridon over Isaiah Likely (NYG), on the lineup of Bo Girds of norcal (roster 7). At the clock 2026-11-12 12:53 UTC the block has both Swaps, with Ekeler and Likely as the benched starters. At the clock 2026-11-13 01:16 UTC, Likely holds TE and Ekeler holds FLEX with `locked` true, and the block has no Swap. The same file shows the 15 recorded week 9 games each with `has_started` true and locked at a clock of 2026-09-01. `locked-run.txt` and `pytest.txt` come from `2adcc0c4`; `pytest.txt` gives the three lock tests: 3 passed. `stream.txt` and `scores.txt` are the live stream and the live `scores` query from before the kickoff, at 17:49:30 and 17:31:20 UTC, with both players `locked` false.

## AT-13: Start or sit follows the order of the day

App: api
Then: Start or sit is first on Thursday and on Sunday, third on Wednesday after Waiver targets, and the Monday order is the order of today.
Files: `evidence/AT-13/output.txt`
Observation: `output.txt` (22:53 UTC on 2adcc0c4) runs the four Suggestions tests for Thursday, Sunday, Wednesday, and Monday and ends with `4 passed`.

## AT-14: A hole in the lineup lifts Start or sit

App: api
Then: Start or sit is first.
Files: `evidence/AT-14/output.txt`
Observation: `output.txt` (22:53 UTC on 2adcc0c4) runs `test_a_starter_on_ir_lifts_start_or_sit_first_on_a_tuesday` and ends with `1 passed`.

## AT-15: The Suggestion fact counts the holes and the Q starters

App: api
Then: The first fact has the shape "1 can't play, 1 Q". The second fact reads "Next kickoff <day> <time>".
Files: `evidence/AT-15/pytest.txt`, `evidence/AT-15/sleeper-starters.txt`, `evidence/AT-15/suggestions-bo-girds.txt`, `evidence/AT-15/suggestions-nfc-least.txt`
Observation: `sleeper-starters.txt` (Sleeper at 20:46:39 UTC) gives the starters of NFC Least (cpc roster 4) as QB Kirk Cousins, RB Chase Brown, RB Cam Skattebo, WR Tetairoa McMillan, WR Jameson Williams, TE Tyler Warren, FLEX David Montgomery (HOU, Questionable), FLEX Hunter Henry (NE, Questionable), and DEF KC, with no other status and no empty slot. Its Suggestions (20:47 UTC) give the Start or sit fact "2 Q" and no kickoff. The starters of Bo Girds (cpc roster 6) are Aaron Rodgers, Kenneth Walker III, Kyren Williams, Matthew Golden, Parker Washington, Trey McBride, Zay Flowers, Blake Corum, and DEF JAX, with no status and no empty slot. Its Suggestions give "Next kickoff Sun 1:00 PM" with the kickoff 1794765600000. In `sleeper-starters.txt` no team of cpc or norcal has a Q starter together with an Out or IR starter or an empty slot, so no file shows the shape "1 can't play, 1 Q". `pytest.txt` runs the Suggestions route over the recorded Sleeper week 10 of cpc, with the starters of Unsolicited Dak Picks (roster 11) set. With J. Jacobs Out and A.J. Brown and George Pickens Questionable as starters, the test reads the fact "1 can't play, 2 Q". With two empty starter slots and those three on the bench, it reads "2 can't play". Both tests passed at `2adcc0c4`. The Suggestions files and `sleeper-starters.txt` come from the run at `fb332f14`; between `fb332f14` and `2adcc0c4`, only `ask_wording.py`, `free_wording.py`, and `personal_wording.py` changed in `apps/api/src`, so the Suggestions route and `start_sit_fact.py` are the same.

## AT-16: A two-player question gets the comparison block

App: api, site
Then: The Answer is Start or sit with the comparison block: a pair of bars from a center line for each fact, the winning side of each fact in red, a dot on each cited fact, and the line "Start <name>."
Files: `evidence/AT-16/375-dark.png`, `evidence/AT-16/375-light.png`, `evidence/AT-16/768-dark.png`, `evidence/AT-16/768-light.png`, `evidence/AT-16/1280-dark.png`, `evidence/AT-16/1280-light.png`, `evidence/AT-16/ask.txt`, `evidence/AT-16/steps.json`, `evidence/AT-16/stream.txt`
Observation: The `ask` route sends the question to the Topic start_sit. The stream (22:15:13 UTC) is the third try: the first two ended with `data-miss`. It has a `comparison` block of K. Williams (15.6) and B. Corum (10.5) with 8 facts and `pick` 0. The block comes first with `cited` false on every fact, then after the check with `cited` true on Projection, Snap share, and Carry share. The text starts "Start Kyren Williams." The second curl gives the same block values. A typed question is not kept, so each page of the shots is a new Claude run: the block values match, and the text can differ.
Observation of the shots: All 6 shots show the question "Start Kyren Williams or Blake Corum?" and a comparison block of K. Williams (red name) and B. Corum, with 8 facts, each a pair of bars from a center tick. Red bars fill the left side for Projection 15.6 to 10.5, Snap share 61% to 38%, Target share 7% to 4%, and Carry share 50% to 42%; red dots sit on Projection, Snap share, and Carry share; ties show gray on both sides; the bold line "Start K. Williams." follows, and the fixed foot covers the rest of the text.

## AT-17: A question with three players gets the lineup block for their slot

App: api, site
Then: The Answer shows the lineup block for the WR and FLEX slots.
Files: `evidence/AT-17/375-dark.png`, `evidence/AT-17/375-light.png`, `evidence/AT-17/768-dark.png`, `evidence/AT-17/768-light.png`, `evidence/AT-17/1280-dark.png`, `evidence/AT-17/1280-light.png`, `evidence/AT-17/ask.txt`, `evidence/AT-17/steps.json`, `evidence/AT-17/stream.txt`
Observation: The `ask` route sends the question to start_sit. The stream (22:16:43 UTC) is the second try: the first ended with `data-miss`. It has a `lineup` block with the rows WR Zay Flowers 13.5, WR Matthew Golden 12.9, FLEX Parker Washington 12.5, and FLEX Blake Corum 10.5, a total of 49.4, then text. The second curl gives the same block. A typed question is not kept, so each page of the shots is a new Claude run: the block values match, and the text can differ.
Observation of the shots: All 6 shots show the question "Should I start Zay Flowers, Matthew Golden, or Parker Washington?" and a "WEEK 10 LINEUP" block with "By projection 49.4" and the rows WR Zay Flowers 13.5, WR Matthew Golden 12.9, FLEX Parker Washington 12.5, and FLEX Blake Corum 10.5. The Answer text differs in each shot and ends with "Checked"; the card ends above the foot.

## AT-18: A player off the roster goes to a free answer

App: api
Then: The Answer is a free answer, not Start or sit.
Files: `evidence/AT-18/ask.txt`, `evidence/AT-18/stream.txt`
Observation: The `ask` route (22:19:34 UTC) gives `route` "free" and `topic` null. The free answer stream (22:19:34 UTC) has no data-block. Its text says that the log lists Kyren Williams with Bo Girds and Amon-Ra St. Brown with Teehee.

## AT-19: The NFL game card shows in a free answer

App: api, site
Then: The free answer shows the NFL game card: a tug bar of the expected margin, a strip of the 32 defenses with the opponent lit, and two pass-share bars against a league mark. The margin equals the gap of the two Sleeper DEF projections.
Files: `evidence/AT-19/375-dark.png`, `evidence/AT-19/375-light.png`, `evidence/AT-19/768-dark.png`, `evidence/AT-19/768-light.png`, `evidence/AT-19/1280-dark.png`, `evidence/AT-19/1280-light.png`, `evidence/AT-19/ask.txt`, `evidence/AT-19/def-projections.txt`, `evidence/AT-19/steps.json`, `evidence/AT-19/stream.txt`
Observation: The `ask` route gives `route` "free". The free answer stream (22:18:22 UTC) has an `nfl_game` block "Week 11: Bears vs Saints" with `projected` CHI 29.25 and NO 19.75, `margin` 9.5, and a strip of 32 defenses with NO lit. `def-projections.txt` (fetched after the round) gives `pts_allow` 19.75 for the CHI DEF and 29.25 for the NO DEF in week 11, a gap of 9.5. The second curl gives the same block.
Observation of the shots: All 6 shots show the question "How does the Bears game look?" and a card "WEEK 11: BEARS VS SAINTS · PROJECTED" with Bears 29.3 and Saints 19.8, a red bar from the center to the left labeled "Bears by 9.5", and a strip of about 32 gray bars from "Fewest" to "Most" with one red bar, the fourth from the right. Under them, "Saints allow 104.1 points to all positions a game, 29th fewest of 32", and two "PASS SHARE" bars, Bears 51% and Saints 60%, each with a tick at the mark "League 55%"; 375-light alone has an extra line "Reading the league data" at the top of the card.

## AT-20: A failed Jev call gives the honest miss

App: api
Then: The Answer is the honest miss, with no lineup and no Swap.
Files: `evidence/AT-20/output.txt`
Observation: `output.txt` (22:53 UTC on 2adcc0c4) runs the two honest-miss tests, a failed Jev read and a failed read of the two players, and ends with `2 passed`.

## AT-21: A Topic Answer shows one block at most

App: site
Then: Each Answer shows one block or none. Position leaders and recent trades shows no block, and its text lists one leader per position.
Files: `evidence/AT-21/how-you-stack-up-375-dark.png`, `evidence/AT-21/how-you-stack-up-375-light.png`, `evidence/AT-21/playoff-race-375-dark.png`, `evidence/AT-21/playoff-race-375-light.png`, `evidence/AT-21/position-leaders-1280-light.png`, `evidence/AT-21/position-leaders-and-recent-375-dark.png`, `evidence/AT-21/position-leaders-and-recent-375-light.png`, `evidence/AT-21/power-rankings-375-dark.png`, `evidence/AT-21/power-rankings-375-light.png`, `evidence/AT-21/sell-high-or-buy-375-dark.png`, `evidence/AT-21/sell-high-or-buy-375-light.png`, `evidence/AT-21/start-or-sit-375-dark.png`, `evidence/AT-21/start-or-sit-375-light.png`, `evidence/AT-21/steps.json`, `evidence/AT-21/steps.txt`, `evidence/AT-21/trade-check-375-dark.png`, `evidence/AT-21/trade-check-375-light.png`, `evidence/AT-21/trade-ideas-375-dark.png`, `evidence/AT-21/trade-ideas-375-light.png`, `evidence/AT-21/waiver-targets-375-dark.png`, `evidence/AT-21/waiver-targets-375-light.png`, `evidence/AT-21/weak-spots-375-dark.png`, `evidence/AT-21/weak-spots-375-light.png`, `evidence/AT-21/week-recap-375-dark.png`, `evidence/AT-21/week-recap-375-light.png`, `evidence/AT-21/your-last-matchup-375-dark.png`, `evidence/AT-21/your-last-matchup-375-light.png`, `evidence/AT-21/your-next-matchup-375-dark.png`, `evidence/AT-21/your-next-matchup-375-light.png`, `evidence/AT-21/your-season-375-dark.png`, `evidence/AT-21/your-season-375-light.png`
Observation: The step list opens all 14 Topics of Bo Girds in one Thread, with Clear between them, one shot per Topic at 375 px, light and dark. `position-leaders-1280-light.png` comes from the extra run (see `steps.txt`).
Observation of the shots: Each of the 14 light shots at 375 px shows one card under the Topic bubble: 12 cards hold one block (slot rank bars, ladder, rank movers, sell list, week 10 lineup, trade ideas list, waiver list, bye grid, recap strip, final matchup, projected matchup, schedule strip), and Trade check holds only text with an "Open the Trade page" button. Position leaders and recent trades shows no block, only a text list of five lines, one leader each for QB, RB, WR, TE, and DEF, in the 375 light shot, the 375 dark shot, and the 1280 light shot; the dark shots of Playoff race and Weak spots show the same block as their light shots. In the long shots of Start or sit, Trade ideas, Weak spots, Your last matchup, and Your next matchup, the fixed foot with the ask box sits once over the card text in the middle of the page.

## AT-22: The cpc recap card shows the median

App: pipeline, site
Then: The recap card shows 114.07, 3rd of 12, a strip with a mark for each team, and a median tick at 103.51.
Files: `evidence/AT-22/375-dark.png`, `evidence/AT-22/375-light.png`, `evidence/AT-22/768-dark.png`, `evidence/AT-22/768-light.png`, `evidence/AT-22/1280-dark.png`, `evidence/AT-22/1280-light.png`, `evidence/AT-22/block-cpc-week_recap.json.txt`, `evidence/AT-22/steps.json`
Observation: `block-cpc-week_recap.json.txt` (rebuilt `topics.json`) gives the `block` of Week recap for roster 6: `kind` "recap", `score` 114.07, `place` 3 of `teams` 12, a `strip` of 12 teams, and `median` 103.51.
Observation of the shots: In all six shots the Week recap card shows "114.07", "3rd of 12", "Won vs Teehee, 100.63", a strip from 64.65 to 144.03 with a red YOU mark, and a dashed tick labeled "Median 103.51" just left of the middle. The strip shows 11 separate marks, one of them thicker near 106; the block data has two scores at 106.71 and 106.39, so two marks draw as one.

## AT-23: The norcal recap card has no median

App: pipeline, site
Then: The recap card shows 155.38 against kaiedmonds, and no median tick.
Files: `evidence/AT-23/375-dark.png`, `evidence/AT-23/375-light.png`, `evidence/AT-23/768-dark.png`, `evidence/AT-23/768-light.png`, `evidence/AT-23/1280-dark.png`, `evidence/AT-23/1280-light.png`, `evidence/AT-23/block-norcal-week_recap.json.txt`, `evidence/AT-23/steps.json`
Observation: `block-norcal-week_recap.json.txt` gives the `block` of Week recap for norcal roster 7: `score` 155.38, `opponent` "kaiedmonds" with `opponent_score` 128.06, and `median` null.
Observation of the shots: In all six shots on the NORCAL APEX 6 site the Week recap card shows "155.38", "2nd of 12", "Won vs kaiedmonds, 128.06", and a strip of 12 marks from 83.1 to 156.88 with a red-orange YOU mark near the right end. The strip has no dashed tick and no "Median" label under it, only the two end values.

## AT-24: The last matchup shows the final scores slot by slot

App: pipeline, site
Then: The matchup card shows 114.07 to 100.63 against Teehee, then the two lineups slot by slot, each slot with a bar from the center line for its gap.
Files: `evidence/AT-24/375-dark.png`, `evidence/AT-24/375-light.png`, `evidence/AT-24/768-dark.png`, `evidence/AT-24/768-light.png`, `evidence/AT-24/1280-dark.png`, `evidence/AT-24/1280-light.png`, `evidence/AT-24/block-cpc-last_matchup.json.txt`, `evidence/AT-24/steps.json`
Observation: `block-cpc-last_matchup.json.txt` gives the `block` of Your last matchup for roster 6: `kind` "matchup", `final` true, you 114.07, Teehee 100.63, and 9 slots, each with the points of each side.
Observation of the shots: In all six shots the card shows "FINAL", Bo Girds 114.07 in red against Teehee 100.63, a red share bar, and nine slot rows QB, RB, RB, WR, WR, TE, FLEX, FLEX, DEF with each side's player and points. Under each slot a bar runs from the center line, red to the left where Bo Girds scored more (for example K. Walker III 34.3 against 8.9) and grey to the right where Teehee scored more (for example Z. Flowers 3.8 against 17.2). In each shot the fixed foot with the chips and the ask box sits over the Answer text below the card.

## AT-25: The next matchup is live

App: api, site
Then: The matchup card shows the two projected totals of the live week and the win odds, and the team with the higher total has odds above 50%. The card data has a read time within the minute of the request.
Files: `evidence/AT-25/375-dark.png`, `evidence/AT-25/375-light.png`, `evidence/AT-25/768-dark.png`, `evidence/AT-25/768-light.png`, `evidence/AT-25/1280-dark.png`, `evidence/AT-25/1280-light.png`, `evidence/AT-25/steps.json`, `evidence/AT-25/stream.txt`
Observation: The `next-matchup` stream (22:01:38 UTC) has a `matchup` block with `final` false, Bo Girds 121.2 against The Blue Tent 94.5, `odds` 0.802 for Bo Girds, and `read_at` 2026-11-12T17:01:38-05:00 (22:01:38 UTC). In both runs of this test, the second curl differs from the first only in `read_at`.
Observation of the shots: In all six shots the card shows "PROJECTED", Bo Girds 121.2 against The Blue Tent 94.5, a red bar with "80%" on the left and "20%" on the right, nine slot rows with bars from the center, and the line "Live projections as of" 5:01 PM in the 375 light shot, 5:02 PM in four shots, and 5:03 PM in the 1280 dark shot. The stream read time is 5:01:38 PM local, and the fixed foot sits over the Answer text, which talks about Lil Fridge, London Cooking, Teehee, and NFC Least.

## AT-26: Power rankings shows the rank mover list

App: pipeline, site
Then: The block shows one row per team with the rank, the name, a bar from the center for the move, and an arrow with the number of places.
Files: `evidence/AT-26/375-dark.png`, `evidence/AT-26/375-light.png`, `evidence/AT-26/768-dark.png`, `evidence/AT-26/768-light.png`, `evidence/AT-26/1280-dark.png`, `evidence/AT-26/1280-light.png`, `evidence/AT-26/block-cpc-power_rankings.json.txt`, `evidence/AT-26/steps.json`
Observation: `block-cpc-power_rankings.json.txt` gives the `block` of Power rankings: `kind` "rank_movers" with 12 rows, one per team, each with `rank`, `name`, and `move`. The first row is Return of T Mac, rank 1, move 3.
Observation of the shots: In all six shots the block shows 12 rows, ranks 1 to 12, each with a team name, a bar from a center line, and a mark at the right: a blue up arrow with 3 for ranks 1, 2, 4, and 5, a red down arrow with 2 or 4 for ranks 3 and 6 to 8, a dash for ranks 9 and 10, "▲1" for NFC Least, and "▼1" for behold the lamb. Row 4 reads "Bo Girds YOU" in red, and the first row is Return of T Mac with "▲3".

## AT-27: Playoff race shows the standings ladder

App: pipeline, site
Then: The ladder shows 12 rows with the rank, the name, an odds bar, and the record, a rule under the 6th row, and the Bo Girds row in red.
Files: `evidence/AT-27/375-dark.png`, `evidence/AT-27/375-light.png`, `evidence/AT-27/768-dark.png`, `evidence/AT-27/768-light.png`, `evidence/AT-27/1280-dark.png`, `evidence/AT-27/1280-light.png`, `evidence/AT-27/block-cpc-playoff_race.json.txt`, `evidence/AT-27/steps.json`
Observation: `block-cpc-playoff_race.json.txt` gives the `block` of Playoff race: `kind` "ladder", `playoff_teams` 6, and 12 rows with rank, name, record, and odds. The Bo Girds row (rank 2, 11-7, 82) has `you` true.
Observation of the shots: In all six shots the ladder shows 12 rows, each with the rank, the name, an odds bar with a percent, and a W-L record, from All You Need Is Love 12-6 to NFC Least 3-15. A rule labeled "PLAYOFF LINE" runs under row 6, Return of T Mac, and row 2 reads "Bo Girds YOU" in red with a red bar, "82%", and 11-7.

## AT-28: Your season shows the schedule strip

App: pipeline, site
Then: The schedule strip shows a step path over weeks 10 to 14 against the playoff line, and one row per week with the opponent, the rank, and the record.
Files: `evidence/AT-28/375-dark.png`, `evidence/AT-28/375-light.png`, `evidence/AT-28/768-dark.png`, `evidence/AT-28/768-light.png`, `evidence/AT-28/1280-dark.png`, `evidence/AT-28/1280-light.png`, `evidence/AT-28/block-cpc-your_season.json.txt`, `evidence/AT-28/steps.json`
Observation: `block-cpc-your_season.json.txt` gives the `block` of Your season: `kind` "schedule", `playoff_teams` 6, and one row per week 10 to 14 with the opponent, the rank, and the record.
Observation of the shots: In all six shots the block "OPPONENTS BY STANDING" shows a dashed step path over Wk 10 to Wk 14 against a solid "PLAYOFF LINE", with filled dots above the line in weeks 10, 12, and 14 and open dots below it in weeks 11 and 13. Under it, five rows give the week, the opponent, the rank, and the record: The Blue Tent 5th 11-7, Maye d'force B with U 7th 10-8, London Cooking 3rd 11-7, NFC Least 12th 3-15, and Lil Fridge 4th 11-7.

## AT-29: Waiver targets shows the waiver list

App: api, site
Then: Each row shows the position, the NFL team, the projection, and the slot that the player fills, and the tapped row opens in place with the why.
Files: `evidence/AT-29/375-dark.png`, `evidence/AT-29/375-light.png`, `evidence/AT-29/768-dark.png`, `evidence/AT-29/768-light.png`, `evidence/AT-29/1280-dark.png`, `evidence/AT-29/1280-light.png`, `evidence/AT-29/steps.json`, `evidence/AT-29/stream.txt`
Observation: The stream (21:51:00 UTC) has a `waiver_list` block with 1 row: Devin Singletary (RB, NYG, 7.66), `slot` "FLEX2", `kind` "add", and a `why` list of 3 lines. Text follows. The second curl gives the same block.
Observation of the shots: In all six shots the list head reads "1 FREE AGENT WORTH A CLAIM", and its one row shows Devin Singletary, "RB · NYG · FLEX2 slot" with "FLEX2 slot" in red, and "7.7 proj". The row is open in place under itself, with the head "Worth a claim this week." and two bullets: "Projects 7.7 this week, over Audric Estime at 7.6 in your FLEX2 slot." and "36.4 projected points for the rest of the season."

## AT-30: How you stack up shows four slot rank bars

App: api, site
Then: The block shows exactly four rows, QB, RB, WR, and TE, each with a bar from the league middle and a rank such as "6th of 12". The header shows the roster grade and its read.
Files: `evidence/AT-30/375-dark.png`, `evidence/AT-30/375-light.png`, `evidence/AT-30/768-dark.png`, `evidence/AT-30/768-light.png`, `evidence/AT-30/1280-dark.png`, `evidence/AT-30/1280-light.png`, `evidence/AT-30/steps.json`, `evidence/AT-30/stream.txt`
Observation: The stream (21:52:39 UTC) has a `slot_ranks` block with four rows: QB 11th of 12, RB 2nd, WR 5th, and TE 5th. Its `grade` is "A" and its `read` is "Strong at RB. Soft at QB." The second curl gives the same block.
Observation of the shots: In all six shots the block shows exactly four rows, QB, RB, WR, and TE, each with a bar from a center line under "LEAGUE MIDDLE", between "WORSE" and "BETTER". QB has a grey bar to the left with "11th of 12", and RB, WR, and TE have red bars to the right with "2nd of 12", "5th of 12", and "5th of 12"; the header shows "A" and "Strong at RB. Soft at QB." under "as of today".

## AT-31: Weak spots shows the bye grid

App: api, site
Then: The bye grid shows his players against the next weeks, with a red dot for each starter on a bye in that week.
Files: `evidence/AT-31/375-dark.png`, `evidence/AT-31/375-light.png`, `evidence/AT-31/768-dark.png`, `evidence/AT-31/768-light.png`, `evidence/AT-31/1280-dark.png`, `evidence/AT-31/1280-light.png`, `evidence/AT-31/byes.txt`, `evidence/AT-31/steps.json`, `evidence/AT-31/stream.txt`
Observation: The stream (21:54:12 UTC) has a `bye_grid` block for weeks 10 to 14. Its starters with a bye in that window are Kyren Williams, Matthew Golden, and Blake Corum (week 11), Zay Flowers (week 13), and Trey McBride (week 14). `byes.txt` gives the same bye weeks from the Sleeper schedule: LAR 11, GB 11, BAL 13, ARI 14. The second curl gives the same block.
Observation of the shots: In all six shots the grid "BYES, WEEKS 10 TO 14" shows nine starter rows and six bench rows against columns 10 to 14, with a legend of a red dot for Starter and an open ring for Bench. Red dots sit at week 11 for Kyren Williams, Matthew Golden, and Blake Corum, at week 13 for Zay Flowers, and at week 14 for Trey McBride, and open rings sit for four bench players; in each shot the fixed foot sits over the Answer text below the grid.

## AT-32: Sell high shows the sell list

App: api, site
Then: Each row shows the player, his ranks, and the headline, and the tapped row opens in place with the bullets. A roster with no clear sell shows its plain line.
Files: `evidence/AT-32/375-dark.png`, `evidence/AT-32/375-light.png`, `evidence/AT-32/768-dark.png`, `evidence/AT-32/768-light.png`, `evidence/AT-32/1280-dark.png`, `evidence/AT-32/1280-light.png`, `evidence/AT-32/steps.json`, `evidence/AT-32/stream.txt`, `evidence/AT-32/vitest.txt`
Observation: The `sell-high` stream (21:55:42 UTC) has a `sell_list` block with 2 rows: Blake Corum (RB, LAR, RB19) and Matthew Golden (WR, GB, WR5), each with a headline and 3 bullets, and `empty` null. The second curl gives the same block. No roster of cpc or norcal had an empty sell list in this round, so `vitest.txt` runs the test "shows the plain line of a roster with no clear sell" and prints `Tests  1 passed | 22 skipped (23)`.
Observation of the shots: At 375, 768, and 1280, light and dark, the "PLAYERS TO SELL" card has two rows: Blake Corum "RB · LAR · Season RB19" and Matthew Golden "WR · GB · Season WR5". Each row has a photo and a one-line headline. The Corum row is open in place, with an up chevron and a gray panel of three bullets: two red dots and one gray dot. The Golden row is closed, with a down chevron. No shot shows the plain line of an empty roster. At 375, the fixed foot sits at the bottom edge of the card and hides part of the "Open your manager page" link; this is the capture, not an overlap in the layout.

## AT-33: Trade ideas shows one card with a row per offer

App: api, site
Then: The Answer shows one trade card with one row per offer, and the first offer is open as the full card.
Files: `evidence/AT-33/375-dark.png`, `evidence/AT-33/375-light.png`, `evidence/AT-33/768-dark.png`, `evidence/AT-33/768-light.png`, `evidence/AT-33/1280-dark.png`, `evidence/AT-33/1280-light.png`, `evidence/AT-33/steps.json`, `evidence/AT-33/stream.txt`
Observation: The `trade-ideas` stream (21:57:46 UTC) has a `trade` block with 2 offers, both with Maye d'force B with U: Parker Washington for Drake Maye, and Zay Flowers for Drake Maye. Each offer has its sides with the rest-of-season points, a case, and bullets. The document also has 3 near offers and `empty` null. The second curl gives the same card.
Observation of the shots: Each of the six shots shows one card for "Trade ideas". The first offer, "WITH MAYE D'FORCE B WITH U", is open, with "YOU GET Drake Maye QB · NE 87.5" on a full red bar and "Parker Washington WR · JAX 65.2" on a gray bar. Under it are a "REST OF SEASON" tug bar of 87.5 red against 65.2 gray, two "FOR" bullets with red triangles, and "Check this trade". The head of the second offer, "Flowers has slumped, so you cash him in…", is closed and sits mostly under the fixed foot; this is the capture. Below the foot are three more rows of "You give … and get Drake Maye", each with a gray-ruled note and "Check this trade", then "Build a trade on the Trade page".

## AT-34: The Lean closes the trade card

App: api, site
Then: The trade card shows the two sides with a bar of the projected points for the rest of the season for each player, a tug bar of the two totals, and it closes with the Lean of the Advisor. It shows no edge line in points. The case and the bullets open in place.
Files: `evidence/AT-34/ask.txt`, `evidence/AT-34/closed-375-dark.png`, `evidence/AT-34/closed-375-light.png`, `evidence/AT-34/closed-768-dark.png`, `evidence/AT-34/closed-768-light.png`, `evidence/AT-34/closed-1280-dark.png`, `evidence/AT-34/closed-1280-light.png`, `evidence/AT-34/open-375-dark.png`, `evidence/AT-34/open-375-light.png`, `evidence/AT-34/open-768-dark.png`, `evidence/AT-34/open-768-light.png`, `evidence/AT-34/open-1280-dark.png`, `evidence/AT-34/open-1280-light.png`, `evidence/AT-34/steps.json`, `evidence/AT-34/stream.txt`
Observation: The `ask` route sends the question to trade_check. The `trade-check` stream (22:19:51 UTC) has a `trade` block with one offer, Kyren Williams for Amon-Ra St. Brown with Teehee. Its sides give the rest-of-season points (St. Brown 81.39, Williams 57.83) and the totals, with `lean` "Lean yes", a `case`, and 3 bullets. The block has no edge field. The second curl gives the same card.
Observation of the shots: The closed shots show "YOU GET Amon-Ra St. Brown WR · DET 81.4" on a full red bar and "TEEHEE GETS Kyren Williams RB · LAR 57.8" on a shorter gray bar. Under them are a "REST OF SEASON" tug bar of 81.4 red against 57.8 gray, a closed "Why" row, a red "Lean yes.", and "Open it on the Trade page". No line of a points edge is visible. In the open shots, "Why" shows a paragraph of the case and three bullets under FOR (red triangle), AGAINST (black triangle), and EVEN (dash). "Lean yes." stays last in the card. In the open shots, the fixed foot covers the FOR bullet at 375 and the AGAINST bullet at 768 and 1280; this is the capture.

## AT-35: A free answer shows the transaction feed

App: api, site
Then: The free answer shows the transaction feed: a strip of the moves per day, one row per move newest first with a dot for its kind, and a trade row that shows what each side got.
Files: `evidence/AT-35/375-dark.png`, `evidence/AT-35/375-light.png`, `evidence/AT-35/768-dark.png`, `evidence/AT-35/768-light.png`, `evidence/AT-35/1280-dark.png`, `evidence/AT-35/1280-light.png`, `evidence/AT-35/ask.txt`, `evidence/AT-35/steps.json`, `evidence/AT-35/stream.txt`
Observation: Recorded at head 83d4afeb, with NFC Least (cpc roster 4) as Your team, because it is in a week 9 trade. The `ask` route (02:12:58 UTC) gives `route` "free". The free answer stream of "What moves happened in week 9?" (02:13:02 UTC) has a `feed` block "Week 9 moves" with the moves per day over 7 days (Wed 9, Thu 0, Fri 4, Sat 2, Sun 2, Mon 0, Tue 4), 20 rows newest first, and `more` 1. Two rows have kind `trade`, each with the players that each side got: Puka Deez... and behold the lamb (Sun Nov 8), and NFC Least and Return of T Mac (Fri Nov 6). The second curl gives the same block. A free answer is not kept, so the page writes its own text above the same feed.
Observation of the shots: Head 83d4afeb, NFC Least as Your team. Every shot shows the question "What moves happened in week 9?", the "WEEK 9 MOVES" strip with a black "Trade" dot and a gray "Free agent" dot in the legend, and the rows newest first from Tue down to Wed, then "1 more move this week" and "Checked". Two rows have the larger black dot (white in dark mode) and show what each side got. The Fri trade row reads "NFC Least YOU got" in red, with Tetairoa McMillan, Makai Lemon, Seth McGowan, and Chase Brown, and "Return of T Mac got" in black or white, with Rome Odunze, CeeDee Lamb, and Jordan Mason. The Fri free agent row "NFC Least YOU" (- Tyjae Spears) is red too, and the names of the other teams are black or white. At 1280 the strip shows all seven day labels, Wed 9 to Tue 4. At 375 and 768 the fixed top band covers the lower part of the strip, so its counts show and its day labels do not. The fixed foot covers the rows from Fri to Wed near the middle of each shot; this is the capture.

## AT-36: The text block renders the allowed marks

App: site
Then: The bold, the italic, and both lists render as marks.
Files: `evidence/AT-36/375-light.png`, `evidence/AT-36/steps.json`, `evidence/AT-36/vitest.txt`
Observation: `vitest.txt` runs `renders bold, italic, a bullet list, and a numbered list as marks, live and kept (AT-36)` at 2adcc0c4 and prints `Tests  1 passed | 24 skipped (25)`. The 375 px shot is of the Answer of Position leaders and recent trades.
Observation of the shots: The 375-light shot of "Position leaders and recent trades" shows a bullet list of five rows with bold position labels: "QB Jordan Love…", "RB Kenneth Walker III…", "WR CeeDee Lamb…", "TE Brock Bowers…", and "DEF San Francisco 49ers…". After the list are a plain paragraph and "Read the full report". The shot shows no italic text and no numbered list. `vitest.txt` prints the AT-36 test with a check mark and `Tests 1 passed | 24 skipped (25)`.

## AT-37: The text block shows blocked marks as plain text

App: site
Then: Each one shows as plain text. The page has no `a`, `img`, heading, or raw HTML element from the text.
Files: `evidence/AT-37/output.txt`
Observation: `output.txt` (22:53 UTC on 2adcc0c4) runs `shows a link, an image, a heading, and raw HTML as plain text, with no such element (AT-37)` and prints `Tests  1 passed | 24 skipped (25)`.

## AT-38: Every block takes the Ledger look

App: site
Then: Each block renders with no overflow and no overlap. Red marks Your team or the side that wins, gray marks the rest, and the up and down colors of the site mark a move. At 1280 px the blocks stack in the column of about 560 px.
Files: `evidence/AT-1/*.png`, `evidence/AT-16/*.png`, `evidence/AT-19/*.png`, `evidence/AT-22/*.png`, `evidence/AT-23/*.png`, `evidence/AT-24/*.png`, `evidence/AT-25/*.png`, `evidence/AT-26/*.png`, `evidence/AT-27/*.png`, `evidence/AT-28/*.png`, `evidence/AT-29/*.png`, `evidence/AT-30/*.png`, `evidence/AT-31/*.png`, `evidence/AT-32/*.png`, `evidence/AT-33/*.png`, `evidence/AT-34/*.png`, `evidence/AT-35/*.png`
Observation: The test has no step list of its own. The files are the shots of the blocks of AT-1, AT-16, AT-19, and AT-22 to AT-35. The shots of AT-35 come from head 83d4afeb, with NFC Least as Your team in the week 9 feed.
Observation of the shots: At 1280 light, every named block sits in a card from x 376 to 903. The card is 528 px wide, inside a column from x 360 to 919, which is 560 px. The column has a gutter of 16 px on each side of the card, and the page has a margin of 360 px on each side of the column. I measured these values from the foot rule at y 765 and the card border in the pixels. Red marks Bo Girds and the leading side: "Bo Girds YOU" in rankings and the playoff race, the K. Williams side in the comparison, the Bears side, the "YOU" tick in the recap, the winning slot bars, the "YOU GET" bars, and the RB, WR, and TE bars above the middle. Gray marks the other side. Red also marks other things: starter byes in the bye grid, "FLEX2 slot", and the red bullet dots of the sell list. Blue (▲, "+14.23") and coral (▼) mark the moves in the rank mover list. Norcal (AT-23) uses an orange accent, and that accent is amber in dark mode. In the 375-dark shots, long names end in an ellipsis ("P. Washingt…", "C. Rodriguez …", "All You Need Is Lo…", "Maye d'force …"), and no text runs outside a card. In the AT-35 shots of head 83d4afeb, the feed card at 1280 light also spans x 376 to 903, and red marks Your side: "NFC Least YOU got" in the Fri trade row and "NFC Least YOU" in the Fri free agent row, while the other teams are black. The fixed foot sits over the middle of the long Answers in AT-1, AT-24, AT-25, AT-31, AT-33, AT-34, and AT-35; this is the capture.

## AT-39: The blocks honor reduced motion

App: site
Then: The block and the row show at once, with no slide, no blur, and no roll of digits.
Files: `evidence/AT-39/output.txt`
Observation: `output.txt` (02:14:50 UTC on 83d4afeb) runs the 23 tests of `reduced-motion-blocks.test.tsx` with the verbose reporter. Each of the 17 block kinds shows at once with no slide and no blur. A row of the lineup, waiver, sell, and trade blocks opens at once. The test "does not roll the digits of the lineup total with reduced motion, when the toggle changes the total" is in the list. It prints `Tests  23 passed (23)`.

## AT-40: `topics.json` carries one block for six league Topics

App: pipeline
Then: `schema_version` is 2. Week recap, Your last matchup, Your next matchup, Power rankings, Playoff race, and Your season each have a `block` with a `kind`. Position leaders and recent trades has no `block`.
Files: `evidence/AT-40/blocks-cpc-bo-girds.json.txt`, `evidence/AT-40/blocks-norcal-bo-girds.json.txt`, `evidence/AT-40/output.txt`, `evidence/AT-40/pytest.txt`
Observation: `output.txt` (22:54 UTC on 2adcc0c4): the rebuild of `topics.json` from the saved raw week 9 ends with exit 0 for both clients, and both files have `schema_version` 2. In each, all 12 Answers of Week recap, Your last matchup, Your next matchup, Power rankings, Playoff race, and Your season have a `block` with a `kind` (recap, matchup, matchup, rank_movers, ladder, schedule). Position leaders and recent trades has no `block` and an empty `stats` list in all 12 Answers. The block files give `block` null for leaders_trades of Bo Girds in both clients. `pytest.txt`: `13 passed`.

## AT-41: A version 1 `topics.json` still renders

App: site
Then: Each league Topic Answer renders as before this spec, with its stats and rows.
Files: `evidence/AT-41/output.txt`
Observation: `output.txt` (22:53 UTC on 2adcc0c4) runs `renders each league Topic Answer as before, with its stats, rows, and text, and no block (AT-41)` and prints `Tests  1 passed | 26 skipped (27)`.

## AT-42: The Suggestions take one row

App: site
Then: The row is one line of about 48 px, with "More" first and each chip showing only a short name of its Topic.
Files: `evidence/AT-42/empty-375-dark.png`, `evidence/AT-42/empty-375-light.png`, `evidence/AT-42/one-answer-375-dark.png`, `evidence/AT-42/one-answer-375-light.png`, `evidence/AT-42/row-height.txt`, `evidence/AT-42/steps.txt`
Observation: `row-height.txt` (22:13 to 22:14 UTC) reads the row after the suggestions response, once the count of buttons stays the same for 1 s. In light and dark, with an empty Thread and with one Answer, the row holds 4 buttons, More first, then the chips with the text "Holes", "Roster", and "Waivers". Each button is 44.0 px tall, and all are at one top. The aria-label of each chip holds the full Topic name and the fact, such as "Weak spots: QB ranks 11th of 12". The row box is 52.0 px tall, with a padding of 4 px at the top and the bottom and a margin of -4 px at the top and the bottom, so its layout height is 44.0 px. The shots come from the same pages as the measure.
Observation of the shots: The empty shots show "GOOD AFTERNOON · WEEK 9", "Ask about Bo Girds", and one row of four buttons, More first, then Holes, Roster, Waivers, above the ask box. The one-answer shots show a Week recap card and the same one row of four buttons in the fixed foot; in all 4 shots the buttons are about 44 px tall at one top.

## AT-43: A first tap shows the fact, and a second tap opens the Topic

App: site
Then: The first tap shows a full-width strip under the row with the whole fact and "Open →". The second tap opens Start or sit.
Files: `evidence/AT-43/first-tap-375-light.png`, `evidence/AT-43/second-tap-375-light.png`, `evidence/AT-43/steps.json`, `evidence/AT-43/suggestions.txt`
Observation: `suggestions.txt` (22:58:33 UTC) gives Unsolicited Dak Picks (cpc roster 11) the picks weak_spots, stack_up, and start_sit, with start_sit in `urgent`, its lift 0.89, and its fact "2 can't play". The step list picks that team, waits for the Start or sit chip, taps it, and waits until it is expanded before the shot `first-tap`. Then it taps the chip again and waits for the Start or sit Answer before the shot `second-tap`.
Observation of the shots: `first-tap` shows the row More, Holes, Roster, and Start/sit, with the Start/sit chip pressed and a full-width strip under the row that reads "Start or sit 2 can't play" and "Open →". `second-tap` shows the Start or sit Answer of Unsolicited Dak Picks: the Week 10 lineup at 98.1, the open Q row of A.J. Brown with its Pivot, the Q tag on George Pickens, and "Can't play: J. Jacobs Out (finger)".

## AT-44: A tap on another chip changes the strip

App: site
Then: The strip shows the fact of the other chip, and the Topic does not open.
Files: `evidence/AT-44/other-chip-375-light.png`, `evidence/AT-44/steps.json`, `evidence/AT-44/strip-375-light.png`
Observation: The step list waits for the Weak spots chip, taps it, and waits until it is expanded before the shot `strip`. Then it taps the How you stack up chip and waits until that chip is expanded before the shot `other-chip`.
Observation of the shots: The strip shot shows the Holes chip filled and the strip "Weak spots QB ranks 11th of 12 · Open →". The other-chip shot shows the Roster chip filled instead and the strip "How you stack up Grade A, QB ranks 11th of 12 · Open →", and the page is still the front door with no Answer.

## AT-45: The header menu opens the sheet of pages

App: site
Then: The front door has no dock. The sheet drops from under the header with five page rows, each with an icon, a name, and its note: "Ask about your team", "Scores and recaps", "The league, ranked", "Grades and records", and "Check a trade". The current page has a check, and the button shows an X.
Files: `evidence/AT-45/375-dark.png`, `evidence/AT-45/375-light.png`, `evidence/AT-45/768-dark.png`, `evidence/AT-45/768-light.png`, `evidence/AT-45/steps.json`
Observation: The step list picks Bo Girds, taps the menu button `Open the menu`, and waits for the `Pages` sheet before the shot, at 375 and 768 px.
Observation of the shots: At 375 and 768, light and dark, a sheet hangs from under the header. It has five rows, each with an icon tile, a name, and a note: Home "Ask about your team", Week 9 "Scores and recaps", Power Rankings "The league, ranked", Managers "Grades and records", and Trade Analyzer "Check a trade". The Home row has a gray fill and a red check, and the header button shows a red X. The page under the sheet is dimmed, and no dock shows at the bottom edge.

## AT-46: The sheet closes four ways and returns the focus

App: site
Then: Each way closes the sheet. The focus goes to the sheet on open and back to the menu button on close.
Files: `evidence/AT-46/output.txt`
Observation: `output.txt` (22:53 UTC on 2adcc0c4) runs the six tests of "The header sheet closes four ways (AT-46)": the X, a tap on the dimmed page, Escape, a swipe up, a Tab out of the sheet, and a short drag that keeps it open. The test names say that the Tab case leaves the focus where it went. It prints `Tests  6 passed | 29 skipped (35)`. The second run gives "moves the focus to the sheet on open": `Tests  1 passed | 34 skipped (35)`.

## AT-47: The week moves into the sheet

App: site
Then: The header has no week pill. The sheet has a week row that opens the latest report, and "Past weeks" under it.
Files: `evidence/AT-47/header-375-dark.png`, `evidence/AT-47/header-375-light.png`, `evidence/AT-47/sheet-375-dark.png`, `evidence/AT-47/sheet-375-light.png`, `evidence/AT-47/steps.json`, `evidence/AT-47/url-375-dark.txt`, `evidence/AT-47/url-375-light.txt`, `evidence/AT-47/week-375-dark.png`, `evidence/AT-47/week-375-light.png`
Observation: The step list takes the header at 375 px, then opens the menu sheet and takes it. Then it taps the week row of the sheet, waits for the URL to change, and takes the shot `week`. `url-375-light.txt` and `url-375-dark.txt` give `http://127.0.0.1:4173/2026/week-09/`.
Observation of the shots: The header shots show the logo, the theme button, and the menu button, with no week pill, and the sheet shots show a "Week 9 / Scores and recaps" row and a "Past weeks" row under it. After a tap on the week row, both url files give `http://127.0.0.1:4173/2026/week-09/`, and the week shots show the week 9 report page with the hero "London Cooking by 4.75".

## AT-48: The foot is one flush surface

App: site
Then: The Suggestions row and the ask box sit on one surface that touches the bottom edge, with no gap under it.
Files: `evidence/AT-48/375-dark.png`, `evidence/AT-48/375-light.png`, `evidence/AT-48/steps.json`
Observation: The step list opens Week recap from "More", so one Answer is in the Thread, then scrolls to the end before the shot at 375 px.
Observation of the shots: At 375, light and dark, the Week recap card sits above a foot. The foot has the Suggestions row (More, Next game, Playoffs, Result) and the ask box. In the pixels, the foot starts with a 1 px rule at y 781. From y 782 down to the last row, y 939, the foot has the color of the page (244 in light, 20 in dark), with no band and no gap at the bottom edge. A blurred patch shows next to "Clear" in the team row, and the header sits about 40 px below the top of the shot.

## AT-49: The other pages keep the dock and the week pill

App: site
Then: Each page shows the dock and the week pill as before this spec.
Files: `evidence/AT-49/rankings-375-dark.png`, `evidence/AT-49/rankings-375-light.png`, `evidence/AT-49/steps.json`, `evidence/AT-49/week-375-dark.png`, `evidence/AT-49/week-375-light.png`
Observation: The step list opens the week 9 report, takes a shot, then taps the rankings link of the dock, waits for the URL to change, and takes a second shot, at 375 px.
Observation of the shots: The week 9 report at 375 shows a "WK 09" pill in the header. The rankings page at 375 shows a "WK 09" pill in the header. On both pages, a dock with Home, Week 9, Rankings, Managers, and Trade shows near the bottom of the first screen. The tab of the open page has a gray fill and a red mark: Week 9 on the report, and Rankings on the rankings page. In both full-page shots, the dock sits once at its screen place over the body text; this is the capture.

## AT-50: The desktop header keeps the inline pages

App: site
Then: The header shows the pages inline and no menu button.
Files: `evidence/AT-50/1280-dark.png`, `evidence/AT-50/1280-light.png`, `evidence/AT-50/steps.json`
Observation: The step list picks Bo Girds on the front door and takes the shot at 1280 px, light and dark.
Observation of the shots: At 1280, light and dark, the header shows the logo, "CORNERSTONE FANTASY FOOTBALL LEAGUE", and the pages inline. The pages are Home in a gray pill, then Week 9, Power Rankings, Managers, and Trade Analyzer. The theme button is at the right. No menu button shows.

## AT-51: The passphrase box stays above the keyboard

App: site
Then: The whole passphrase box is above the foot and in view.
Files: `evidence/AT-51/focus-then-resize-393-light.png`, `evidence/AT-51/positions-focus-then-resize.txt`, `evidence/AT-51/positions-resize-then-tap.txt`, `evidence/AT-51/resize-then-tap-393-light.png`, `evidence/AT-51/steps.txt`
Observation: Instrument: a Playwright WebKit run at 393 x 852 that sets a keyboard height of 336 px, because Playwright cannot open the iOS keyboard (`steps.txt`). It ran near 22:38 UTC on the cpc export of 2adcc0c4. With the box focused first and the viewport shrunk to 516 px after, the box spans 315 to 369 px and the foot starts at 381 px. With the viewport shrunk first and the box tapped after, the box spans 315 to 369 px and the foot starts at 381 px. In both files the box has the focus and the page has `data-keyboard`.
Observation of the shots: The two WebKit shots at 393 px (1179 × 1548 at 3x, so a 516 px viewport) look the same. "How did my bench do?" sits above the passphrase card, and its "League passphrase" box has a dark focus border at y 945 to 1107, which is 315 to 369 px. The foot rule is at about y 1145, which is about 381 px. The Suggestions row and the ask box sit below the rule. In both shots, the faded text "bench in a swap that would have flipped the result." shows behind the sticky "Bo Girds / Clear" row at the top.

## AT-52: The roster grade keeps four slots

App: pipeline
Then: Each grade in `managers.json` has slots for QB, RB, WR, and TE only, with no DEF and no FLEX.
Files: `evidence/AT-52/output.txt`, `evidence/AT-52/pytest.txt`
Observation: `output.txt` (22:54 UTC on 2adcc0c4): each of the 12 grades in `clients/cpc/published/2026/managers.json` (through week 9, from the Week 9 publish 7053c79b) has the slots QB, RB, WR, TE, with no DEF and no FLEX. `pytest.txt` of `test_manager_grade.py`: `50 passed`.

## AT-53: Start or sit fetches no news

App: api
Then: The API calls no host other than Sleeper, ESPN, TypeSafe, and Anthropic.
Files: `evidence/AT-53/hosts.txt`, `evidence/AT-53/pytest.txt`
Observation: `hosts.txt` is the log of one Start or sit request of Bo Girds to a second local API on port 8081 at 2adcc0c4, with no other traffic. Its HTTP request lines go to api.sleeper.app (22 GET), sleeper.com/graphql (1 POST, the `scores` query), api.typesafe.ai (4 POST, Jev), and api.anthropic.com (1 POST), and to no other host. The one pydantic.dev URL is in a startup banner line, not a request. That Answer ended as checked. `pytest.txt`: `test_start_sit_calls_only_sleeper_and_the_kickoff_sources` gives `1 passed`.
