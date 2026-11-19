# Season sim: evidence

Spec: `.scratch/season-sim/PRD.md`. Acceptance tests: `.scratch/season-sim/ACCEPTANCE.md`.
Built from: `42644789` for the pipeline tests, the API tests, and the first site round, and `b5de9120` for AT-45 to AT-49 and AT-51 to AT-59, on 2026-11-18. Fix group d (`d78d6e74` to `b5de9120`) changed only the Sim tile, the team pick, the Sim chapter height, and the Announcement team read. AT-22 and AT-23 ran on Fly from `dbea219f`. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 27 min for 44 site tests, then 6 min for 14 site tests again after fix group d.

The site tests ran with Playwright WebKit scripts, not the evidence runner, because the runner has no WebKit and no four sizes. Each folder has a `steps.txt`.

## AT-1: The weekly build writes a sim file in the week folder

App: pipeline
Then: `clients/cpc/published/2026/week-10/sim.json` exists with `runs` 10000, 12 `teams`, 200 runs in `sample`, and 12 entries in `pages`.
Files: `evidence/AT-1/output.txt`
Observation: A fresh `make sim CLIENT=cpc WEEK=10` at 42644789 writes a build file, and `cmp` shows that it equals the committed `published/2026/week-10/sim.json` byte for byte. The file has `runs` 10000, 12 `teams`, 200 `sample` runs, and 12 `pages`.

## AT-2: The rankings odds come from the sim

App: pipeline
Then: the playoff odds of each of the 12 teams in `rankings.json` for week 10 equal the playoff odds of that team in `week-10/sim.json`.
Files: `evidence/AT-2/output.txt`, `evidence/AT-2/table.md`, `evidence/AT-2/facts_and_rankings.py`, `evidence/AT-2/at2_table.py`
Observation: A script ran the facts step (`make_bundle`) and the rankings step (`_write_rankings`) of `run_build` on the saved raw week, with no Claude writer. The table shows the same playoff odds and bye odds for all 12 teams in week 10 of the fresh `rankings.json` and in `week-10/sim.json`.

## AT-3: The facts quote the odds of the sim

App: pipeline
Then: each playoff odds number in the facts of week 10 equals the number of that team in `week-10/sim.json`.
Files: `evidence/AT-3/output.txt`, `evidence/AT-3/odds-facts.json`, `evidence/AT-3/at3_facts.py`
Observation: The same facts-step run gives 12 `ODDS.` facts and 2 `SW.` facts. Each of the 28 numbers in them equals the number of that team in `sim.json` (`teams` or `swings`). Two `SW.` facts say "stay near 1% either way" with no win or loss number, and the file has 1 and 1 there.

## AT-4: The odds of past weeks stay

App: pipeline
Then: no odds value of weeks 1 to 9 changes.
Files: `evidence/AT-4/output.txt`, `evidence/AT-4/at4_odds.py`
Observation: `git diff origin/main` of the published `rankings.json` is empty, and origin/main 33da78a4 is the merge base. A row-by-row check of weeks 1 to 9 shows 0 changed odds values, in the published file and in the fresh build file of the AT-2 run; the only changes of the build file are week 10 odds.

## AT-5: The old odds engine is gone

App: pipeline
Then: `packages/rankings/python/src/rankings/odds.py` and its parity test do not exist, and no module imports `rankings.odds`.
Files: `evidence/AT-5/output.txt`
Observation: `odds.py` and `apps/pipeline/tests/test_odds.py` are not in the tree at HEAD, and `git diff --stat` shows both deleted against origin/main. The test on main that held the sim within 2 points of the old odds is gone, and `git grep` finds no `.py` or `.toml` import of `rankings.odds`; other `odds.py` hits are a layer-test file name, script test paths, and markdown notes.

## AT-6: The ladder names the wins Your team needs

App: pipeline
Then: the ladder lists each count of more wins with its playoff odds and its chance, and the sentence names the smallest count with odds of 90 % or more.
Files: `evidence/AT-6/output.txt`
Observation: The ladder of Bo Girds lists 0 to 8 more wins, each with `playoff` and `chance`. The smallest count with odds of 90 % or more is 5, at 99 %, and the sentence is "Win 5 of the 8 left and you're in."

## AT-7: Week 11 has four results with the median game

App: pipeline
Then: the opponent is Maye d'force B with U, and four results each give odds after, a chance, and wins added of 2, 1, 1, and 0.
Files: `evidence/AT-7/output.txt`
Observation: The week 11 block of Bo Girds names opponent 9, Maye d'force B with U. Its four results have `wins_added` 2, 1, 1, and 0, each with odds after (86, 65, 67, 41) and a chance (24.1, 5.2, 19.7, 51.0).

## AT-8: Week 11 has two results with no median game

App: pipeline
Then: the opponent is The Mean Machine, and two results give odds after a win and after a loss.
Files: `evidence/AT-8/output.txt`
Observation: A fresh `make sim CLIENT=norcal WEEK=10` equals the committed norcal file byte for byte, and the file has `median_game` false. The week 11 block of Bo Girds (roster 7) names The Mean Machine and has two results: a win at 67 % and a loss at 30 %.

## AT-9: The root-for rows follow the rules of the spec

App: pipeline
Then: there are at most 3 rows, each lifts the odds after a loss by 1 point or more, each number is whole, the rows rank by the lift, and each reason is one of the five reasons of the spec.
Files: `evidence/AT-9/output.txt`
Observation: The odds after a loss are 48 %, and there are 3 rows at 51, 50, and 50 %, so the lifts are 3, 2, and 2 points, each a whole number. The reasons are "1 win ahead of you" and "1 win behind you", and across all 12 pages each reason is one of the five reasons of the PRD.

## AT-10: A small sample shows "about"

App: pipeline
Then: each result whose chance times `effective_runs` is under 400 has the "about" flag, and each other result does not.
Files: `evidence/AT-10/output.txt`, `evidence/AT-10/check_about.py`
Observation: The 192 week results of the 12 pages all have chance times 10000 at 400 or more, and none has the flag, so no week result falls under 400. The script also checks the 108 ladder rows: 22 are under 400 and each has the flag, and 86 are at 400 or more and none has it.

## AT-11: A set result agrees with an exact reference

App: pipeline
Then: the playoff odds of Bo Girds are within 1.5 points of an exact rejection reference on the same inputs.
Files: `evidence/AT-11/output.txt`
Observation: The pytest test prints the weighted odds 42 at 9170 effective runs and the rejection reference 42.21 from 31105 kept runs. The gap is 0.21 points.

## AT-12: The same set results give the same numbers

App: pipeline
Then: the two page blocks are equal byte for byte.
Files: `evidence/AT-12/output.txt`, `evidence/AT-12/page-block.json`
Observation: The pytest test prints the same SHA-256 for two dumps of the sim result with a win above the median in week 11. Two real posts of the same What-if to the local API give `page` blocks with one SHA-256, and `cmp` shows them equal byte for byte.

## AT-13: An injury does not change the level of a team

App: pipeline
Then: the level mean of each team equals its season average shrunk toward the league average with 5 weeks of weight, with no injury term.
Files: `evidence/AT-13/output.txt`, `evidence/AT-13/level_means.py`
Observation: The script works out (own points + 5 x league average) / (games + 5) from the saved `matchups.json` of weeks 1 to 10. All 12 values match `parameters.level_mean` of the file, and the largest gap is under 0.00001. The parameters have no injury key, and the sim source says the level has no injury term.

## AT-14: The What-if answers with no passphrase

App: api
Then: the answer is 200 with `schema_version`, `season`, `week`, `runs`, `effective_runs`, `you`, `set`, `teams`, `sample`, and `page`.
Files: `evidence/AT-14/output.txt`, `evidence/AT-14/answer-page.json`
Observation: A real `curl` post with no passphrase header to the local API at 42644789 gets 200. The answer has each named key, plus `sample_weights`.

## AT-15: A What-if with no set result equals the file

App: api
Then: the `page` of the answer equals the page of Bo Girds in `week-10/sim.json`.
Files: `evidence/AT-15/output.txt`, `evidence/AT-15/answer-page.json`, `evidence/AT-15/file-page.json`
Observation: A real post of `{"you": 6}` gets 200 with `effective_runs` 10000. `diff -u` of the answer `page` and `pages["6"]` of the file is empty, and both have one SHA-256.

## AT-16: The What-if never calls Sleeper

App: api
Then: the answer is 200, and the log shows no request to Sleeper.
Files: `evidence/AT-16/output.txt`
Observation: A second local API ran with each outbound request sent to a dead proxy, and a real post got 200. Its log lines show only the What-if run and the access line, with 0 Sleeper lines; a control call to the analyzer route of that process got 500 with `ConnectError`, so the block was live. The pytest test with each Sleeper DNS lookup blocked also shows 200 and no Sleeper host tried.

## AT-17: The What-if has its own rate limit

App: api
Then: the call past the limit gets 429 with a retry-after, and a call to `/health` and to the analyzer from that address still answers.
Files: `evidence/AT-17/output.txt`
Observation: 31 real What-if posts from 127.0.0.1 within one second got 422 for calls 1 to 30 and 429 for call 31. The cheap posts set a result for week 3, and the limit counts them. A valid post then got 429 with `retry-after: 59`, and `/health` got 200 and the analyzer `/clients/cpc/teams` got 200 from that address.

## AT-18: The What-if answer is gzip

App: api
Then: the answer has `Content-Encoding: gzip`, and its size is under 60 KB.
Files: `evidence/AT-18/output.txt`
Observation: A real post with `Accept-Encoding: gzip` got 200 with `content-encoding: gzip` and 37087 bytes on the wire. The body unzips to 139274 bytes of JSON for week 10.

## AT-19: A cancelled call stops its work

App: api
Then: the log shows that the sim stopped before it ran all 10,000 runs.
Files: `evidence/AT-19/output.txt`
Observation: A real `curl` post with `--max-time 0.1` went away after 108 ms. The server log then shows "What-if of cpc stopped after 250 of 10000 runs: the client went away".

## AT-20: A bad set result gets 422

App: api
Then: the answer is 422 with a message that names the week.
Files: `evidence/AT-20/output.txt`
Observation: A real post with a set result for week 3 got `422 Unprocessable Entity`. The body is `{"detail":"week 3 is not a week left of the sim"}`.

## AT-21: The API machine stays the same size

App: api
Then: the machine is `shared-cpu-1x` with 1 GB, as on `main`.
Files: `evidence/AT-21/output.txt`
Observation: `git diff origin/main -- apps/api/fly.toml` is empty. The `[[vm]]` block on the branch and on origin/main is `size = "shared-cpu-1x"` and `memory = "1gb"`.

## AT-22: A What-if on Fly answers in time

App: api
Then: the median time is 2.5 s or less.
Files: `evidence/AT-22/output.txt`, `evidence/AT-22/idle.txt`, `evidence/AT-22/idle-start.txt`, `evidence/AT-22/after-deploy.txt`, `evidence/AT-22/deploy-end.txt`, `evidence/AT-22/deploy-tail.txt`
Observation: Release v62 deployed from dbea219f at 02:35 to 02:36 UTC on 2026-11-19, and no What-if call ran from 02:36:19 to 02:46:55 UTC. The AT-62 check loaded the built home pages at about 02:39 UTC, which may make small API calls such as the egg board, but no What-if call. The 10 calls from 02:46:55 UTC each got 200, with times from 1.55 s to 1.90 s and a median of 1.73 s.

## AT-23: The time just after a deploy is on record

App: api
Then: each call answers 200, and each time is on record for Brian.
Files: `evidence/AT-23/output.txt`, `evidence/AT-23/after-deploy.txt`, `evidence/AT-23/deploy-end.txt`, `evidence/AT-23/deploy-tail.txt`, `evidence/AT-23/idle.txt`, `evidence/AT-23/idle-start.txt`
Observation: Release v62 from dbea219f finished its deploy at 02:36:00 UTC on 2026-11-19, and the 10 calls ran one at a time from 02:36:00 to 02:36:19 UTC. Each of the 10 calls got 200, with times from 1.69 s to 1.89 s and a median of 1.79 s.

## AT-24: The page opens on Your team

App: site
Then: the header shows the avatar of Bo Girds, "Bo Girds", 11-9, 4 weeks left, and the playoff odds of the file.
Files: `evidence/AT-24/overlap.txt`, `evidence/AT-24/page-1080x740-dark.png`, `evidence/AT-24/page-1080x740-light.png`, `evidence/AT-24/page-1280x800-dark.png`, `evidence/AT-24/page-1280x800-light.png`, `evidence/AT-24/page-390x660-dark.png`, `evidence/AT-24/page-390x660-light.png`, `evidence/AT-24/page-810x980-dark.png`, `evidence/AT-24/page-810x980-light.png`, `evidence/AT-24/readings.txt`, `evidence/AT-24/steps.txt`
Observation: The header shows the avatar of Bo Girds (`/2026/week-10/avatars/6.jpg`), "Bo Girds", "11-9 · 4 weeks left", and 58% playoff odds, which is `playoff` 58 of page 6 in `week-10/sim.json`. The overlap check shows no issue in the 8 shots.

## AT-25: The sentence opens the ladder

App: site
Then: the ladder opens with each count of more wins, its odds, and its chance, as in the file.
Files: `evidence/AT-25/ladder-open-1080x740-dark.png`, `evidence/AT-25/ladder-open-1080x740-light.png`, `evidence/AT-25/ladder-open-1280x800-dark.png`, `evidence/AT-25/ladder-open-1280x800-light.png`, `evidence/AT-25/ladder-open-390x660-dark.png`, `evidence/AT-25/ladder-open-390x660-light.png`, `evidence/AT-25/ladder-open-810x980-dark.png`, `evidence/AT-25/ladder-open-810x980-light.png`, `evidence/AT-25/overlap.txt`, `evidence/AT-25/readings.txt`, `evidence/AT-25/steps.txt`
Observation: The open sheet "Wins left and your odds" lists 8 of 8 down to 0 of 8, each with its odds and chance (for example 4 of 8, 75%, 22.1%), and these match the ladder of page 6 in the file. The overlap check shows no issue in the 8 view shots.

## AT-26: The week switch goes from week 11 to Playoffs

App: site
Then: the items are Wk 11, Wk 12, Wk 13, Wk 14, and Playoffs, and each opens its own week page.
Files: `evidence/AT-26/overlap.txt`, `evidence/AT-26/playoffs-1080x740-dark.png`, `evidence/AT-26/playoffs-1080x740-light.png`, `evidence/AT-26/playoffs-1280x800-dark.png`, `evidence/AT-26/playoffs-1280x800-light.png`, `evidence/AT-26/playoffs-390x660-dark.png`, `evidence/AT-26/playoffs-390x660-light.png`, `evidence/AT-26/playoffs-810x980-dark.png`, `evidence/AT-26/playoffs-810x980-light.png`, `evidence/AT-26/readings.txt`, `evidence/AT-26/steps.txt`, `evidence/AT-26/wk12-1080x740-dark.png`, `evidence/AT-26/wk12-1080x740-light.png`, `evidence/AT-26/wk12-1280x800-dark.png`, `evidence/AT-26/wk12-1280x800-light.png`, `evidence/AT-26/wk12-390x660-dark.png`, `evidence/AT-26/wk12-390x660-light.png`, `evidence/AT-26/wk12-810x980-dark.png`, `evidence/AT-26/wk12-810x980-light.png`
Observation: The switch items read "Wk 11", "Wk 12", "Wk 13", "Wk 14", "Playoffs", and each tap opens its own page: Week 12 vs Puka Deez..., Week 13 vs NFC Least, Week 14 vs Lil Fridge, and "Your playoff odds / Your weeks left" for Playoffs. The shots of Wk 12 and Playoffs show no overlap issue.

## AT-27: The week card shows four tiles in cpc

App: site
Then: the card says "Week 11 vs Maye d'force B with U" and shows four tiles, each with the odds after, the chance, and the wins it adds, as in the file.
Files: `evidence/AT-27/overlap.txt`, `evidence/AT-27/page-1080x740-dark.png`, `evidence/AT-27/page-1080x740-light.png`, `evidence/AT-27/page-1280x800-dark.png`, `evidence/AT-27/page-1280x800-light.png`, `evidence/AT-27/page-390x660-dark.png`, `evidence/AT-27/page-390x660-light.png`, `evidence/AT-27/page-810x980-dark.png`, `evidence/AT-27/page-810x980-light.png`, `evidence/AT-27/readings.txt`, `evidence/AT-27/steps.txt`
Observation: The card reads "Week 11 vs Maye d'force B with U" with four tiles: 86% / 24% likely / +2 wins, 65% / 5% / +1, 67% / 20% / +1, and 41% / 51% / No wins. These match the four week 11 results of page 6 in the file.

## AT-28: The week card shows two tiles in norcal

App: site
Then: the card says "Week 11 vs The Mean Machine" and shows two tiles, a win and a loss.
Files: `evidence/AT-28/overlap.txt`, `evidence/AT-28/page-1080x740-dark.png`, `evidence/AT-28/page-1080x740-light.png`, `evidence/AT-28/page-1280x800-dark.png`, `evidence/AT-28/page-1280x800-light.png`, `evidence/AT-28/page-390x660-dark.png`, `evidence/AT-28/page-390x660-light.png`, `evidence/AT-28/page-810x980-dark.png`, `evidence/AT-28/page-810x980-light.png`, `evidence/AT-28/readings.txt`, `evidence/AT-28/steps.txt`
Observation: The norcal card reads "Week 11 vs The Mean Machine" with two tiles, "Win" (67%, 72% likely, +1 win) and "Lose" (30%, 28% likely, No wins). The header shows Bo Girds at 5-5 with 57%, and the overlap check shows no issue.

## AT-29: The root-for card says what a loss costs

App: site
Then: the header says "If you lose, you drop to X%" with X from the file, and each row shows "<winner> beats <loser>", its reason, and "→ Y%".
Files: `evidence/AT-29/overlap.txt`, `evidence/AT-29/readings.txt`, `evidence/AT-29/root-for-open-1080x740-dark.png`, `evidence/AT-29/root-for-open-1080x740-light.png`, `evidence/AT-29/root-for-open-1280x800-dark.png`, `evidence/AT-29/root-for-open-1280x800-light.png`, `evidence/AT-29/root-for-open-390x660-dark.png`, `evidence/AT-29/root-for-open-390x660-light.png`, `evidence/AT-29/root-for-open-810x980-dark.png`, `evidence/AT-29/root-for-open-810x980-light.png`, `evidence/AT-29/steps.txt`
Observation: The header reads "If you lose, you drop to 48%", which is `loss_playoff` 48 of week 11 in the file. The three rows read "Unsolicited Dak Picks beats The Blue Tent · 1 win ahead of you · → 51%", "NFC Least beats Puka Deez... → 50%", and "Return of T Mac beats Teehee → 50%", with the card open on the phone.

## AT-30: The root-for card opens from one row on a phone

App: site
Then: at 390x660 the card is one row that opens on a tap, and at 1080x740 the card shows in full.
Files: `evidence/AT-30/overlap.txt`, `evidence/AT-30/readings.txt`, `evidence/AT-30/root-for-after-tap-390x660-dark.png`, `evidence/AT-30/root-for-after-tap-390x660-light.png`, `evidence/AT-30/root-for-as-loaded-1080x740-dark.png`, `evidence/AT-30/root-for-as-loaded-1080x740-light.png`, `evidence/AT-30/root-for-as-loaded-390x660-dark.png`, `evidence/AT-30/root-for-as-loaded-390x660-light.png`, `evidence/AT-30/steps.txt`
Observation: At 390x660 the card loads as one row with `aria-expanded=false` and hidden rows, and one tap sets `aria-expanded=true` and shows the rows. At 1080x740 the card has no toggle and shows all three rows as loaded.

## AT-31: A long team name stays readable in a root-for row

App: site
Then: the names of the winner and the loser both show in full or as a short name, with no cut word.
Files: `evidence/AT-31/long-name-page-390x660-dark.png`, `evidence/AT-31/long-name-page-390x660-light.png`, `evidence/AT-31/long-name-row-390x660-dark.png`, `evidence/AT-31/long-name-row-390x660-light.png`, `evidence/AT-31/overlap.txt`, `evidence/AT-31/readings.txt`, `evidence/AT-31/steps.txt`
Observation: At 390x660 the row reads "Maye d'force B with U beats Bo Girds" on full lines, and each text leaf has scrollWidth equal to clientWidth with white-space normal, so the names wrap and no word is cut. The overlap check shows no issue.

## AT-32: A noisy number shows "about"

App: site
Then: the number reads "about X%".
Files: `evidence/AT-32/ladder-file-1280x800-dark.png`, `evidence/AT-32/ladder-file-1280x800-light.png`, `evidence/AT-32/ladder-file-390x660-dark.png`, `evidence/AT-32/ladder-file-390x660-light.png`, `evidence/AT-32/output.txt`, `evidence/AT-32/overlap.txt`, `evidence/AT-32/readings.txt`, `evidence/AT-32/steps.txt`, `evidence/AT-32/wk11-after-tap-1280x800-dark.png`, `evidence/AT-32/wk11-after-tap-1280x800-light.png`, `evidence/AT-32/wk11-after-tap-390x660-dark.png`, `evidence/AT-32/wk11-after-tap-390x660-light.png`
Observation: No result tile in any sim file has the `about` flag (output.txt counts 0 in each file), so no tile could show "about X%" from the file; the shots show "about 99%" and "about 1%" only on the ladder steps that the file flags. output.txt also holds the code that writes "about " before a flagged tile number and a passed unit test "reads a flagged number as about X%".

## AT-33: A tap on a tile sets a What-if

App: site
Then: the header odds, the sentence, and the root-for list change to the numbers of the API answer, and Wk 12 opens.
Files: `evidence/AT-33/after-tap-1080x740-dark.png`, `evidence/AT-33/after-tap-1080x740-light.png`, `evidence/AT-33/after-tap-1280x800-dark.png`, `evidence/AT-33/after-tap-1280x800-light.png`, `evidence/AT-33/after-tap-390x660-dark.png`, `evidence/AT-33/after-tap-390x660-light.png`, `evidence/AT-33/after-tap-810x980-dark.png`, `evidence/AT-33/after-tap-810x980-light.png`, `evidence/AT-33/api-answer.json`, `evidence/AT-33/overlap.txt`, `evidence/AT-33/readings.txt`, `evidence/AT-33/steps.txt`
Observation: After the tap, the header goes from 58% to 86%, the sentence from "Win 5 of the 8 left" to "Win 3 of the 6 left", the root-for header from 48% to 71%, and Wk 12 becomes the current item. These numbers match `api-answer.json` from the local API (`playoff` 86, sentence "Win 3 of the 6 left and you're in.", week 12 `loss_playoff` 71).

## AT-34: The set line lists each set result and resets

App: site
Then: the set line goes away, and the page shows the numbers of the file again.
Files: `evidence/AT-34/after-reset-390x660-dark.png`, `evidence/AT-34/after-reset-390x660-light.png`, `evidence/AT-34/before-reset-390x660-dark.png`, `evidence/AT-34/before-reset-390x660-light.png`, `evidence/AT-34/overlap.txt`, `evidence/AT-34/readings.txt`, `evidence/AT-34/steps.txt`
Observation: Before the Reset the set line reads "What-if: Wk 11 win, beat median | Reset" with 86%. After the Reset no "What-if" region is on the page, and the header shows 58% and "Win 5 of the 8 left" again, as in the file.

## AT-35: A new tap cancels the call before it

App: site
Then: the network log shows the first call cancelled, and the page shows the answer of the second call.
Files: `evidence/AT-35/network.txt`, `evidence/AT-35/overlap.txt`, `evidence/AT-35/readings.txt`, `evidence/AT-35/steps.txt`, `evidence/AT-35/two-taps-390x660-light.png`
Observation: The two taps came 110 ms apart; the network log shows the first POST (win, above) "failed cancelled" at +1422 ms and the second POST (loss, below) finished 200. The page then shows 42% and the set line "What-if: Wk 11 lose, miss median".

## AT-36: The page works with the API down

App: site
Then: the page shows the numbers of the file, and the tap shows one line that the What-if is not available now.
Files: `evidence/AT-36/after-tap-390x660-dark.png`, `evidence/AT-36/after-tap-390x660-light.png`, `evidence/AT-36/network.txt`, `evidence/AT-36/on-open-390x660-dark.png`, `evidence/AT-36/on-open-390x660-light.png`, `evidence/AT-36/overlap.txt`, `evidence/AT-36/readings.txt`, `evidence/AT-36/steps.txt`
Observation: With the API stopped, the page opens at 58% from the file; after the tap the header still shows 58% and one line "The What-if is not available now.". The network log shows the POST to `/sim/what-if` failed with "Could not connect to the server.".

## AT-37: The page makes no call with no set result

App: site
Then: the network log shows no What-if call.
Files: `evidence/AT-37/network.txt`, `evidence/AT-37/overlap.txt`, `evidence/AT-37/readings.txt`, `evidence/AT-37/steps.txt`
Observation: The network log shows no request that names what-if across the load and five week taps. Two requests leave the static server: `gc.zgo.at/count.js` and `GET localhost:8080/clients/cpc/eggs/board`.

## AT-38: "Sim week 11" plays Games, then Standings

App: site
Then: the stage plays the games with Bo Girds first and one median line, then the standings in the Race style.
Files: `evidence/AT-38/0-page-1080x740-dark.png`, `evidence/AT-38/0-page-1080x740-light.png`, `evidence/AT-38/0-page-1280x800-dark.png`, `evidence/AT-38/0-page-1280x800-light.png`, `evidence/AT-38/0-page-390x660-dark.png`, `evidence/AT-38/0-page-390x660-light.png`, `evidence/AT-38/0-page-810x980-dark.png`, `evidence/AT-38/0-page-810x980-light.png`, `evidence/AT-38/1-week-games-1080x740-dark.png`, `evidence/AT-38/1-week-games-1080x740-light.png`, `evidence/AT-38/1-week-games-1280x800-dark.png`, `evidence/AT-38/1-week-games-1280x800-light.png`, `evidence/AT-38/1-week-games-390x660-dark.png`, `evidence/AT-38/1-week-games-390x660-light.png`, `evidence/AT-38/1-week-games-810x980-dark.png`, `evidence/AT-38/1-week-games-810x980-light.png`, `evidence/AT-38/2-week-standings-1080x740-dark.png`, `evidence/AT-38/2-week-standings-1080x740-light.png`, `evidence/AT-38/2-week-standings-1280x800-dark.png`, `evidence/AT-38/2-week-standings-1280x800-light.png`, `evidence/AT-38/2-week-standings-390x660-dark.png`, `evidence/AT-38/2-week-standings-390x660-light.png`, `evidence/AT-38/2-week-standings-810x980-dark.png`, `evidence/AT-38/2-week-standings-810x980-light.png`, `evidence/AT-38/3-week-games-again-1080x740-dark.png`, `evidence/AT-38/3-week-games-again-1080x740-light.png`, `evidence/AT-38/3-week-games-again-1280x800-dark.png`, `evidence/AT-38/3-week-games-again-1280x800-light.png`, `evidence/AT-38/3-week-games-again-390x660-dark.png`, `evidence/AT-38/3-week-games-again-390x660-light.png`, `evidence/AT-38/3-week-games-again-810x980-dark.png`, `evidence/AT-38/3-week-games-again-810x980-light.png`, `evidence/AT-38/overlap.txt`, `evidence/AT-38/readings.txt`, `evidence/AT-38/steps.txt`
Observation: The games screen lists Bo Girds vs Maye d'force B with U first, with one median line (for example "Median 109.4 · you were above"), and the standings screen then shows the Race rows such as "7 Bo Girds (Your team) L 12-10" and "10–12 · out of it". The stage check shows no overlap, no scroll, and no box under the controls in all 32 shots.

## AT-39: "Sim the season" plays three screens on one stage

App: site
Then: the stage plays Season, Playoffs one round at a time, then Champion, with no scroll, and the controls stay in their own row.
Files: `evidence/AT-39/4-season-week-12-1080x740-dark.png`, `evidence/AT-39/4-season-week-12-1080x740-light.png`, `evidence/AT-39/4-season-week-12-1280x800-dark.png`, `evidence/AT-39/4-season-week-12-1280x800-light.png`, `evidence/AT-39/4-season-week-12-390x660-dark.png`, `evidence/AT-39/4-season-week-12-390x660-light.png`, `evidence/AT-39/4-season-week-12-810x980-dark.png`, `evidence/AT-39/4-season-week-12-810x980-light.png`, `evidence/AT-39/5-season-field-set-1080x740-dark.png`, `evidence/AT-39/5-season-field-set-1080x740-light.png`, `evidence/AT-39/5-season-field-set-1280x800-dark.png`, `evidence/AT-39/5-season-field-set-1280x800-light.png`, `evidence/AT-39/5-season-field-set-390x660-dark.png`, `evidence/AT-39/5-season-field-set-390x660-light.png`, `evidence/AT-39/5-season-field-set-810x980-dark.png`, `evidence/AT-39/5-season-field-set-810x980-light.png`, `evidence/AT-39/6-playoffs-round-1-1080x740-dark.png`, `evidence/AT-39/6-playoffs-round-1-1080x740-light.png`, `evidence/AT-39/6-playoffs-round-1-1280x800-dark.png`, `evidence/AT-39/6-playoffs-round-1-1280x800-light.png`, `evidence/AT-39/6-playoffs-round-1-390x660-dark.png`, `evidence/AT-39/6-playoffs-round-1-390x660-light.png`, `evidence/AT-39/6-playoffs-round-1-810x980-dark.png`, `evidence/AT-39/6-playoffs-round-1-810x980-light.png`, `evidence/AT-39/7-playoffs-semifinal-1080x740-dark.png`, `evidence/AT-39/7-playoffs-semifinal-1080x740-light.png`, `evidence/AT-39/7-playoffs-semifinal-1280x800-dark.png`, `evidence/AT-39/7-playoffs-semifinal-1280x800-light.png`, `evidence/AT-39/7-playoffs-semifinal-390x660-dark.png`, `evidence/AT-39/7-playoffs-semifinal-390x660-light.png`, `evidence/AT-39/7-playoffs-semifinal-810x980-dark.png`, `evidence/AT-39/7-playoffs-semifinal-810x980-light.png`, `evidence/AT-39/8-playoffs-final-1080x740-dark.png`, `evidence/AT-39/8-playoffs-final-1080x740-light.png`, `evidence/AT-39/8-playoffs-final-1280x800-dark.png`, `evidence/AT-39/8-playoffs-final-1280x800-light.png`, `evidence/AT-39/8-playoffs-final-390x660-dark.png`, `evidence/AT-39/8-playoffs-final-390x660-light.png`, `evidence/AT-39/8-playoffs-final-810x980-dark.png`, `evidence/AT-39/8-playoffs-final-810x980-light.png`, `evidence/AT-39/9-champion-1080x740-dark.png`, `evidence/AT-39/9-champion-1080x740-light.png`, `evidence/AT-39/9-champion-1280x800-dark.png`, `evidence/AT-39/9-champion-1280x800-light.png`, `evidence/AT-39/9-champion-390x660-dark.png`, `evidence/AT-39/9-champion-390x660-light.png`, `evidence/AT-39/9-champion-810x980-dark.png`, `evidence/AT-39/9-champion-810x980-light.png`, `evidence/AT-39/overlap.txt`, `evidence/AT-39/readings.txt`, `evidence/AT-39/steps.txt`
Observation: The stage plays Season (week 12, field set), Playoffs (round 1, semifinal, final), then Champion, with the tabs SEASON, PLAYOFFS, CHAMPION on top and Sim again and Done in their own row at the bottom. The stage check finds no scroll in the stage or the page and no body box under the controls in all 48 shots.

## AT-40: The replay follows the set results

App: site
Then: the games show Bo Girds beat Maye d'force B with U, and the median line says Bo Girds was above.
Files: `evidence/AT-40/at40-1-games-1080x740-dark.png`, `evidence/AT-40/at40-1-games-1080x740-light.png`, `evidence/AT-40/at40-1-games-1280x800-dark.png`, `evidence/AT-40/at40-1-games-1280x800-light.png`, `evidence/AT-40/at40-1-games-390x660-dark.png`, `evidence/AT-40/at40-1-games-390x660-light.png`, `evidence/AT-40/at40-1-games-810x980-dark.png`, `evidence/AT-40/at40-1-games-810x980-light.png`, `evidence/AT-40/at40-2-standings-1080x740-dark.png`, `evidence/AT-40/at40-2-standings-1080x740-light.png`, `evidence/AT-40/at40-2-standings-1280x800-dark.png`, `evidence/AT-40/at40-2-standings-1280x800-light.png`, `evidence/AT-40/at40-2-standings-390x660-dark.png`, `evidence/AT-40/at40-2-standings-390x660-light.png`, `evidence/AT-40/at40-2-standings-810x980-dark.png`, `evidence/AT-40/at40-2-standings-810x980-light.png`, `evidence/AT-40/overlap.txt`, `evidence/AT-40/readings.txt`, `evidence/AT-40/steps.txt`
Observation: With the What-if "Win, beat median" set through the local API (200), each of the 8 replays shows "Bo Girds wins." in the first game row and a median line that ends "you were above". The overlap check shows no issue in the 16 shots.

## AT-41: The replay uses fades only under reduced motion

App: site
Then: no element moves its position, and each change is a fade.
Files: `evidence/AT-41/motion-full-1-season-390x660-dark.png`, `evidence/AT-41/motion-full-1-season-390x660-light.png`, `evidence/AT-41/motion-full-2-playoffs-390x660-dark.png`, `evidence/AT-41/motion-full-2-playoffs-390x660-light.png`, `evidence/AT-41/motion-full-3-champion-390x660-dark.png`, `evidence/AT-41/motion-full-3-champion-390x660-light.png`, `evidence/AT-41/motion-full-4-week-standings-390x660-dark.png`, `evidence/AT-41/motion-full-4-week-standings-390x660-light.png`, `evidence/AT-41/motion-reduced-1-season-390x660-dark.png`, `evidence/AT-41/motion-reduced-1-season-390x660-light.png`, `evidence/AT-41/motion-reduced-2-playoffs-390x660-dark.png`, `evidence/AT-41/motion-reduced-2-playoffs-390x660-light.png`, `evidence/AT-41/motion-reduced-3-champion-390x660-dark.png`, `evidence/AT-41/motion-reduced-3-champion-390x660-light.png`, `evidence/AT-41/motion-reduced-4-week-standings-390x660-dark.png`, `evidence/AT-41/motion-reduced-4-week-standings-390x660-light.png`, `evidence/AT-41/overlap.txt`, `evidence/AT-41/readings.txt`, `evidence/AT-41/steps.txt`
Observation: Under reduced motion the frame check counts 0 elements that moved over two frames and 0 inline transforms, in both themes. With full motion the same check counts 194 and 200 moved elements, so the check does see motion when it is on.

## AT-42: A team in the playoffs sees its title odds and its game

App: both
Then: the page shows the title odds of that team, its game of the round, and two tiles with the odds after a win and after a loss.
Files: `evidence/AT-42/output.txt`, `evidence/AT-42/page-block.json`, `evidence/AT-42/overlap.txt`, `evidence/AT-42/readings.txt`, `evidence/AT-42/round-2-top-seed-1080x740-dark.png`, `evidence/AT-42/round-2-top-seed-1080x740-light.png`, `evidence/AT-42/round-2-top-seed-1280x800-dark.png`, `evidence/AT-42/round-2-top-seed-1280x800-light.png`, `evidence/AT-42/round-2-top-seed-390x660-dark.png`, `evidence/AT-42/round-2-top-seed-390x660-light.png`, `evidence/AT-42/round-2-top-seed-810x980-dark.png`, `evidence/AT-42/round-2-top-seed-810x980-light.png`, `evidence/AT-42/steps.txt`
Observation: Pipeline part: A fresh `make sim-fixtures` gives seeds 1 All You Need Is Love, 2 Lil Fridge, 3 Maye d'force B with U, 4 Return of T Mac, 5 Teehee, 6 The Blue Tent, and run 1 champion Lil Fridge, with no change to the committed fixtures. In the round-two fixture, the page of top seed All You Need Is Love has title odds 19 and a week 16 game against The Blue Tent, with two results: a win at title odds 43 and a loss at 0.
Site part: with the top seed All You Need Is Love as Your team, the page shows 19% title odds, "Week 16 vs The Blue Tent", and two tiles: Win 43% (45% likely, To the final) and Lose 0% (55% likely, Season over). The overlap check shows no issue in the 8 shots.

## AT-43: A team out of the playoffs sees the bracket

App: both
Then: the page says "Out of the playoffs" and shows the bracket with the title odds of each team left.
Files: `evidence/AT-43/output.txt`, `evidence/AT-43/page-block.json`, `evidence/AT-43/overlap.txt`, `evidence/AT-43/playoffs-12th-1080x740-dark.png`, `evidence/AT-43/playoffs-12th-1080x740-light.png`, `evidence/AT-43/playoffs-12th-1280x800-dark.png`, `evidence/AT-43/playoffs-12th-1280x800-light.png`, `evidence/AT-43/playoffs-12th-390x660-dark.png`, `evidence/AT-43/playoffs-12th-390x660-light.png`, `evidence/AT-43/playoffs-12th-810x980-dark.png`, `evidence/AT-43/playoffs-12th-810x980-light.png`, `evidence/AT-43/readings.txt`, `evidence/AT-43/steps.txt`
Observation: Pipeline part: In the playoff fixture, the 12th team is NFC Least at 7-21, and its page has status `out`, title 0, and no game. Its `playoffs.teams` lists the 6 seeds, each alive with title odds from 12 to 23, and `rounds` gives the week 15 games Maye d'force B with U vs The Blue Tent and Return of T Mac vs Teehee.
Site part: with NFC Least as Your team, the page says "Out of the playoffs" and "Your season is over. 6 teams are left in the race for the title.", with the title odds of the 6 teams and the bracket. The overlap check shows no issue.

## AT-44: After the final the page shows the champion

App: both
Then: the page shows the final bracket and the champion, with no result tile and no sim button.
Files: `evidence/AT-44/output.txt`, `evidence/AT-44/page-block.json`, `evidence/AT-44/overlap.txt`, `evidence/AT-44/readings.txt`, `evidence/AT-44/season-end-1080x740-dark.png`, `evidence/AT-44/season-end-1080x740-light.png`, `evidence/AT-44/season-end-1280x800-dark.png`, `evidence/AT-44/season-end-1280x800-light.png`, `evidence/AT-44/season-end-390x660-dark.png`, `evidence/AT-44/season-end-390x660-light.png`, `evidence/AT-44/season-end-810x980-dark.png`, `evidence/AT-44/season-end-810x980-light.png`, `evidence/AT-44/steps.txt`
Observation: Pipeline part: The season-end fixture has weeks 15 to 17 played, and the fact "Lil Fridge is the 2026 champion". Each page has `champion` 3, Lil Fridge, and `game` null; the rounds show the final, All You Need Is Love vs Lil Fridge, 119.1 to 131.9.
Site part: the page shows "2026 CHAMPION Lil Fridge", "Beat All You Need Is Love 131.9 to 119.1 in the final", and the full bracket with scores. It has 0 buttons in main, no result tile group, and no Sim button.

## AT-45: The Sim tile shows Your team's odds after Standings

App: site
Then: the Sim tile sits between Standings and Next week, shows the odds of Bo Girds and the line of more wins from the file, and links to `/sim/2026/`.
Files: `evidence/AT-45/overlap.txt`, `evidence/AT-45/readings.txt`, `evidence/AT-45/sim-tile-bo-girds-1080x740-dark.png`, `evidence/AT-45/sim-tile-bo-girds-1080x740-light.png`, `evidence/AT-45/sim-tile-bo-girds-1280x800-dark.png`, `evidence/AT-45/sim-tile-bo-girds-1280x800-light.png`, `evidence/AT-45/sim-tile-bo-girds-390x660-dark.png`, `evidence/AT-45/sim-tile-bo-girds-390x660-light.png`, `evidence/AT-45/sim-tile-bo-girds-810x980-dark.png`, `evidence/AT-45/sim-tile-bo-girds-810x980-light.png`, `evidence/AT-45/steps.txt`
Observation: At each size the tile sits between the ids `standings` and `next-week`, shows "PLAYOFF ODDS 58%" and "Win 5 of the 8 left and you're in.", and links to `/sim/2026/`. The labels "After week 10" and "Playoff odds" read 12px at 390x660, 13px at 810x980, and 14px at 1080x740 and 1280x800, and `section#sim` is 278px high at 1280x800. The overlap check shows 12 issues only at 810x980, all in the wrapped byes line of Next week under the tile.

## AT-46: The Sim tile shows a league fact with no team set

App: site
Then: the Sim tile shows the league fact of the file.
Files: `evidence/AT-46/overlap.txt`, `evidence/AT-46/readings.txt`, `evidence/AT-46/sim-tile-no-team-1080x740-dark.png`, `evidence/AT-46/sim-tile-no-team-1080x740-light.png`, `evidence/AT-46/sim-tile-no-team-1280x800-dark.png`, `evidence/AT-46/sim-tile-no-team-1280x800-light.png`, `evidence/AT-46/sim-tile-no-team-390x660-dark.png`, `evidence/AT-46/sim-tile-no-team-390x660-light.png`, `evidence/AT-46/sim-tile-no-team-810x980-dark.png`, `evidence/AT-46/sim-tile-no-team-810x980-light.png`, `evidence/AT-46/steps.txt`
Observation: With no team set, the tile shows "THE LEAGUE 6 managers fight for the last 4 spots" at each size, which is the `fact` of `week-10/sim.json` at b5de9120. The overlap check shows 15 issues only at 810x980, in the wrapped byes line of Next week, outside the tile.

## AT-47: The Sim tile fits a playoff week

App: both
Then: the tile shows the title odds of the top seed, and the favorite fact for the 12th team.
Files: `evidence/AT-47/output.txt`, `evidence/AT-47/output.txt`, `evidence/AT-47/overlap.txt`, `evidence/AT-47/readings.txt`, `evidence/AT-47/sim-tile-12th-team-390x660-dark.png`, `evidence/AT-47/sim-tile-12th-team-390x660-light.png`, `evidence/AT-47/sim-tile-top-seed-390x660-dark.png`, `evidence/AT-47/sim-tile-top-seed-390x660-light.png`, `evidence/AT-47/steps.txt`
Observation: Pipeline part: The playoff fixture has the fact "6 teams left, Lil Fridge is the favorite at 23%". The page of top seed All You Need Is Love has title odds 17 and a week 15 bye, and the page of the 12th team, NFC Least, has status `out` and title 0.
Site part: on the playoff fixture, the tile with the top seed (roster 2) shows "AFTER WEEK 14 TITLE ODDS 17% Seed 1, a bye in week 15.". With the 12th team (roster 4) it shows "THE LEAGUE 6 teams left, Lil Fridge is the favorite at 23%". The overlap check shows no issue in the 4 shots at 390x660.

## AT-48: The week 17 Sim tile shows the champion

App: both
Then: the tile names the champion of the fixture and links to the sim page.
Files: `evidence/AT-48/output.txt`, `evidence/AT-48/output.txt`, `evidence/AT-48/overlap.txt`, `evidence/AT-48/readings.txt`, `evidence/AT-48/sim-tile-season-end-1080x740-dark.png`, `evidence/AT-48/sim-tile-season-end-1080x740-light.png`, `evidence/AT-48/sim-tile-season-end-1280x800-dark.png`, `evidence/AT-48/sim-tile-season-end-1280x800-light.png`, `evidence/AT-48/sim-tile-season-end-390x660-dark.png`, `evidence/AT-48/sim-tile-season-end-390x660-light.png`, `evidence/AT-48/sim-tile-season-end-810x980-dark.png`, `evidence/AT-48/sim-tile-season-end-810x980-light.png`, `evidence/AT-48/steps.txt`
Observation: Pipeline part: The season-end fixture has week 17, weeks 15 to 17 played, and the fact "Lil Fridge is the 2026 champion". The champion of the pages is Lil Fridge.
Site part: on the season-end fixture, the tile shows "AFTER WEEK 17 THE LEAGUE Lil Fridge is the 2026 champion" and "Open the season sim", with href `/sim/2026/`, at each size. The overlap check shows 15 issues only at 810x980, in the wrapped byes line of Next week, outside the tile.

## AT-49: The home page ladder links to the sim page

App: site
Then: the browser opens `/sim/2026/`.
Files: `evidence/AT-49/after-tap-390x660-dark.png`, `evidence/AT-49/after-tap-390x660-light.png`, `evidence/AT-49/ladder-1080x740-dark.png`, `evidence/AT-49/ladder-1080x740-light.png`, `evidence/AT-49/ladder-1280x800-dark.png`, `evidence/AT-49/ladder-1280x800-light.png`, `evidence/AT-49/ladder-390x660-dark.png`, `evidence/AT-49/ladder-390x660-light.png`, `evidence/AT-49/ladder-810x980-dark.png`, `evidence/AT-49/ladder-810x980-light.png`, `evidence/AT-49/overlap.txt`, `evidence/AT-49/readings.txt`, `evidence/AT-49/steps.txt`
Observation: The ladder shows the link "Open the season sim" with href `/sim/2026/` at each size. A tap at 390x660 opens `http://127.0.0.1:4173/sim/2026/` in light and in dark. The overlap check flags "Clear" against "Playoff race" at 810x980, in the chip row above the ladder.

## AT-50: The menu has "Season sim"

App: site
Then: the menu has "Season sim", and it opens `/sim/2026/`.
Files: `evidence/AT-50/menu-open-1080x740-dark.png`, `evidence/AT-50/menu-open-1080x740-light.png`, `evidence/AT-50/menu-open-1280x800-dark.png`, `evidence/AT-50/menu-open-1280x800-light.png`, `evidence/AT-50/menu-open-390x660-dark.png`, `evidence/AT-50/menu-open-390x660-light.png`, `evidence/AT-50/menu-open-810x980-dark.png`, `evidence/AT-50/menu-open-810x980-light.png`, `evidence/AT-50/overlap.txt`, `evidence/AT-50/readings.txt`, `evidence/AT-50/steps.txt`
Observation: At 390x660 and 810x980 the open menu sheet has one visible "Season sim" link to `/sim/2026/`, and a tap opens `/sim/2026/`. At 1080x740 and 1280x800 the site shows no menu button; the top band lists "Season sim" in line, linked to `/sim/2026/`.

## AT-51: The Announcement opens on the home page

App: site
Then: the sheet rises with the rows of The Blue Tent, Bo Girds, and Return of T Mac, the playoff line, the chip, and the copy of the spec.
Files: `evidence/AT-51/closed-after-not-now-1080x740-dark.png`, `evidence/AT-51/closed-after-not-now-1080x740-light.png`, `evidence/AT-51/closed-after-not-now-1280x800-dark.png`, `evidence/AT-51/closed-after-not-now-1280x800-light.png`, `evidence/AT-51/closed-after-not-now-390x660-dark.png`, `evidence/AT-51/closed-after-not-now-390x660-light.png`, `evidence/AT-51/closed-after-not-now-810x980-dark.png`, `evidence/AT-51/closed-after-not-now-810x980-light.png`, `evidence/AT-51/open-1080x740-dark.png`, `evidence/AT-51/open-1080x740-light.png`, `evidence/AT-51/open-1280x800-dark.png`, `evidence/AT-51/open-1280x800-light.png`, `evidence/AT-51/open-390x660-dark.png`, `evidence/AT-51/open-390x660-light.png`, `evidence/AT-51/open-810x980-dark.png`, `evidence/AT-51/open-810x980-light.png`, `evidence/AT-51/steps.txt`, `evidence/AT-51/test-output.txt`
Observation: At each size and theme the sheet shows rows 5 The Blue Tent 81%, 6 Bo Girds 86%, the PLAYOFF LINE, 7 Return of T Mac 39%, the chip "What-if: Bo Girds win both" (ON), "NEW: SEASON SIM", "See your path to the playoffs", the line, "Open the sim", and "Not now". The test output reads no overlap and no cover in all 8 open shots, and Not now closes the sheet each time.

## AT-52: The What-if chip is a button

App: site
Then: the first tap turns it off and the odds go back to the odds of the week, and the second tap turns it on again.
Files: `evidence/AT-52/0-after-auto-390x660-dark.png`, `evidence/AT-52/1-tap-off-390x660-dark.png`, `evidence/AT-52/2-tap-on-390x660-dark.png`, `evidence/AT-52/steps.txt`, `evidence/AT-52/test-output.txt`
Observation: After the automatic turn the chip is on at 86%. The first tap sets `aria-pressed` false with the status "Playoff odds 58%", and the second tap sets it true with "Playoff odds 86%". The three shots show ON at 86%, TAP at 58%, and ON at 86%.

## AT-53: The chip turns on once by itself after the sheet settles

App: site
Then: the chip turns on once after the sheet stops, and it does not turn on again.
Files: `evidence/AT-53/00-0852ms-off-390x660-dark.png`, `evidence/AT-53/01-1420ms-off-390x660-dark.png`, `evidence/AT-53/02-2013ms-off-390x660-dark.png`, `evidence/AT-53/03-2604ms-off-390x660-dark.png`, `evidence/AT-53/04-3199ms-on-390x660-dark.png`, `evidence/AT-53/05-3790ms-on-390x660-dark.png`, `evidence/AT-53/06-4378ms-on-390x660-dark.png`, `evidence/AT-53/07-4969ms-on-390x660-dark.png`, `evidence/AT-53/08-5584ms-on-390x660-dark.png`, `evidence/AT-53/09-6181ms-on-390x660-dark.png`, `evidence/AT-53/10-6779ms-on-390x660-dark.png`, `evidence/AT-53/steps.txt`, `evidence/AT-53/test-output.txt`
Observation: Over the series from 852 ms to 6779 ms the chip reads off four times, then on at 3199 ms, and stays on to the end, with one flip in all (test output and 11 shots).

## AT-54: Four ways close the Announcement

App: site
Then: the sheet closes each time.
Files: `evidence/AT-54/closed-by-drag-down-390x660-dark.png`, `evidence/AT-54/closed-by-Escape-390x660-dark.png`, `evidence/AT-54/closed-by-Not-now-390x660-dark.png`, `evidence/AT-54/closed-by-tap-on-the-dim-390x660-dark.png`, `evidence/AT-54/steps.txt`, `evidence/AT-54/test-output.txt`
Observation: The test output shows the sheet gone after each of drag down, Not now, Escape, and a tap on the dim, each in a fresh browser. The drag used a mouse pointer at the phone size, because Playwright WebKit sends no touch drag.

## AT-55: A dismiss or the link hides the Announcement for good

App: site
Then: the Announcement does not open.
Files: `evidence/AT-55/after-dismiss-reload-390x660-dark.png`, `evidence/AT-55/after-link-reload-390x660-dark.png`, `evidence/AT-55/steps.txt`, `evidence/AT-55/test-output.txt`
Observation: After Not now and a reload, the test output counts no Announcement. After "Open the sim", which opened `/sim/2026/`, and a load of the home page, it counts none too. The two shots show the home page with no sheet.

## AT-56: The Announcement does not open on the sim page or over a sheet

App: site
Then: the Announcement does not open in either case.
Files: `evidence/AT-56/menu-open-390x660-dark.png`, `evidence/AT-56/sim-page-390x660-dark.png`, `evidence/AT-56/steps.txt`, `evidence/AT-56/test-output.txt`
Observation: The test output counts no Announcement on `/sim/2026/` and none with the menu sheet "Pages" open, and the next load opens it. The shots show the sim page of Bo Girds and the open menu, each with no Announcement.

## AT-57: A first visit shows the team picker, and the next load shows the Announcement

App: site
Then: the first load shows only the team picker, and the reload shows the Announcement.
Files: `evidence/AT-57/1-first-load-390x660-dark.png`, `evidence/AT-57/2-reload-390x660-dark.png`, `evidence/AT-57/3-fast-pick-same-load-390x660-dark.png`, `evidence/AT-57/steps.txt`, `evidence/AT-57/test-output.txt`
Observation: The first load shows only "Which team is yours?" and no Announcement, the pick of Bo Girds does not open it on the same load, and the reload shows the Announcement. A second browser picked Bo Girds 261 ms after the start of the load, before the load beat. 3 s later it counted no Announcement, with `cpc.your-team` 6 (shot 3).

## AT-58: The Announcement does not open with no team set

App: site
Then: the Announcement does not open, and it opens on a later load after a team is set.
Files: `evidence/AT-58/0-after-close-tries-390x660-dark.png`, `evidence/AT-58/1-reload-no-team-390x660-dark.png`, `evidence/AT-58/2-later-load-team-set-390x660-dark.png`, `evidence/AT-58/steps.txt`, `evidence/AT-58/test-output.txt`
Observation: The shots start from a fresh browser with no team set, at b5de9120: Escape, a tap on the dim, and a mouse drag down each leave the first-visit team picker open, with `cpc.your-team` null. The reload with no team shows the picker again and no Announcement, and a later load with `cpc.your-team` 6 shows the Announcement. The vitest output shows the 11 tests of `announcement.test.tsx` passed, with the AT-57, AT-58 test among them.

## AT-59: The Announcement stops after its end date

App: site
Then: the Announcement does not open.
Files: `evidence/AT-59/past-end-390x660-dark.png`, `evidence/AT-59/steps.txt`, `evidence/AT-59/test-output.txt`
Observation: With the page clock at 2026-12-02 12:00, 1 day past the stop date 2026-12-01, the test output counts no Announcement, and the shot shows the home page with no sheet.

## AT-60: The Announcement takes other art and copy

App: site
Then: it shows the test art and copy, with the same close rules.
Files: `evidence/AT-60/output.txt`
Observation: The vitest output shows the 8 tests of `packages/design/site/parts/announcement.test.tsx` passed, which render the Announcement with a test art slot and test copy and close it by Not now, Escape, a tap on the dim, and a drag down.

## AT-61: The Announcement under reduced motion

App: site
Then: the rows and the odds show at once, and the chip does not turn on by itself.
Files: `evidence/AT-61/closed-reduced-1080x740-dark.png`, `evidence/AT-61/closed-reduced-1080x740-light.png`, `evidence/AT-61/closed-reduced-1280x800-dark.png`, `evidence/AT-61/closed-reduced-1280x800-light.png`, `evidence/AT-61/closed-reduced-390x660-dark.png`, `evidence/AT-61/closed-reduced-390x660-light.png`, `evidence/AT-61/closed-reduced-810x980-dark.png`, `evidence/AT-61/closed-reduced-810x980-light.png`, `evidence/AT-61/open-reduced-1080x740-dark.png`, `evidence/AT-61/open-reduced-1080x740-light.png`, `evidence/AT-61/open-reduced-1280x800-dark.png`, `evidence/AT-61/open-reduced-1280x800-light.png`, `evidence/AT-61/open-reduced-390x660-dark.png`, `evidence/AT-61/open-reduced-390x660-light.png`, `evidence/AT-61/open-reduced-810x980-dark.png`, `evidence/AT-61/open-reduced-810x980-light.png`, `evidence/AT-61/steps.txt`, `evidence/AT-61/test-output.txt`
Observation: Under reduced motion the shot at 0.9 s shows all rows and the 86% odds, and the test output reads `chip stays off` (aria-pressed false) at each size and theme. Shots of all four sizes are in the folder; the Evidence line asks for 390x660.

## AT-62: No banned word shows on the new parts

App: site
Then: none has "rival", "Brian", "Jev", "Advisor", "Finder", or "front door".
Files: `evidence/AT-62/at62-rendered.txt`, `evidence/AT-62/at62.mjs`, `evidence/AT-62/at62.txt`, `evidence/AT-62/steps.txt`
Observation: The rendered text of the sim page, the replay, the Sim tile, and the Announcement of both clients has no hit of any banned word. The built HTML search finds one hit, "brian", in the norcal `/2026/week-10/index.html`: it is the NFL player "Brian Robinson Jr." in Next week byes, outside the new parts.

## AT-63: The site has no copy of the sim

App: site
Then: no site module draws a score, and each What-if number comes from the API.
Files: `evidence/AT-63/output.txt`
Observation: The search finds `Math.random` only in the replay, where it picks a stored run by its weight (`pickRun`, `randomRun`); no site module draws a score. Each What-if number comes from `useWhatIf`, which holds the `page` of the answer of `whatIfApi`, a `fetch` to `POST /clients/<slug>/sim/what-if`.

## AT-64: The midseason report does not change

App: both
Then: the diff is empty, and `/midseason/2026/` looks as on `main`.
Files: `evidence/AT-64/output.txt`, `evidence/AT-64/compare.txt`, `evidence/AT-64/midseason-cpc-branch-390x660-dark.png`, `evidence/AT-64/midseason-cpc-branch-390x660-light.png`, `evidence/AT-64/midseason-cpc-branch-text.txt`, `evidence/AT-64/midseason-cpc-main-390x660-dark.png`, `evidence/AT-64/midseason-cpc-main-390x660-light.png`, `evidence/AT-64/midseason-cpc-main-text.txt`, `evidence/AT-64/midseason-norcal-branch-390x660-dark.png`, `evidence/AT-64/midseason-norcal-branch-390x660-light.png`, `evidence/AT-64/midseason-norcal-branch-text.txt`, `evidence/AT-64/midseason-norcal-main-390x660-dark.png`, `evidence/AT-64/midseason-norcal-main-390x660-light.png`, `evidence/AT-64/midseason-norcal-main-text.txt`, `evidence/AT-64/overlap.txt`, `evidence/AT-64/readings.txt`, `evidence/AT-64/steps.txt`
Observation: Pipeline part: `git diff origin/main` of the season `sim.json` and `midseason.json` of both clients is empty, and the four files are tracked. origin/main 33da78a4 is the merge base, and the diff from the merge base to HEAD is empty too.
Site part: the shots of `/midseason/2026/` at 390x660 on the branch build and on the main build are the same bytes for both clients and both themes, and the main text of each pair has no diff (`compare.txt`). The overlap check reports the same issues on the branch and on main, in the report page itself.

## AT-65: The page has no grid of every game

App: site
Then: the only result tiles are the results of Bo Girds, and no grid lists every game.
Files: `evidence/AT-65/overlap.txt`, `evidence/AT-65/playoffs-1080x740-dark.png`, `evidence/AT-65/playoffs-1080x740-light.png`, `evidence/AT-65/playoffs-1280x800-dark.png`, `evidence/AT-65/playoffs-1280x800-light.png`, `evidence/AT-65/playoffs-390x660-dark.png`, `evidence/AT-65/playoffs-390x660-light.png`, `evidence/AT-65/playoffs-810x980-dark.png`, `evidence/AT-65/playoffs-810x980-light.png`, `evidence/AT-65/readings.txt`, `evidence/AT-65/steps.txt`, `evidence/AT-65/wk11-1080x740-dark.png`, `evidence/AT-65/wk11-1080x740-light.png`, `evidence/AT-65/wk11-1280x800-dark.png`, `evidence/AT-65/wk11-1280x800-light.png`, `evidence/AT-65/wk11-390x660-dark.png`, `evidence/AT-65/wk11-390x660-light.png`, `evidence/AT-65/wk11-810x980-dark.png`, `evidence/AT-65/wk11-810x980-light.png`, `evidence/AT-65/wk12-1080x740-dark.png`, `evidence/AT-65/wk12-1080x740-light.png`, `evidence/AT-65/wk12-1280x800-dark.png`, `evidence/AT-65/wk12-1280x800-light.png`, `evidence/AT-65/wk12-390x660-dark.png`, `evidence/AT-65/wk12-390x660-light.png`, `evidence/AT-65/wk12-810x980-dark.png`, `evidence/AT-65/wk12-810x980-light.png`, `evidence/AT-65/wk13-1080x740-dark.png`, `evidence/AT-65/wk13-1080x740-light.png`, `evidence/AT-65/wk13-1280x800-dark.png`, `evidence/AT-65/wk13-1280x800-light.png`, `evidence/AT-65/wk13-390x660-dark.png`, `evidence/AT-65/wk13-390x660-light.png`, `evidence/AT-65/wk13-810x980-dark.png`, `evidence/AT-65/wk13-810x980-light.png`, `evidence/AT-65/wk14-1080x740-dark.png`, `evidence/AT-65/wk14-1080x740-light.png`, `evidence/AT-65/wk14-1280x800-dark.png`, `evidence/AT-65/wk14-1280x800-light.png`, `evidence/AT-65/wk14-390x660-dark.png`, `evidence/AT-65/wk14-390x660-light.png`, `evidence/AT-65/wk14-810x980-dark.png`, `evidence/AT-65/wk14-810x980-light.png`
Observation: Each of Wk 11 to Wk 14 has exactly 4 result tiles, all results of Bo Girds, and Playoffs has 0; no labelled list of games is on any week page. The overlap check shows no issue in the 40 shots.

## AT-66: The page offers no result of an unset bracket game

App: site
Then: only the game of the current round has tiles, and no later round has a tile.
Files: `evidence/AT-66/overlap.txt`, `evidence/AT-66/playoffs-seed-3-390x660-dark.png`, `evidence/AT-66/playoffs-seed-3-390x660-light.png`, `evidence/AT-66/playoffs-top-seed-390x660-dark.png`, `evidence/AT-66/playoffs-top-seed-390x660-light.png`, `evidence/AT-66/readings.txt`, `evidence/AT-66/steps.txt`
Observation: With the top seed (a bye in week 15) the Playoffs page has no result tile, and with seed 3 it has two tiles only for "Week 15 vs The Blue Tent". The semifinal and final rows show only "Winner of week 15" and "Winner of week 16", with no tile.

## AT-67: The server keeps no record of a dismiss

App: api
Then: no route reads or writes an Announcement.
Files: `evidence/AT-67/output.txt`
Observation: `openapi.json` of the real local API lists 24 routes, and no path names an Announcement or a dismiss. No route sets `include_in_schema`, and `git grep` finds no "announce" or "dismiss" in the API source or the Python packages.

## AT-68: The API keeps no cache of answers

App: api
Then: the log shows two runs of the sim.
Files: `evidence/AT-68/output.txt`
Observation: Two real posts of the same What-if both got 200, and the answers have one SHA-256. The server log shows two lines "What-if of cpc ran 10000 runs", at 3.69 s and 2.68 s.

## AT-69: The page shows no chart of odds by week after the final

App: site
Then: the page has no chart of the odds of each team by week.
Files: `evidence/AT-69/overlap.txt`, `evidence/AT-69/readings.txt`, `evidence/AT-69/season-end-1080x740-dark.png`, `evidence/AT-69/season-end-1080x740-light.png`, `evidence/AT-69/season-end-1280x800-dark.png`, `evidence/AT-69/season-end-1280x800-light.png`, `evidence/AT-69/season-end-390x660-dark.png`, `evidence/AT-69/season-end-390x660-light.png`, `evidence/AT-69/season-end-810x980-dark.png`, `evidence/AT-69/season-end-810x980-light.png`, `evidence/AT-69/steps.txt`
Observation: The season-end page shows the champion block and the bracket only; main holds no canvas, no role img, and one svg, and no chart of the odds by week shows in the 8 shots. The overlap check shows no issue.
