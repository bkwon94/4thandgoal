# Front door: evidence

Spec: `.scratch/front-door/PRD.md`. Acceptance tests: `.scratch/front-door/ACCEPTANCE.md`.
Built from: `bfb301df`, on 2026-11-10. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 1 min for 2 site tests with a `steps.json` (the runner total, 58.3 s). The whole round took about 65 min of wall time.

## How the round ran

- The week. `main` publishes week 9 too. To match the setup ("latest week 8"), the round moved `clients/cpc/published/2026/week-09/` and `clients/norcal/published/2026/week-09/` out of the repo, so each site build had latest week 8. The round put them back after the last site test. AT-33 uses the real week 9 for its rebuild. The season files (`managers.json`, `rankings.json`) stay at their week 9 state, because the round hid only the week folders.
- The API. The API ran on this machine with the passphrase `localtest`, a rate limit of 600, the allowed origin `http://127.0.0.1:4173`, and `CORNERSTONE_ASK_DIR` set to an empty temp folder outside the repo. It called the real Jev and the real Claude, and it read live Sleeper data. The launcher (scratchpad `driver/launch_api.py`) runs the app of `make -C apps/api api-evidence` with one seam for AT-34: a flag file adds one player to the live roster of Lil Fridge. The flag was off for every other test.
- The live data. The API reads the league now, through week 9 games (the trade documents say `stats_through: 9`). So a live fact, such as the fact of a personal Topic or of a trade, reads the league after week 9. The league Topics read the published week 8.
- The site tests. The evidence runner (`pnpm --dir apps/site evidence front-door AT-1 AT-50`) took the shots of AT-1 and AT-50. Each other site test needs a step that no runner verb covers: a fixed day, a stored team, the passphrase, a recording, or the API calls of the run. Those tests ran in a Playwright 1.64 driver of the round (scratchpad `driver/tests.mjs`), against the static export served on `http://127.0.0.1:4173` with a `404.html` fallback. The driver fixes the browser clock to Wednesday 2026-11-04 10:00 America/Los_Angeles (Tuesday 2026-11-03 for AT-5), and it records each API call with its full body in `api-calls*.json`. Each folder holds a `steps.txt` that says how its files were made.
- The API clock is the real clock: Tuesday 2026-11-10 in the league time zone. A stale line names the day that the API kept the Answer, so it says "Tuesday".
- The site builds set `NEXT_PUBLIC_API_URL=http://localhost:8080`. The NorCal build failed one time on stale generated types in `apps/site/.next/dev`. The round moved that folder out of the repo, and the build then passed.
- After each API run, the round put back the files that the live API rewrites under `clients/*/data/2026/history/week-09/`.

## AT-1: The first visit asks for Your team with no skip

App: site
Then: A sheet lists the 12 teams of CPC, and it has no skip, no close, and no login.
Files: `evidence/AT-1/steps.json`, `evidence/AT-1/375-light.png`, `evidence/AT-1/375-dark.png`, `evidence/AT-1/768-light.png`, `evidence/AT-1/768-dark.png`, `evidence/AT-1/1280-light.png`, `evidence/AT-1/1280-dark.png`
Observation: Each shot shows the sheet "Which team is yours?" with 12 team rows, each with its record and place. The sheet shows no skip button, no close button, and no login field.

## AT-2: The browser keeps Your team

App: site
Then: The front door shows the Suggestions of Lil Fridge, and no sheet shows.
Files: `evidence/AT-2/steps.txt`, `evidence/AT-2/sheet-375-light.png`, `evidence/AT-2/sheet-375-dark.png`, `evidence/AT-2/before-reload-375-light.png`, `evidence/AT-2/before-reload-375-dark.png`, `evidence/AT-2/after-reload-375-light.png`, `evidence/AT-2/after-reload-375-dark.png`, `evidence/AT-2/after-reload-dialogs-375-light.txt`, `evidence/AT-2/after-reload-dialogs-375-dark.txt`
Observation: After the reload, the page shows "Ask about Lil Fridge" with its Suggestion chips. The text files count 0 dialogs on the page after the reload, and `cpc.your-team` is 3.

## AT-3: A change of Your team keeps each Thread

App: site
Then: Bo Girds shows an empty Thread, and Lil Fridge shows its week recap Answer again.
Files: `evidence/AT-3/steps.txt`, `evidence/AT-3/1-lil-fridge-recap-375-light.png`, `evidence/AT-3/1-lil-fridge-recap-375-dark.png`, `evidence/AT-3/2-bo-girds-375-light.png`, `evidence/AT-3/2-bo-girds-375-dark.png`, `evidence/AT-3/3-lil-fridge-again-375-light.png`, `evidence/AT-3/3-lil-fridge-again-375-dark.png`
Observation: Shot 2 shows "Ask about Bo Girds" with no Answer in the Thread. Shot 3 shows the Thread of Lil Fridge with the Week recap Answer (80.11, 12th of 12) as in shot 1.

## AT-4: Three Suggestions with a fact each, plus More

App: site
Then: 3 Suggestion chips show, each with a Topic name and one number, and "More" leads the row. A tap on "More" lists all 13 Topics.
Files: `evidence/AT-4/steps.txt`, `evidence/AT-4/api-calls.json`, `evidence/AT-4/closed-375-light.png`, `evidence/AT-4/closed-375-dark.png`, `evidence/AT-4/closed-768-light.png`, `evidence/AT-4/closed-768-dark.png`, `evidence/AT-4/closed-1280-light.png`, `evidence/AT-4/closed-1280-dark.png`, `evidence/AT-4/open-375-light.png`, `evidence/AT-4/open-375-dark.png`, `evidence/AT-4/open-768-light.png`, `evidence/AT-4/open-768-dark.png`, `evidence/AT-4/open-1280-light.png`, `evidence/AT-4/open-1280-dark.png`, `evidence/AT-4/row-375-light.txt`, `evidence/AT-4/row-375-dark.txt`, `evidence/AT-4/row-768-light.txt`, `evidence/AT-4/row-768-dark.txt`, `evidence/AT-4/row-1280-light.txt`, `evidence/AT-4/row-1280-dark.txt`
Observation: Each row file lists "More" first, then 3 chips, and "More" lists 13 items. The row scrolls sideways, so in each width the third chip is cut at the edge of the row. Some facts hold no number: "Sell high or buy low" shows "Tyler Allgeier: 12.7 a game over 4 weeks, 8.8 for the season" in some runs, and the Topics in "More" with no live fact show a line such as "Name a trade, get the read".

## AT-5: Tuesday puts the week recap first

App: site
Then: The first Suggestion is the week recap.
Files: `evidence/AT-5/steps.txt`, `evidence/AT-5/375-light.png`, `evidence/AT-5/375-dark.png`, `evidence/AT-5/row-375-light.txt`, `evidence/AT-5/row-375-dark.txt`, `evidence/AT-5/api-calls-light.json`, `evidence/AT-5/api-calls-dark.json`
Observation: The Given "no Topic of Lil Fridge is urgent" did not hold on the live data: Jev gave power_rankings a lift of 0.81 and 0.83, and week_recap 0.74, both above 0.7. The first chip is Power rankings and the second is Week recap, in both themes.

## AT-6: Jev lifts an urgent Topic to the top

App: site
Then: That Topic is the first Suggestion, above the order of the day.
Files: `evidence/AT-6/steps.txt`, `evidence/AT-6/375-light.png`, `evidence/AT-6/375-dark.png`, `evidence/AT-6/row-375-light.txt`, `evidence/AT-6/row-375-dark.txt`, `evidence/AT-6/api-calls-light.json`, `evidence/AT-6/api-calls-dark.json`
Observation: On Wednesday the order of the day starts with waiver_targets and weak_spots. The response lifts power_rankings (0.83, 0.84) and week_recap (0.75, 0.77) above 0.7, and the row shows Power rankings first, then Week recap, then Waiver targets.

## AT-7: An opened Topic drops off the Suggestions

App: site
Then: The power rankings Topic is not in the 3 Suggestions. It still shows in "More".
Files: `evidence/AT-7/steps.txt`, `evidence/AT-7/before-tap-375-light.png`, `evidence/AT-7/before-tap-375-dark.png`, `evidence/AT-7/after-reload-375-light.png`, `evidence/AT-7/after-reload-375-dark.png`, `evidence/AT-7/after-reload-more-375-light.png`, `evidence/AT-7/after-reload-more-375-dark.png`, `evidence/AT-7/row-after-reload-375-light.txt`, `evidence/AT-7/row-after-reload-375-dark.txt`, `evidence/AT-7/api-calls-light.json`, `evidence/AT-7/api-calls-dark.json`
Observation: Before the tap, Power rankings is the first chip. After the reload, the row holds no Power rankings chip, and "More" lists Power rankings as item 4 of 13. The light row file lists 4 chips after "More", because one chip was still leaving as the live Suggestions came in.

## AT-8: The top personal Suggestion builds on open

App: site
Then: The whole Answer shows at once, with no stream and no tool step.
Files: `evidence/AT-8/steps.txt`, `evidence/AT-8/recording-375-light.webm`, `evidence/AT-8/api-log.txt`, `evidence/AT-8/api-calls.json`, `evidence/AT-8/run.txt`, `evidence/AT-8/after-tap-375-light.png`, `evidence/AT-8/frame-33.7s-tap.png`, `evidence/AT-8/frame-34.6s-reading-the-rosters.png`, `evidence/AT-8/frame-36.2s-answer-blurred-in.png`, `evidence/AT-8/frame-36.4s-answer.png`
Observation: Jev lifts Power rankings and Week recap on this data, so the setup marks those two as opened; the first Suggestion is then Waiver targets, a personal Topic. The log shows "The head start builds the personal Topic waiver_targets on open" with one Claude call, then on the tap 30 s later "came from the store, with no Claude call", and the stream holds one text part with the id "kept". After the tap, the card shows the line "Reading the rosters…" for about 2.3 s, then the whole Answer fades in at once.

## AT-9: Loose words reach the right Topic

App: site
Then: The Answer is the next matchup of Lil Fridge for week 9, with the name of its opponent.
Files: `evidence/AT-9/steps.txt`, `evidence/AT-9/375-light.png`, `evidence/AT-9/375-dark.png`, `evidence/AT-9/api-calls.json`, `evidence/AT-9/api-calls-dark-reload.json`, `evidence/AT-9/api-log.txt`, `evidence/AT-9/page-text-375-light.txt`
Observation: The route response is `topic`, `next_matchup`, with fits_topic 0.82 and next_matchup 0.95 in the topic Choice. The Answer shows Lil Fridge 10-6 against behold the lamb 6-10, with "Read the full report".

## AT-10: A question about another team answers about that team

App: site
Then: The Answer is about Bo Girds, with the 9-7 record of Bo Girds, not the record of Lil Fridge.
Files: `evidence/AT-10/steps.txt`, `evidence/AT-10/375-light.png`, `evidence/AT-10/375-dark.png`, `evidence/AT-10/api-calls.json`, `evidence/AT-10/api-calls-dark-reload.json`, `evidence/AT-10/api-log.txt`, `evidence/AT-10/page-text-375-light.txt`
Observation: The route response is `free` with `names_team` 0.99, `team` 6 (Bo Girds), and the Suggestion your_season. The free answer reads "Bo Girds is 9-7 and ranked third. Their head-to-head record is 3-5, but they've scored the most points in the league at 921.62.", with "Checked" and a "Your season · Bo Girds" chip.

## AT-11: A stat lookup gets a free answer

App: site
Then: A short answer names the team with the most points for in weeks 1 to 8, and the number matches the standings data.
Files: `evidence/AT-11/steps.txt`, `evidence/AT-11/375-light.png`, `evidence/AT-11/375-dark.png`, `evidence/AT-11/api-calls.json`, `evidence/AT-11/api-calls-dark-reload.json`, `evidence/AT-11/api-log.txt`, `evidence/AT-11/page-text-375-light.txt`, `evidence/AT-11/standings-points-for.txt`
Observation: The answer reads "Bo Girds has scored the most points this season, with 921.62 through week 8. London Cooking is second with 918.99. Your team, Lil Fridge, is third with 909.55.", and the stream holds one tool step, `standings`, shown as "Reading the standings". The week 8 `page.json` gives the same top three (921.62, 918.99, 909.55). Three lower teams differ between the tool output and `page.json`: Maye d'force B with U 900.65 against 901.65, Return of T Mac 832.55 against 831.55, Teehee 885.98 against 885.88.

## AT-12: A half fit shows its Topic under the free answer

App: site
Then: One Suggestion chip of the top Topic shows under the answer.
Files: `evidence/AT-12/steps.txt`, `evidence/AT-12/375-light.png`, `evidence/AT-12/375-dark.png`, `evidence/AT-12/api-calls.json`, `evidence/AT-12/api-log.txt`
Observation: The route of "highest scoring team this season" gives fits_topic 0.59 and the Suggestion your_season. Under the checked answer, one chip "Your season" shows.

## AT-13: A question that the data cannot answer gets an honest miss

App: site
Then: The Answer says the site has no injury news, shows the 3 closest Topics, and hides the chips of the dock.
Files: `evidence/AT-13/steps.txt`, `evidence/AT-13/375-light.png`, `evidence/AT-13/375-dark.png`, `evidence/AT-13/api-calls.json`, `evidence/AT-13/api-calls-dark-reload.json`, `evidence/AT-13/api-log.txt`, `evidence/AT-13/page-text-375-light.txt`
Observation: The route is `miss` (fits_topic 0.09, data_can_answer 0.14). The card says "The site has no answer to that. It holds this season's league data and game stats, but no injury news, live game status, betting odds, news articles, or past seasons." with the closest Topics Your next matchup, How you stack up, and Week recap, and no Suggestion chips show above the ask box.

## AT-14: An honest miss writes a log entry

App: api
Then: The miss log holds one entry with the question text, the team, the time, and the 3 closest Topics.
Files: `evidence/AT-14/output.txt`, `evidence/AT-14/api-log.txt`
Observation: The miss log has 0 rows before the request. After the `miss` response, it holds one row: "is CeeDee Lamb playing sunday", roster 3, Lil Fridge, 2026-11-10T20:04:31-05:00, and ["next_matchup", "stack_up", "week_recap"].

## AT-15: A rule break gets a calm refusal

App: site
Then: A calm refusal shows. It holds no passphrase, no Claude text, and no tool step.
Files: `evidence/AT-15/steps.txt`, `evidence/AT-15/375-light.png`, `evidence/AT-15/375-dark.png`, `evidence/AT-15/api-calls.json`, `evidence/AT-15/api-calls-dark-reload.json`, `evidence/AT-15/api-log.txt`, `evidence/AT-15/page-text-375-light.txt`
Observation: The route is `refuse` (abuse 1.0). The card says "That is not a question the front door answers. Ask about your team, another team, or the league.", and it shows no step line. The API log of the run holds no line to api.anthropic.com.

## AT-16: An off-topic request gets an honest miss, not a poem

App: site
Then: The honest miss shows with the 3 closest Topics, and no poem shows.
Files: `evidence/AT-16/steps.txt`, `evidence/AT-16/375-light.png`, `evidence/AT-16/375-dark.png`, `evidence/AT-16/api-calls.json`, `evidence/AT-16/api-calls-dark-reload.json`, `evidence/AT-16/api-log.txt`, `evidence/AT-16/page-text-375-light.txt`
Observation: The route is `miss` (fits_topic 0.02, about_league 0.35). The honest miss shows with How you stack up, Week recap, and Weak spots, and no poem text shows.

## AT-17: The route eval hits 35 of 40

App: api
Then: At least 35 of the 40 questions with an expected route get that route.
Files: `evidence/AT-17/output.txt`, `evidence/AT-17/route-table.md`
Observation: The live run against jev-1.14.0 prints "Hits: 36 of 40." and the test passes. The table lists 43 questions, and the 4 misses are questions 7, 9, 12, and 31.

## AT-18: The data block of a Topic shows before the text

App: site
Then: The data block shows first, and the text streams under it after.
Files: `evidence/AT-18/steps.txt`, `evidence/AT-18/recording-375-light.webm`, `evidence/AT-18/api-calls.json`, `evidence/AT-18/api-log.txt`, `evidence/AT-18/end-375-light.png`, `evidence/AT-18/frame-08.50s-block-alone.png`, `evidence/AT-18/frame-09.25s-text-in-stream.png`, `evidence/AT-18/frame-09.50s-text-in-stream.png`, `evidence/AT-18/frame-10.50s-card-blank.png`, `evidence/AT-18/frame-10.75s-card-back-blurred.png`
Observation: At 8.50 s the card shows the block alone (QB, 7th of 12, 0 holes, and four slot rows); at 9.25 s and 9.50 s the text grows under it ("Your team has no true…"). The log shows one Claude call, so the Answer was not kept before. At 10.50 s, after the last word, the whole card and the question bubble go blank for about 0.2 s, then the card comes back blurred and sharpens.

## AT-19: Each tool call shows as a plain step

App: site
Then: Each tool call shows as a step in plain words, such as "Reading week 1…". No step and no copy names Jev, the Advisor, or the Finder.
Files: `evidence/AT-19/steps.txt`, `evidence/AT-19/recording-375-light.webm`, `evidence/AT-19/api-calls.json`, `evidence/AT-19/api-log.txt`, `evidence/AT-19/end-375-light.png`, `evidence/AT-19/page-text.txt`, `evidence/AT-19/copy-search.txt`
Observation: The stream holds one tool call, `week_results` with week 1, and the page shows it as "Reading week 1". The text of the page has 0 hits for Jev, Advisor, or Finder; the front-door source has 3 hits, two TypeScript type names (`FinderTrade`) and one code comment, and the export of `/` has none.

## AT-20: The check mark turns from checking to checked

App: site
Then: A "checking" mark shows, then turns into "checked" in the ink color, with no bounce.
Files: `evidence/AT-20/steps.txt`, `evidence/AT-20/recording-375-light.webm`, `evidence/AT-20/recording-375-dark.webm`, `evidence/AT-20/mark-light.txt`, `evidence/AT-20/mark-dark.txt`, `evidence/AT-20/api-calls-light.json`, `evidence/AT-20/api-calls-dark.json`, `evidence/AT-20/api-log-light.txt`, `evidence/AT-20/api-log-dark.txt`, `evidence/AT-20/end-375-light.png`, `evidence/AT-20/end-375-dark.png`, `evidence/AT-20/light-frame-10.3s-text-ended.png`, `evidence/AT-20/light-frame-10.4s-card-blank.png`, `evidence/AT-20/light-frame-10.6s-checked-blurred-in.png`, `evidence/AT-20/light-frame-10.8s-checked.png`, `evidence/AT-20/dark-frame-09.8s-text-ended.png`, `evidence/AT-20/dark-frame-09.9s-card-blank.png`, `evidence/AT-20/dark-frame-10.1s-checked-blurred-in.png`, `evidence/AT-20/dark-frame-10.3s-checked.png`
Observation: The DOM samples show "Checking" in the mute color for about 100 ms (light) and about 50 ms (dark), then "Checked" in the ink color, rgb(20, 20, 20) in light and rgb(255, 255, 255) in dark. In both recordings no frame shows "Checking": the text ends, the card goes blank for about 0.2 s, then it comes back blurred with "Checked". The dark run had a real failed check, so it also showed "Fixing a number…" and a second text before the mark.

## AT-21: A failed check rewrites the text

App: both
Then: The first text fades out, "Fixing a number…" shows, and a second text streams with "checked".
Files: `evidence/AT-21/steps.txt`, `evidence/AT-21/output.txt`, `evidence/AT-21/at-21-weak-spots-one-failed-claim.sse`, `evidence/AT-21/recording-375-light.webm`, `evidence/AT-21/replay-text-changes.txt`, `evidence/AT-21/replay-calls.json`, `evidence/AT-21/end-375-light.png`, `evidence/AT-21/frame-20.2s-first-text-fading.png`, `evidence/AT-21/frame-20.4s-blank.png`, `evidence/AT-21/frame-20.8s-second-text.png`, `evidence/AT-21/frame-23.2s-checked.png`, `evidence/AT-21/frame-25.4s-stale-after-key-check.png`, `evidence/AT-21/live-AT-20-dark-frame-8.3s-fixing-a-number.png`
Observation: The pytest run passes, and its stream gives the check states checking, fixing, checking, checked, with a data-fix part. In the replay, the first text fades out, the text area is blank for about 0.4 s, the second text shows, and "Checked" follows; no frame of the replay shows "Fixing a number…". The live dark run of AT-20 shows "Fixing a number…" under the block. The replayed Answer later shows "Your roster changed." with Refresh, because the recorded key comes from the test fixtures and is not a live key.

## AT-22: A second failed check gives the honest miss

App: api
Then: The stream ends with the honest miss, and it holds neither text.
Files: `evidence/AT-22/steps.txt`, `evidence/AT-22/output.txt`, `evidence/AT-22/at-22-weak-spots-two-failed-claims.sse`, `evidence/AT-22/replay-text-changes.txt`, `evidence/AT-22/replay-calls.json`, `evidence/AT-22/end-375-light.png`
Observation: The stream ends with check state `failed`, then `data-miss` with closest stack_up, waiver_targets, and trade_ideas, then `finish`. The stream holds the text-delta parts of both texts before the failed checks. In the replay, the card ends as the honest miss card with those three Topics and no text of the Answer.

## AT-23: A Topic Answer links to its page

App: site
Then: The power rankings page opens at `/rankings/`.
Files: `evidence/AT-23/steps.txt`, `evidence/AT-23/answer-375-light.png`, `evidence/AT-23/answer-375-dark.png`, `evidence/AT-23/page-375-light.png`, `evidence/AT-23/page-375-dark.png`, `evidence/AT-23/url-375-light.txt`, `evidence/AT-23/url-375-dark.txt`
Observation: The Power rankings Answer shows "Read the full report". After the tap, the URL is `http://127.0.0.1:4173/rankings/` and the power rankings page shows.

## AT-24: The trade check shows the Lean, the Case, and the Bullets

App: site
Then: The Answer shows the Lean, the Case, the top Bullets, and a link to the Trade page.
Files: `evidence/AT-24/steps.txt`, `evidence/AT-24/recording-375-light.webm`, `evidence/AT-24/375-light.png`, `evidence/AT-24/375-dark.png`, `evidence/AT-24/768-light.png`, `evidence/AT-24/768-dark.png`, `evidence/AT-24/1280-light.png`, `evidence/AT-24/1280-dark.png`, `evidence/AT-24/api-calls.json`, `evidence/AT-24/api-log.txt`, `evidence/AT-24/page-text-375-light.txt`
Observation: The question is "is Courtland Sutton for Zay Flowers fair" (Sutton is on Lil Fridge and Flowers on Bo Girds in the week 8 rosters and now). The route is `topic`, `trade_check`; the picks are Courtland Sutton (roster 3) and Zay Flowers (roster 6), both sure. The Answer shows the Lean "Send it" on a five-step scale, the Case, three "for" Bullets, and "Open it on the Trade page"; the result comes from the data-answer part of the trade-check stream.

## AT-25: The Case leads with the reason for its Lean

App: site
Then: The first sentence of the Case gives the reason for the Lean, and the fairness line agrees with the Lean.
Files: `evidence/AT-25/steps.txt`, `evidence/AT-25/case-and-lean.txt`, `evidence/AT-25/375-light.png`
Observation: The Lean is "Send it". The first sentence of the Case is "If you trust that Flowers' full season matters more than his last few weeks, this is a move you make." The fairness state is lopsided with `gives_more` 6, and the site line is "It helps Lil Fridge more."

## AT-26: Trade ideas come from the real Finder in CPC

App: site
Then: The Answer shows trade offers from the real `/find` output, each for a weak spot of Lil Fridge.
Files: `evidence/AT-26/steps.txt`, `evidence/AT-26/recording-375-light.webm`, `evidence/AT-26/375-light.png`, `evidence/AT-26/375-dark.png`, `evidence/AT-26/768-light.png`, `evidence/AT-26/768-dark.png`, `evidence/AT-26/1280-light.png`, `evidence/AT-26/1280-dark.png`, `evidence/AT-26/api-calls.json`, `evidence/AT-26/api-log.txt`, `evidence/AT-26/page-text-375-light.txt`
Observation: The stream of `/clients/cpc/trade-ideas` gives the steps "Checked 11 teams for a fit", "Built 52 offers", "Weighed 52 offers", "Picked the best 2", then two offers, both with Teehee: McCaffrey for Amon-Ra St. Brown and Tee Higgins, and McCaffrey for St. Brown. Each offer says it adds WRs in the top 36 ("from 2 to 4", "from 2 to 3"). The trade ideas fact names the QB ("Offers for your QB, 7th of 12"), and the weak spots Answer names RB and QB as the weakest spots; neither offer adds a QB or an RB.

## AT-27: Sell high or buy low names players of Your team

App: site
Then: The Answer names at least one player on the roster of Lil Fridge to sell, with the reason.
Files: `evidence/AT-27/steps.txt`, `evidence/AT-27/recording-375-light.webm`, `evidence/AT-27/375-light.png`, `evidence/AT-27/375-dark.png`, `evidence/AT-27/api-calls.json`, `evidence/AT-27/api-log.txt`, `evidence/AT-27/page-text-375-light.txt`, `evidence/AT-27/roster-lil-fridge.txt`
Observation: The Answer names Tyler Allgeier (RB, ARI), who is on the live roster of Lil Fridge. The reason: "Sell Tyler Allgeier now, since his hot month sits above a weaker season and the schedule ahead gets harder.", with two Bullets (12.7 points a game over 4 weeks against 8.8 for the season, and four hard matchups in weeks 10 to 13).

## AT-28: The steps of a trade Answer show during the wait

App: site
Then: Plain steps, such as "Weighed 6 offers", show one by one before the whole Answer shows.
Files: `evidence/AT-28/steps.txt`, `evidence/AT-28/recording-375-light.webm`, `evidence/AT-28/contact-sheet-1fps.png`, `evidence/AT-28/frame-04s-looking-for-trades.png`, `evidence/AT-28/frame-06s-checked-11-teams.png`, `evidence/AT-28/frame-07s-built-52-offers.png`, `evidence/AT-28/frame-08s-weighed-52-offers.png`, `evidence/AT-28/frame-50s-picked-the-best-2.png`, `evidence/AT-28/frame-53s-whole-answer.png`
Observation: The frames show "Looking for trades…" at 4 s, then "Checked 11 teams for a fit" at 6 s, "Built 52 offers" at 7 s, "Weighed 52 offers" at 8 s, and "Picked the best 2" at 50 s, each added under the one before. The whole Answer shows at 53 s.

## AT-29: A kept Answer comes back at once and costs nothing

App: api
Then: The kept Answer comes back with no Claude call, and the team count stays the same.
Files: `evidence/AT-29/output.txt`, `evidence/AT-29/api-log.txt`
Observation: Both requests return the same key and a text part with the id "kept", with only the check state `checked`. The log says "The personal Topic weak_spots came from the store, with no Claude call" twice and has no line to api.anthropic.com, and the team count is 9 before, 9 after the first, and 9 after the second.

## AT-30: The Thread reads like a chat, and older Answers fold

App: site
Then: The weak spots Answer shows at the bottom, open. The week recap folds to one line with its question and one fact.
Files: `evidence/AT-30/steps.txt`, `evidence/AT-30/375-light.png`, `evidence/AT-30/375-dark.png`, `evidence/AT-30/768-light.png`, `evidence/AT-30/768-dark.png`, `evidence/AT-30/1280-light.png`, `evidence/AT-30/1280-dark.png`, `evidence/AT-30/api-calls-375-light.json`
Observation: Each shot shows one line "Week recap · You scored 80.11, 12th of 12" with a chevron, and under it the Weak spots question and its open Answer with the block and the text.

## AT-31: A fold opens in place and folds again

App: site
Then: The week recap opens in place at its top under the header, then folds to one line.
Files: `evidence/AT-31/steps.txt`, `evidence/AT-31/recording-375-light.webm`, `evidence/AT-31/opened-375-light.png`, `evidence/AT-31/folded-again-375-light.png`, `evidence/AT-31/measures.txt`
Observation: After the first tap, the Week recap Answer is open, and its top sits at 118 px, the bottom of the Thread header. After the second tap, its button has `aria-expanded` false and the shot shows the one line again.

## AT-32: The Thread stays for the week

App: site
Then: The Thread shows the same two Answers.
Files: `evidence/AT-32/steps.txt`, `evidence/AT-32/before-375-light.png`, `evidence/AT-32/before-375-dark.png`, `evidence/AT-32/after-375-light.png`, `evidence/AT-32/after-375-dark.png`
Observation: Before the close, the Thread holds Week recap (folded) and Power rankings (open). The new context on the same day shows the same two entries.

## AT-33: A new week starts an empty Thread

App: site
Then: The Thread is empty.
Files: `evidence/AT-33/steps.txt`, `evidence/AT-33/before-rebuild-375-light.png`, `evidence/AT-33/before-rebuild-375-dark.png`, `evidence/AT-33/after-rebuild-375-light.png`, `evidence/AT-33/after-rebuild-375-dark.png`, `evidence/AT-33/thread-store-after-375-light.txt`, `evidence/AT-33/thread-store-after-375-dark.txt`
Observation: This test uses the real week 9 for the rebuild. Before, the week 8 site shows two Answers; after, the week 9 site ("WK 09", "Week 9") shows "Ask about Lil Fridge" with no Answer, and local storage holds `{"3":{"week":9,"entries":[]}}`.

## AT-34: A stale Answer shows dimmed with Refresh

App: site
Then: The weak spots Answer shows dimmed with "Your roster changed since <day>. [Refresh]", and no "checked" mark.
Files: `evidence/AT-34/steps.txt`, `evidence/AT-34/before-375-light.png`, `evidence/AT-34/before-375-dark.png`, `evidence/AT-34/after-375-light.png`, `evidence/AT-34/after-375-dark.png`, `evidence/AT-34/marks-after-375-light.txt`, `evidence/AT-34/marks-after-375-dark.txt`, `evidence/AT-34/api-calls-after-light.json`, `evidence/AT-34/api-calls-after-dark.json`
Observation: The key check response gives `current` false and `kept_at` 2026-11-10T20:06:52-05:00 for the weak spots key. The Answer shows dimmed under "Your roster changed since Tuesday." and a Refresh button, and the page holds 0 "Checked" marks.

## AT-35: Refresh gets a fresh Answer

App: site
Then: A fresh weak spots Answer streams with "checked", and it is no longer dimmed.
Files: `evidence/AT-35/steps.txt`, `evidence/AT-35/recording-375-light.webm`, `evidence/AT-35/end-375-light.png`, `evidence/AT-35/end-state.txt`, `evidence/AT-35/team-count.txt`, `evidence/AT-35/api-calls.json`, `evidence/AT-35/api-log.txt`
Observation: After the tap on Refresh, the log shows two Claude calls and "The personal Topic weak_spots ended as checked, with 2 texts", and the stream ends with `checked`. The end shot shows a new text, 0 articles have `data-stale`, and the team count goes from 9 to 10.

## AT-36: Clear empties the Thread with no confirm

App: site
Then: The Thread is empty at once, with no confirm, and the opened Topics stay off the Suggestions.
Files: `evidence/AT-36/steps.txt`, `evidence/AT-36/before-375-light.png`, `evidence/AT-36/before-375-dark.png`, `evidence/AT-36/after-375-light.png`, `evidence/AT-36/after-375-dark.png`, `evidence/AT-36/after-375-light.txt`, `evidence/AT-36/after-375-dark.txt`
Observation: 150 ms after the tap on Clear, the page holds 0 articles, and no browser dialog showed. The row after Clear is Waiver targets, Weak spots, Playoff race, with no Week recap and no Power rankings.

## AT-37: The team cap shows its calm line

App: site
Then: The line "That's 25 questions today. Ask again tomorrow." shows with the 3 closest Topics, and no manager is named.
Files: `evidence/AT-37/steps.txt`, `evidence/AT-37/seed.txt`, `evidence/AT-37/375-light.png`, `evidence/AT-37/375-dark.png`, `evidence/AT-37/api-calls.json`, `evidence/AT-37/api-calls-dark-reload.json`, `evidence/AT-37/api-log.txt`, `evidence/AT-37/page-text-375-light.txt`
Observation: The seed brings the count of Lil Fridge today to 25 (10 real Answers plus 15 seeded rows). The card says "That's 25 questions today. Ask again tomorrow." with Your season, Playoff race, and Power rankings, and names no manager; the log says "A free answer stopped at the team cap, with no Claude call" and has no line to api.anthropic.com.

## AT-38: The league cap shows its calm line

App: site
Then: CPC shows the line "The league's question budget is used up for this month. It resets on Dec 1." NorCal gets a free answer.
Files: `evidence/AT-38/steps.txt`, `evidence/AT-38/seed.txt`, `evidence/AT-38/cpc-375-light.png`, `evidence/AT-38/cpc-375-dark.png`, `evidence/AT-38/norcal-375-light.png`, `evidence/AT-38/norcal-375-dark.png`, `evidence/AT-38/cpc-api-calls-light.json`, `evidence/AT-38/cpc-api-calls-dark.json`, `evidence/AT-38/norcal-api-calls-light.json`, `evidence/AT-38/api-log-cpc.txt`, `evidence/AT-38/api-log-norcal.txt`
Observation: With CPC at $25.00, the CPC card says "The league's question budget is used up for this month." and "It resets on Dec 1.", and the log says "stopped at the league cap, with no Claude call". NorCal, at $0, gets a checked free answer that names Mitseeker5000 at 1,130.34 points.

## AT-39: The 80% mark logs one alert

App: api
Then: The API logs one alert, and a later answer logs no second alert.
Files: `evidence/AT-39/output.txt`, `evidence/AT-39/api-log.txt`
Observation: The seed sets $19.997 in place of $19.90, because one free answer costs $0.003 to $0.006 (a first try at $19.99 ended at $19.9998 with no alert). The first answer takes the month to $20.0007, and the log holds one WARNING "The league cpc used $20.00 of its $25.00 Claude budget for 2026-11, past 80%."; the second answer takes it to $20.0047 with no second WARNING, and the alerts table holds 1 row.

## AT-40: Past a cap, what costs nothing still works

App: site
Then: The power rankings Answer shows in full.
Files: `evidence/AT-40/steps.txt`, `evidence/AT-40/375-light.png`, `evidence/AT-40/375-dark.png`
Observation: With the team cap of AT-37 in the store, the Power rankings Answer shows its rank, move, record, three team rows, the text, and "Read the full report".

## AT-41: The ask endpoint needs the passphrase

App: api
Then: Both get 401, and no Jev or Claude call runs.
Files: `evidence/AT-41/output.txt`, `evidence/AT-41/api-log.txt`
Observation: Both requests get "HTTP/1.1 401 Unauthorized" with no body. The log of the two requests holds only the two 401 lines, with no typesafe_sdk line and no api.anthropic.com line.

## AT-42: The ask box glides to the bottom on the first question

App: site
Then: The ask box glides to the bottom in one move, and the question shows above it.
Files: `evidence/AT-42/steps.txt`, `evidence/AT-42/recording-375-light.webm`, `evidence/AT-42/ask-box-top.txt`, `evidence/AT-42/end-375-light.png`
Observation: The top of the ask box moves from 386 px through 398, 463, 528, 594, 638, 655, 662, 666, 667 to 668 px in about 450 ms, always down. The end shot shows the question above the ask box.

## AT-43: A tapped Suggestion morphs into the question

App: site
Then: The chip morphs into the question bubble as one surface.
Files: `evidence/AT-43/steps.txt`, `evidence/AT-43/recording-375-light.webm`, `evidence/AT-43/run.txt`, `evidence/AT-43/end-375-light.png`, `evidence/AT-43/contact-sheet-20fps-from-5.40s.png`, `evidence/AT-43/frame-5.40s-before-tap.png`, `evidence/AT-43/frame-5.50s-chip-rising.png`, `evidence/AT-43/frame-5.60s-chip-rising.png`, `evidence/AT-43/frame-5.65s-chip-to-bubble.png`, `evidence/AT-43/frame-5.70s-bubble.png`
Observation: The tapped chip is "Power rankings: 6th, down 5". From 5.50 s to 5.60 s the chip, with its name and fact, moves up and to the right; at 5.65 s it shows as a grey pill with the name only at the place of the question; at 5.70 s it is the dark question bubble "Power rankings", and the Answer fades in under it.

## AT-44: The words sharpen from a blur as they stream

App: site
Then: Each new word shows blurred, then sharp.
Files: `evidence/AT-44/steps.txt`, `evidence/AT-44/recording-375-light.webm`, `evidence/AT-44/frame-7.32s-blurred.png`, `evidence/AT-44/frame-7.36s-blurred.png`, `evidence/AT-44/frame-7.44s-sharper.png`, `evidence/AT-44/frame-7.48s-card-blank.png`, `evidence/AT-44/frame-9.10s-sharp.png`, `evidence/AT-44/frames-7.32s-to-7.48s-strip.png`
Observation: The stream has 18 text parts, but the whole text shows in one block within about 0.1 s: at 7.32 s one blurred line, at 7.36 s the full text blurred, at 7.44 s less blurred. At 7.48 s the card goes blank for about 1.4 s, and at 9.10 s the text shows sharp with "Checked".

## AT-45: The front door wears the brand of each league

App: site
Then: Each front door uses the fonts, the band, and the accent of its client, in light and dark.
Files: `evidence/AT-45/steps.txt`, 12 shots `evidence/AT-45/cpc-<width>-<theme>.png` and 12 style files `evidence/AT-45/cpc-<width>-<theme>-style.txt`, 12 shots `evidence/AT-45/norcal-<width>-<theme>.png` and 12 style files `evidence/AT-45/norcal-<width>-<theme>-style.txt`, for widths 375, 768, 1280 and themes light, dark
Observation: The CPC shots show the CPC logo, Space Grotesk ("spaceGrotesk" in the style files), and the accent #b8342a; the NorCal shots show the name "NORCAL APEX 6" in the band, the accent #c2410c in the style files, and a warm paper color in light. The style files give the same font, spaceGrotesk, for both clients. Each client shows one Week recap Answer in both themes; the NorCal team is puurdygood (roster 1).

## AT-46: Reduced motion keeps only the fades

App: site
Then: The ask box and the Answer fade in place, with no glide, no blur, and no spring.
Files: `evidence/AT-46/steps.txt`, `evidence/AT-46/recording-375-light.webm`, `evidence/AT-46/ask-box-samples.txt`, `evidence/AT-46/end-375-light.png`
Observation: Under `prefers-reduced-motion: reduce`, the first sample 50 ms after Send has the ask box top at 644 px and the next at 668 px, from 386 px before; its opacity is 1 in every sample. At the end, no element has a CSS filter.

## AT-47: The ask box clears the home bar of an iPhone

App: site
Then: The ask box sits fully above the home bar.
Files: `evidence/AT-47/steps.txt`, `evidence/AT-47/iphone-393-light.png`, `evidence/AT-47/iphone-393-dark.png`, `evidence/AT-47/iphone-393-light-home-bar-marked.png`, `evidence/AT-47/iphone-393-dark-home-bar-marked.png`, `evidence/AT-47/measures-light.txt`, `evidence/AT-47/measures-dark.txt`
Observation: The device emulation is Playwright Chromium at 393x852, scale 3, with the CDP command `Emulation.setSafeAreaInsetsOverride` (bottom 34 px); the page has `viewport-fit=cover` and measures `env(safe-area-inset-bottom)` as 34 px. The ask box ends at 728 px, the dock ends above the home bar zone, and the zone starts at 818 px.

## AT-48: The menu keeps four links

App: site
Then: Each shows Home, Week 8, Power Rankings, and Managers, and nothing else.
Files: `evidence/AT-48/steps.txt`, `evidence/AT-48/cpc-375-light.png`, `evidence/AT-48/cpc-375-dark.png`, `evidence/AT-48/cpc-1280-light.png`, `evidence/AT-48/cpc-1280-dark.png`, `evidence/AT-48/norcal-375-light.png`, `evidence/AT-48/norcal-375-dark.png`, `evidence/AT-48/norcal-1280-light.png`, `evidence/AT-48/norcal-1280-dark.png`, and one `-links.txt` file for each shot
Observation: At 1280 px the header nav of each client shows Home, Week 8, Power Rankings, and Managers. At 375 px the dock shows Home, Week 8, Rankings, and Managers, with the label "Rankings" in place of "Power Rankings". The link files also list three links with no text to week pages, which sit in the closed "WK 08" week picker.

## AT-49: Every page stays

App: site
Then: Each page renders as before the spec.
Files: `evidence/AT-49/steps.txt`, `evidence/AT-49/week-08-375-light.png`, `evidence/AT-49/rankings-375-light.png`, `evidence/AT-49/managers-375-light.png`, `evidence/AT-49/midseason-375-light.png`, `evidence/AT-49/analyze-375-light.png`
Observation: Each of the five pages renders with its hero and content. The rankings page says "Week 9 // Power Rankings" and the managers page "through week 9", because the season files hold the week 9 state. The `/analyze/` shot shows the league passphrase sheet over the page, because this context stored no passphrase. The round took no shots of these pages before the spec, so no side-by-side comparison is in the files.

## AT-50: `/` has no hero and no tool tiles

App: site
Then: No hero, no four numbers, no midseason takeover, and no tool tiles show.
Files: `evidence/AT-50/steps.json`, `evidence/AT-50/375-light.png`, `evidence/AT-50/375-dark.png`, `evidence/AT-50/768-light.png`, `evidence/AT-50/768-dark.png`, `evidence/AT-50/1280-light.png`, `evidence/AT-50/1280-dark.png`
Observation: Each shot shows the band, "Ask about Lil Fridge", the Suggestion chips, the ask box, and the menu or dock. No hero card, no row of four numbers, no midseason block, and no tool tile shows.

## AT-51: The weekly build writes the league Topic Answers

App: pipeline
Then: The published week holds an Answer of each of the 7 league Topics for each of the 12 teams.
Files: `evidence/AT-51/output.txt`
Observation: `clients/cpc/published/2026/week-08/topics.json` holds 12 teams with 7 Answers each, 84 in all, over the 7 league Topics. The command is `make page-json`, the step of the build that writes `topics.json` with no Sleeper refetch and no Claude call; its new `topics.json` differs from the published one only in the your_season Answers, which read the season `managers.json` that now holds the week 9 state.

## AT-52: ADR 0031 records the manager text

App: both
Then: It says what goes to TypeSafe and to Anthropic, that the miss log lives on Fly, and that each entry stays 90 days.
Files: `evidence/AT-52/output.txt`
Observation: `docs/adr/0031-the-text-that-managers-type.md` has the sections "What goes to TypeSafe", "What goes to Anthropic", and "The miss log". The miss log section says "one SQLite file per client on the Fly volume, at `CORNERSTONE_ASK_DIR`, which is `/data/ask` on Fly" and "Each entry stays 90 days."

## AT-53: The miss log stays out of the repo

App: api
Then: No file of the miss log shows.
Files: `evidence/AT-53/output.txt`
Observation: The store of the round sits at `<scratchpad>/ask/` with `cpc.sqlite` (5 miss rows, row 1 from AT-14), outside the repo; `fly.toml` sets `/data/ask`, and `.gitignore` lists `data/ask/`. After the API stopped, `git status` lists no file outside the evidence of this round, and `git ls-files` has no `.sqlite` file and no `data/ask/` file.

## AT-54: A past season gets an honest miss

App: site
Then: The honest miss shows, and no answer names a past champion.
Files: `evidence/AT-54/steps.txt`, `evidence/AT-54/375-light.png`, `evidence/AT-54/375-dark.png`, `evidence/AT-54/api-calls.json`, `evidence/AT-54/api-calls-dark-reload.json`, `evidence/AT-54/api-log.txt`, `evidence/AT-54/page-text-375-light.txt`
Observation: The route is `miss` (data_can_answer 0.03). The honest miss card shows with Playoff race, Week recap, and Your season, and it names no team as a champion.

## AT-55: No control stops a stream

App: site
Then: No stop control shows.
Files: `evidence/AT-55/steps.txt`, `evidence/AT-55/during-stream-375-light.png`, `evidence/AT-55/visible-buttons-during-stream.txt`
Observation: At the shot, one article has `aria-busy` true and its first step shows. The visible buttons are the theme switch, the team button, Clear, More, three Suggestion chips, and Send; none is a stop control.

## AT-56: The weekly report keeps its content

App: pipeline
Then: The `page.json` of week 8 is the same on both.
Files: `evidence/AT-56/output.txt`
Observation: `make page-json CLIENT=cpc WEEK=8` ran on `front-door` (bfb301df) and in a detached worktree of `origin/main` (777bde7c); the full build was not run, because it writes new Claude text for each chapter. The two `page.json` files have no diff and the same SHA-256, and each equals the committed build file; `git diff origin/main HEAD` of the published week 8 shows only the new `topics.json`.

## AT-57: The API keeps no Thread and asks for no login

App: api
Then: No table holds a Thread, an account, or a login.
Files: `evidence/AT-57/output.txt`
Observation: The store holds the tables `answers` (key, topic, roster_id, answer, kept_at), `spend`, `alerts`, and `misses` for each client. The eggs store holds `eggs` and `claims`; no table is named or shaped as a Thread, an account, or a login.

## AT-58: An unsure player pick opens the Trade page

App: site
Then: The Answer opens the Trade page with the form, and fills no player that Jev is unsure of.
Files: `evidence/AT-58/steps.txt`, `evidence/AT-58/answer-375-light.png`, `evidence/AT-58/answer-375-dark.png`, `evidence/AT-58/trade-page-375-light.png`, `evidence/AT-58/trade-page-375-dark.png`, `evidence/AT-58/answer-text.txt`, `evidence/AT-58/api-calls.json`, `evidence/AT-58/api-log.txt`
Observation: The picks are Derrick Henry (0.68, sure false) and Justin Jefferson (0.16, sure false), and the answer part is a form with no gives and no gets. The Answer says "Name the players to check that trade." with "Open the Trade page", whose link is `/analyze/?team=3`, and the URL after the tap is `/analyze/?team=3`. The dark shot of the Trade page shows the form with Your Team (Lil Fridge) and Team Two (no team yet), and no player added on either side; the light shot shows only the hero of the page, 5 s after the tap, with no form yet.
