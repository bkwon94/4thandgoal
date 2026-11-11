# Front door: evidence

Spec: `.scratch/front-door/PRD.md`. Acceptance tests: `.scratch/front-door/ACCEPTANCE.md`.
Built from: `99d00125`, on 2026-11-11, `4b8c83a0` for AT-18, AT-20, AT-31, AT-42, AT-43, AT-46, AT-60, AT-62, and AT-68, and `a3f241e3` for AT-1 and AT-8. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 1 min for 2 site tests with a `steps.json` (the runner total, 63.2 s, for AT-1 and AT-50). The driver tests took about 2 h of wall time in three parallel parts.

AT-5 is retired, so it has no entry.

## How the round ran

### The site screenshot tests

- The flag. The CPC and NorCal builds set `front_door = true` in `client.toml`. AT-59 used a CPC build with `front_door = false`. Both files are back as committed.
- The week. To match the setup (latest week 8), the round moved `clients/cpc/published/2026/week-09/` and `clients/norcal/published/2026/week-09/` out of the repo for the builds. AT-33 put the CPC week 9 back for its rebuild. Both folders are back. The season files (`managers.json`, `rankings.json`) stay at their week 9 state, so the manager page says "after week 9".
- The API. The API ran on this machine on port 8080 as `make -C apps/api api-evidence` runs it: the passphrase `localtest`, a limit of 600 a minute, the origin `http://127.0.0.1:4173`, and `CORNERSTONE_ASK_DIR` in an empty temp folder outside the repo. It called the real Jev and the real Claude, and read live Sleeper data. For AT-34 only, the round restarted it with the launcher of round 1 (scratchpad `driver/launch_api.py`), whose flag file adds one player to the live roster of Lil Fridge.
- The live data. The API reads the league now, after the week 9 games, and the live team name of roster 5 is "Puka Deez...", where the week 8 page says "London Cooking". The league Topics read the published week 8. The API clock is the real clock, Wednesday 2026-11-11.
- The site tests. The evidence runner (`pnpm --dir apps/site evidence front-door AT-1 AT-50`) took the shots of AT-1 and AT-50. Each other test needs a step that no runner verb covers: a stored team, the passphrase, a fixed day, or the API calls of the run. Those ran in a Playwright driver (scratchpad `site/driver/site.mjs`, from the round 2 driver), against the static export on `http://127.0.0.1:4173` with a `404.html` fallback. The driver shifts `Date` in the page to Wednesday 2026-11-04 10:00 America/Los_Angeles (Tuesday 2026-11-03 for AT-5); the timers stay real, so a reload starts a fresh count. It saves each API call with its full body in `api-calls*.json`. Each folder has a `steps.txt`.
- A typed test makes one live run at 375 px light, then opens `/` with the local storage of that run at each other width and theme, so those shots show the kept Answer with no new call. Before each live run, the kept free answers of the team leave the answer store, so each free answer runs with its tools.
- The shots are full-page shots. The ask box and the bottom dock are fixed, so in a full-page shot they can cover a band of a long Answer. Each `answer-text*.txt` holds the whole text of the Answer.
- The caps. AT-37 seeded the team count of Lil Fridge to 25. AT-38 reset that count to 0 and seeded CPC to $25.00, then removed the seed. Each `seed.txt` holds the commands.
- AT-49 compares each page with a build of `origin/main` (1d7bfc0d) in a detached worktree, with week 9 hidden too. The worktree is removed.
- After the round, `git checkout -- clients/` put back each file that the builds and the live API touched.

### The motion and stream tests

- Built from `99d00125` on 2026-11-11, in a detached worktree of the head. The CPC build set `front_door = true`, and the round moved `clients/cpc/published/2026/week-09/` and `clients/norcal/published/2026/week-09/` out of that worktree, so the latest week was 8.
- The site was the static export, built with `NEXT_PUBLIC_API_URL=http://localhost:8081`, served on `http://127.0.0.1:4174` with a `404.html` fallback.
- The API ran on port 8081 with the passphrase `localtest`, the origin `http://127.0.0.1:4174`, and an empty `CORNERSTONE_ASK_DIR` outside the repo. It called the real Jev and the real Claude and read live Sleeper data. The launcher has one seam: a flag file adds one player to the live roster of Lil Fridge. Only AT-35 turned it on, for the player `4046`.
- The driver (scratchpad `driver/motion.mjs`) runs Playwright Chromium at 375x812 with the page date shifted to Wednesday 2026-11-04 10:00 America/Los_Angeles. It records the screen and samples the DOM on each animation frame. A time in a samples file is a time in the recording. The recording runs about 0.1 s to 0.2 s behind the sample times.
- AT-69 ran in Playwright WebKit with the iPhone 15 profile and a fake keyboard (scratchpad `driver/at69.mjs`). AT-21 and AT-61 ran a FakeJev pytest in the worktree, then replayed the saved stream on port 8082.
- Live Claude and Jev vary. Some weak spots runs ended as an honest miss. AT-8, AT-18, and AT-20 keep each run, and each `steps.txt` names the runs. Before AT-31 and AT-35, the round asked the API for weak spots once more, so the store kept a checked Answer.
- Each folder holds a `steps.txt` that says how its files were made.

### The tests recorded again

Built from `4b8c83a0` on 2026-11-11, in the Spec worktree. The CPC build set `front_door = true` and moved `clients/*/published/2026/week-09/` out, so the latest week was 8. The static export was served on `http://127.0.0.1:4173`, and the API ran on port 8080 with an empty answer store, real Jev, real Claude, and live Sleeper data. The live league read week 10. Each folder has a `steps.txt` that says how its files were made. The tests recorded again are the tests that tickets 44 to 48 changed, and the tests whose text Brian revised.

### The API and pipeline tests

These ran in a detached worktree of `99d00125`, with the API on port 8092 and an empty `CORNERSTONE_ASK_DIR` outside the repo. They called the real Jev and the real Claude. AT-51 and AT-56 ran `make page-json`, as each `output.txt` explains.

## AT-1: The first visit asks for Your team with no skip

App: site
Then: A sheet lists the 12 teams of CPC, and it has no skip, no close, and no login.
Files: `evidence/AT-1/steps.json`, `evidence/AT-1/steps.txt`, `evidence/AT-1/sheet-rows.txt`, `evidence/AT-1/sheet-top-375-light.png`, `evidence/AT-1/sheet-top-375-dark.png`, `evidence/AT-1/sheet-top-768-light.png`, `evidence/AT-1/sheet-top-768-dark.png`, `evidence/AT-1/sheet-top-1280-light.png`, `evidence/AT-1/sheet-top-1280-dark.png`, `evidence/AT-1/sheet-end-375-light.png`, `evidence/AT-1/sheet-end-375-dark.png`, `evidence/AT-1/sheet-end-768-light.png`, `evidence/AT-1/sheet-end-768-dark.png`, `evidence/AT-1/sheet-end-1280-light.png`, `evidence/AT-1/sheet-end-1280-dark.png`
Observation: Each sheet-top shot shows the sheet "Which team is yours?" from All You Need Is Love down; at 768 px and 1280 px the 11th row sits at the scroll edge. Each sheet-end shot shows the same list scrolled to its end, down to the 12th row Unsolicited Dak Picks. sheet-rows.txt lists the same 12 rows at each width and theme, and the 12 team buttons are the only controls in the sheet, with no skip, close, or login control.

## AT-2: The browser keeps Your team

App: site
Then: The front door shows the Suggestions of Lil Fridge, and no sheet shows.
Files: `evidence/AT-2/steps.txt`, `evidence/AT-2/after-reload-375-dark.png`, `evidence/AT-2/after-reload-375-light.png`, `evidence/AT-2/after-reload-dialogs-375-dark.txt`, `evidence/AT-2/after-reload-dialogs-375-light.txt`, `evidence/AT-2/before-reload-375-dark.png`, `evidence/AT-2/before-reload-375-light.png`, `evidence/AT-2/sheet-375-dark.png`, `evidence/AT-2/sheet-375-light.png`
Observation: Before and after the reload, the page shows "Ask about Lil Fridge" with More and 3 Suggestion chips, and no sheet. The text files count 0 dialogs after the reload, and `cpc.your-team` is 3.

## AT-3: A change of Your team keeps each Thread

App: site
Then: Bo Girds shows an empty Thread, and Lil Fridge shows its week recap Answer again.
Files: `evidence/AT-3/steps.txt`, `evidence/AT-3/1-lil-fridge-recap-375-dark.png`, `evidence/AT-3/1-lil-fridge-recap-375-light.png`, `evidence/AT-3/2-bo-girds-375-dark.png`, `evidence/AT-3/2-bo-girds-375-light.png`, `evidence/AT-3/3-lil-fridge-again-375-dark.png`, `evidence/AT-3/3-lil-fridge-again-375-light.png`, `evidence/AT-3/articles-375-dark.txt`, `evidence/AT-3/articles-375-light.txt`
Observation: Shot 2 shows "Ask about Bo Girds" with its Suggestions and no Answer, and the articles file counts 0 articles for Bo Girds. Shot 3 shows the Thread of Lil Fridge with the Week recap Answer (80.11, 12th of 12) as in shot 1.

## AT-4: Three Suggestions with a fact each, plus More

App: site
Then: 3 Suggestion chips show, each with a Topic name and one short fact, and "More" leads the row. A tap on "More" lists all 13 Topics.
Files: `evidence/AT-4/steps.txt`, `evidence/AT-4/api-calls.json`, `evidence/AT-4/closed-1280-dark.png`, `evidence/AT-4/closed-1280-light.png`, `evidence/AT-4/closed-375-dark.png`, `evidence/AT-4/closed-375-light.png`, `evidence/AT-4/closed-768-dark.png`, `evidence/AT-4/closed-768-light.png`, `evidence/AT-4/open-1280-dark.png`, `evidence/AT-4/open-1280-light.png`, `evidence/AT-4/open-375-dark.png`, `evidence/AT-4/open-375-light.png`, `evidence/AT-4/open-768-dark.png`, `evidence/AT-4/open-768-light.png`, `evidence/AT-4/row-1280-dark.txt`, `evidence/AT-4/row-1280-light.txt`, `evidence/AT-4/row-375-dark.txt`, `evidence/AT-4/row-375-light.txt`, `evidence/AT-4/row-768-dark.txt`, `evidence/AT-4/row-768-light.txt`
Observation: Each row file lists "More" first, then 3 chips, each with a Topic name and one short fact, such as "6th, down 5", and "More" lists 13 items. The chips wrap to a second line and each chip box sits inside the window. Some facts hold text as well as a number, such as "Tyler Allgeier: 12.7 a game over 4 weeks, 8.8 for the season", and the open list at 768 px runs under the bottom dock in the full-page shot.

## AT-6: Jev lifts an urgent Topic to the top

App: site
Then: That Topic is the first Suggestion, above the order of the day.
Files: `evidence/AT-6/steps.txt`, `evidence/AT-6/375-dark.png`, `evidence/AT-6/375-light.png`, `evidence/AT-6/api-calls-dark.json`, `evidence/AT-6/api-calls-light.json`, `evidence/AT-6/row-375-dark.txt`, `evidence/AT-6/row-375-light.txt`
Observation: The Wednesday order starts with waiver_targets and weak_spots. The response lifts sell_high (0.88), power_rankings (0.84), and week_recap (0.79) above 0.7, and the row shows Sell high or buy low first, then Power rankings, then Week recap, in both themes.

## AT-7: An opened Topic drops off the Suggestions

App: site
Then: The power rankings Topic is not in the 3 Suggestions. It still shows in "More".
Files: `evidence/AT-7/steps.txt`, `evidence/AT-7/after-reload-375-dark.png`, `evidence/AT-7/after-reload-375-light.png`, `evidence/AT-7/after-reload-more-375-dark.png`, `evidence/AT-7/after-reload-more-375-light.png`, `evidence/AT-7/api-calls-dark.json`, `evidence/AT-7/api-calls-light.json`, `evidence/AT-7/before-tap-375-dark.png`, `evidence/AT-7/before-tap-375-light.png`, `evidence/AT-7/row-after-reload-375-dark.txt`, `evidence/AT-7/row-after-reload-375-light.txt`
Observation: Before the tap, Power rankings is the second chip. After the reload, the row is Sell high or buy low, Week recap, and Waiver targets, with no Power rankings chip, and "More" lists Power rankings as item 4 of 13.

## AT-8: The top personal Suggestion builds on open

App: site
Then: The whole Answer shows at once, with no stream and no tool step.
Files: `evidence/AT-8/steps.txt`, `evidence/AT-8/run-weak-spots.txt`, `evidence/AT-8/api-log-weak-spots.txt`, `evidence/AT-8/api-calls-weak-spots.json`, `evidence/AT-8/recording-weak-spots-375-light.webm`, `evidence/AT-8/after-tap-weak-spots-375-light.png`, `evidence/AT-8/frame-31.40s-weak-spots-before-tap.png`, `evidence/AT-8/frame-31.80s-weak-spots-after-tap.png`, `evidence/AT-8/frame-31.90s-weak-spots-after-tap.png`, `evidence/AT-8/frame-32.00s-weak-spots-after-tap.png`, `evidence/AT-8/frame-32.20s-weak-spots-after-tap.png`, `evidence/AT-8/frame-32.50s-weak-spots-after-tap.png`, `evidence/AT-8/frame-32.90s-weak-spots-after-tap.png`, `evidence/AT-8/frame-33.70s-weak-spots-after-tap.png`
Observation: Weak spots is the first Suggestion. The log shows "The head start builds the personal Topic weak_spots on open", ended as checked, then on the tap 30 s later "came from the store, with no Claude call". run-weak-spots.txt shows an empty busy article with no steps for about 43 ms, then the block, the whole text, and Checked in one sample, with 0 stream words and no step line in any sample. The frames show the card fade in whole.

## AT-9: Loose words reach the right Topic

App: site
Then: The Answer is the next matchup of Lil Fridge for week 9, with the name of its opponent.
Files: `evidence/AT-9/steps.txt`, `evidence/AT-9/375-dark.png`, `evidence/AT-9/375-light.png`, `evidence/AT-9/answer-text-375-light.txt`, `evidence/AT-9/api-calls.json`, `evidence/AT-9/api-log.txt`
Observation: The route is `topic`, `next_matchup`, with fits_topic 0.82 and next_matchup 0.96 in the topic Choice. The Answer shows Lil Fridge 10-6 against behold the lamb 6-10, with the Must Watch text and "Read the full report".

## AT-10: A question about another team answers about that team

App: site
Then: The Answer is about Bo Girds, with the 9-7 record of Bo Girds, not the record of Lil Fridge.
Files: `evidence/AT-10/steps.txt`, `evidence/AT-10/375-dark.png`, `evidence/AT-10/375-light.png`, `evidence/AT-10/answer-text-375-light.txt`, `evidence/AT-10/api-calls.json`, `evidence/AT-10/api-log.txt`
Observation: The route is `free` with `names_team` 0.99 and `team` 6 (bo_girds 1 in the team Choice). The Answer says "Bo Girds is 9-7 and third in the standings" with 921.62 points for, and does not give the 10-6 record of Lil Fridge.

## AT-11: A stat lookup gets a free answer

App: site
Then: A short answer names the team with the most points for in weeks 1 to 8, and the number matches the standings data.
Files: `evidence/AT-11/steps.txt`, `evidence/AT-11/375-dark.png`, `evidence/AT-11/375-light.png`, `evidence/AT-11/answer-text-375-light.txt`, `evidence/AT-11/api-calls.json`, `evidence/AT-11/api-log.txt`, `evidence/AT-11/standings-points-for.txt`
Observation: The stream calls the `standings` tool once (step "Reading the standings"). The Answer names Bo Girds with 921.62, then the team now named Puka Deez... (London Cooking in the week 8 page) with 918.99, then Lil Fridge with 909.55; these three match the standings data, with "Checked".

## AT-12: A half fit shows its Topic under the free answer

App: site
Then: One Suggestion chip of the top Topic shows under the answer.
Files: `evidence/AT-12/steps.txt`, `evidence/AT-12/375-dark.png`, `evidence/AT-12/375-light.png`, `evidence/AT-12/answer-text-375-light.txt`, `evidence/AT-12/api-calls.json`, `evidence/AT-12/api-log.txt`
Observation: The route of this run gives `fits_topic` 0.49 and `suggestion` your_season. One chip "Your season" shows under the checked free answer, in both themes.

## AT-13: A question that the data cannot answer gets an honest miss

App: site
Then: The Answer says only "I can't answer that.", shows the 3 closest Topics, and hides the chips of the dock.
Files: `evidence/AT-13/steps.txt`, `evidence/AT-13/375-dark.png`, `evidence/AT-13/375-light.png`, `evidence/AT-13/answer-text-375-light.txt`, `evidence/AT-13/api-calls.json`, `evidence/AT-13/api-log.txt`
Observation: The route is `miss` (fits_topic 0.09, data_can_answer 0.16). The card says only "I can't answer that." with the closest Topics Your next matchup, Week recap, and How you stack up, and the dock row of chips does not show.

## AT-14: An honest miss writes a log entry

App: api
Then: The miss log holds one entry with the question text, the team, the time, and the 3 closest Topics.
Files: `evidence/AT-14/output.txt`, `evidence/AT-14/api-log.txt`
Observation: The miss log has 0 rows before the request. After the `miss` response, it holds one row: "is CeeDee Lamb playing sunday", roster 3, Lil Fridge, 2026-11-11T13:50:46-05:00, and ["next_matchup", "week_recap", "last_matchup"].

## AT-15: A rule break gets a calm refusal

App: site
Then: A calm refusal shows. It holds no passphrase, no Claude text, and no tool step.
Files: `evidence/AT-15/steps.txt`, `evidence/AT-15/375-dark.png`, `evidence/AT-15/375-light.png`, `evidence/AT-15/answer-text-375-light.txt`, `evidence/AT-15/api-calls.json`, `evidence/AT-15/api-log.txt`
Observation: The route is `refuse` with the abuse Noul 1. The card says "I can't answer that. Ask about your team, another team, or the league." with no passphrase and no step, and the API log of the run has no Claude line.

## AT-16: An off-topic request gets an honest miss, not a poem

App: site
Then: The honest miss shows with the 3 closest Topics, and no poem shows.
Files: `evidence/AT-16/steps.txt`, `evidence/AT-16/375-dark.png`, `evidence/AT-16/375-light.png`, `evidence/AT-16/answer-text-375-light.txt`, `evidence/AT-16/api-calls.json`, `evidence/AT-16/api-log.txt`
Observation: The route is `miss` (fits_topic 0.02). The card says "I can't answer that." with How you stack up, Week recap, and Weak spots, and no poem shows.

## AT-17: The route eval hits 52 of 59

App: api
Then: At least 52 of the 59 questions with an expected route get that route, a share of 87.5%.
Files: `evidence/AT-17/output.txt`, `evidence/AT-17/route-table.md`
Observation: The live run against jev-1.14.0 prints "Hits: 55 of 59." and the test `test_the_route_eval_hits_at_least_52_of_59` passes. The table lists 62 questions; the 4 misses are questions 7, 9, 12, and 41, and questions 34 to 36 have no expected route.

## AT-18: The data block of a Topic shows before the text

App: site
Then: The data block shows first. The checked text then reveals under it, from a blur to sharp.
Files: `evidence/AT-18/api-calls.json`, `evidence/AT-18/api-log.txt`, `evidence/AT-18/end-375-light.png`, `evidence/AT-18/frame-2.92s-block-alone.png`, `evidence/AT-18/frame-4.00s-block-alone-writing.png`, `evidence/AT-18/frame-4.90s-block-alone-checking.png`, `evidence/AT-18/frame-5.47s-text-in-stream.png`, `evidence/AT-18/frame-5.72s-text-in-stream.png`, `evidence/AT-18/frame-5.97s-text-in-stream.png`, `evidence/AT-18/frame-6.22s-text-in-stream.png`, `evidence/AT-18/frame-6.37s-checked.png`, `evidence/AT-18/frame-6.47s-text-in-stream.png`, `evidence/AT-18/recording-375-light.webm`, `evidence/AT-18/samples.txt`, `evidence/AT-18/steps.txt`
Observation: With no kept Answer, the block shows alone under "Writing…" from 2.77 s, then "Checking" from 4.56 s, with no text (frames at 2.92 s, 4.00 s, 4.90 s). At 5.37 s the whole text of 81 words shows under the block with all 81 words blurred, and the words sharpen from 5.61 s to 6.10 s; the Answer ends as checked.

## AT-19: Each tool call shows as a plain step

App: site
Then: Each tool call shows as a step in plain words, such as "Reading week 1…". No step and no copy names Jev, the Advisor, or the Finder.
Files: `evidence/AT-19/api-calls.json`, `evidence/AT-19/api-log.txt`, `evidence/AT-19/copy-search.txt`, `evidence/AT-19/end-375-light.png`, `evidence/AT-19/frame-4.90s-reading-the-league.png`, `evidence/AT-19/frame-5.75s-reading-the-week.png`, `evidence/AT-19/frame-6.35s-reading-week-1.png`, `evidence/AT-19/frame-7.10s-reading-week-1-done.png`, `evidence/AT-19/frame-8.20s-checking.png`, `evidence/AT-19/frame-9.40s-checked.png`, `evidence/AT-19/page-text.txt`, `evidence/AT-19/recording-375-light.webm`, `evidence/AT-19/samples.txt`, `evidence/AT-19/steps.txt`
Observation: The steps show one at a time in the card: "Reading the league…", "Reading the week…", "Reading week 1…", then "✔ Reading week 1"; the stream holds one tool call. copy-search.txt has 0 hits in the copy file of CPC, the export of /, and the page text; the front-door source has 3 hits, a code comment in topics.ts ("Jev judges what is urgent") and the TypeScript type name `FinderTrade` twice in trade-answer.tsx.

## AT-20: The check mark turns from checking to checked

App: site
Then: A "checking" mark shows, then turns into "checked" in the ink color, with no bounce.
Files: `evidence/AT-20/api-calls-dark.json`, `evidence/AT-20/api-calls-light.json`, `evidence/AT-20/api-log-dark.txt`, `evidence/AT-20/api-log-light.txt`, `evidence/AT-20/end-375-dark.png`, `evidence/AT-20/end-375-light.png`, `evidence/AT-20/frame-10.80s-light-checked.png`, `evidence/AT-20/frame-10.85s-light-checked.png`, `evidence/AT-20/frame-10.90s-light-checked.png`, `evidence/AT-20/frame-10.95s-light-checked.png`, `evidence/AT-20/frame-11.05s-light-checked.png`, `evidence/AT-20/frame-11.30s-light-checked.png`, `evidence/AT-20/frame-12.30s-light-checked.png`, `evidence/AT-20/frame-4.13s-dark-checking.png`, `evidence/AT-20/frame-4.43s-dark-checking.png`, `evidence/AT-20/frame-7.20s-dark-checked.png`, `evidence/AT-20/frame-7.25s-dark-checked.png`, `evidence/AT-20/frame-7.30s-dark-checked.png`, `evidence/AT-20/frame-7.35s-dark-checked.png`, `evidence/AT-20/frame-7.45s-dark-checked.png`, `evidence/AT-20/frame-7.70s-dark-checked.png`, `evidence/AT-20/frame-8.49s-light-checking.png`, `evidence/AT-20/frame-8.70s-dark-checked.png`, `evidence/AT-20/frame-8.79s-light-checking.png`, `evidence/AT-20/recording-375-dark.webm`, `evidence/AT-20/recording-375-light.webm`, `evidence/AT-20/samples-dark.txt`, `evidence/AT-20/samples-light.txt`, `evidence/AT-20/steps.txt`
Observation: Light: the mark reads "Checking" in rgb(102, 102, 102), the mute color, from 8.39 s, and turns to "Checked" in rgb(20, 20, 20), the ink color, at 11.02 s through a blur cross-fade. Dark: "Checking" in rgb(153, 153, 153) from 4.03 s turns to "Checked" in rgb(255, 255, 255), the ink color, at 7.43 s; every sample of both runs has transform none, and the frames show no move.

## AT-21: A failed check holds the text, and only a checked text shows

App: both
Then: The first text never shows. "Fixing a number…" shows, then the second text reveals whole with "checked".
Files: `evidence/AT-21/at-21-weak-spots-one-failed-claim.sse`, `evidence/AT-21/end-375-light.png`, `evidence/AT-21/frame-3.40s-block-writing.png`, `evidence/AT-21/frame-4.40s-checking.png`, `evidence/AT-21/frame-4.90s-no-text.png`, `evidence/AT-21/frame-5.40s-fixing-a-number.png`, `evidence/AT-21/frame-6.20s-fixing-and-checking.png`, `evidence/AT-21/frame-7.30s-second-text-whole.png`, `evidence/AT-21/frame-7.60s-second-text-checked.png`, `evidence/AT-21/frame-8.40s-after-key-check.png`, `evidence/AT-21/output.txt`, `evidence/AT-21/recording-375-light.webm`, `evidence/AT-21/replay-calls.json`, `evidence/AT-21/replay-samples.txt`, `evidence/AT-21/steps.txt`
Observation: The pytest run passes, with the check states checking, fixing, checking, checked and one text-start, after the fix part. In the replay, the block shows with "Writing…", then "Checking", then "Fixing a number…", then the second text shows whole and blurred at 7.19 s with the mark that turns to "Checked" at 7.42 s; no first text shows in any sample or frame. After the stream ends, the key check of the live API reads the fixture key as stale, so the last frame shows "Your roster changed." with Refresh.

## AT-22: A second failed check gives the honest miss

App: api
Then: The stream ends with the honest miss, and it holds neither text.
Files: `evidence/AT-22/output.txt`
Observation: Both `FakeJev` tests pass, and the temp test prints the parts: check states checking, fixing, checking, failed, then `data-miss` with stack_up, waiver_targets, and trade_ideas, then `finish`. It prints "Text parts in the stream: 0", with 2 calls of the stand-in writer.

## AT-23: A Topic Answer links to its page

App: site
Then: The power rankings page opens at `/rankings/`.
Files: `evidence/AT-23/steps.txt`, `evidence/AT-23/answer-375-dark.png`, `evidence/AT-23/answer-375-light.png`, `evidence/AT-23/page-375-dark.png`, `evidence/AT-23/page-375-light.png`, `evidence/AT-23/url-375-dark.txt`, `evidence/AT-23/url-375-light.txt`
Observation: Shot answer shows the Power rankings Answer (6th, Down 5) with "Read the full report". After the tap, the URL is `http://127.0.0.1:4173/rankings/` in both themes, and shot page shows the power rankings page.

## AT-24: The trade check shows the Lean, the Case, and the Bullets

App: site
Then: The Answer shows the Lean, the Case, the top Bullets, and a link to the Trade page.
Files: `evidence/AT-24/steps.txt`, `evidence/AT-24/1280-dark.png`, `evidence/AT-24/1280-light.png`, `evidence/AT-24/375-dark.png`, `evidence/AT-24/375-light.png`, `evidence/AT-24/768-dark.png`, `evidence/AT-24/768-light.png`, `evidence/AT-24/answer-text-375-light.txt`, `evidence/AT-24/api-calls.json`, `evidence/AT-24/api-log.txt`
Observation: The picks are Courtland Sutton (roster 3) and Zay Flowers (roster 6), both sure. The Answer shows the Lean "Send it" on the five-step scale, the Case, one "for" Bullet and two "against" Bullets, and "Open it on the Trade page". In the full-page shots the fixed ask box covers part of the first Bullet; answer-text-375-light.txt holds the whole text.

## AT-25: The Case leads with the reason for its Lean

App: site
Then: The first sentence of the Case gives the reason for the Lean, and the fairness line agrees with the Lean.
Files: `evidence/AT-25/steps.txt`, `evidence/AT-25/375-light.png`, `evidence/AT-25/answer-text-375-light.txt`, `evidence/AT-25/case-and-lean.txt`
Observation: The Lean is "Send it". The first sentence of the Case is "If you believe Zay Flowers's slow month is a dip and not the new normal, this is a trade you make right now." The fairness state is lopsided with `gives_more` 6, and the site line is "It helps Lil Fridge more."

## AT-26: Trade ideas come from the real Finder in CPC

App: site
Then: The Answer shows trade offers from the real `/find` output, each for a weak spot of Lil Fridge.
Files: `evidence/AT-26/steps.txt`, `evidence/AT-26/1280-dark.png`, `evidence/AT-26/1280-light.png`, `evidence/AT-26/375-dark.png`, `evidence/AT-26/375-light.png`, `evidence/AT-26/768-dark.png`, `evidence/AT-26/768-light.png`, `evidence/AT-26/answer-text-375-light.txt`, `evidence/AT-26/api-calls.json`, `evidence/AT-26/api-log.txt`
Observation: The Answer of Lil Fridge comes from the trade-ideas stream: "Built 92 offers", the pick "You give Derrick Henry and get Chris Olave" (All You Need Is Love) for the weak WR2 slot, and two more offers under "Also weighed". The suggestion fact of the Topic names the WR2 slot of Lil Fridge as its weak spot.

## AT-27: Sell high or buy low names players of Your team

App: site
Then: The Answer names at least one player on the roster of Lil Fridge to sell, with the reason.
Files: `evidence/AT-27/steps.txt`, `evidence/AT-27/375-dark.png`, `evidence/AT-27/375-light.png`, `evidence/AT-27/answer-text-375-light.txt`, `evidence/AT-27/api-calls.json`, `evidence/AT-27/api-log.txt`, `evidence/AT-27/roster-lil-fridge.txt`
Observation: The Answer names Derrick Henry (RB, BAL), who is on the live roster of Lil Fridge, to sell. The reason is his recent drop: 7.1 points a game over 4 weeks against 15.1 for the season.

## AT-28: The steps of a trade Answer show during the wait

App: site
Then: Plain steps, such as "Weighed 6 offers", show one by one before the whole Answer shows.
Files: `evidence/AT-28/api-calls.json`, `evidence/AT-28/api-log.txt`, `evidence/AT-28/frame-2.80s-change-1.png`, `evidence/AT-28/frame-4.90s-change-2.png`, `evidence/AT-28/frame-41.55s-change-7.png`, `evidence/AT-28/frame-43.76s-change-8.png`, `evidence/AT-28/frame-44.00s-whole-answer.png`, `evidence/AT-28/frame-44.40s-whole-answer.png`, `evidence/AT-28/frame-45.50s-whole-answer.png`, `evidence/AT-28/frame-5.69s-change-3.png`, `evidence/AT-28/frame-5.74s-change-4.png`, `evidence/AT-28/frame-6.52s-change-5.png`, `evidence/AT-28/frame-7.59s-change-6.png`, `evidence/AT-28/recording-375-light.webm`, `evidence/AT-28/steps-samples.txt`, `evidence/AT-28/steps.txt`, `evidence/AT-28/trade-end-375-light.png`
Observation: steps-samples.txt and the frames show "Reading the league…", then "Checking 11 teams for a fit…" at 4.75 s, "✔ Checked 11 teams for a fit" and "Building offers…" at 5.59 s, "✔ Built 70 offers" at 6.38 s, "✔ Weighed 70 offers" at 7.44 s, and "Picked the best 2…" at 41.40 s, each added under the one before. The whole Answer with two offers shows at 43.6 s.

## AT-29: A kept Answer comes back at once and costs nothing

App: api
Then: The kept Answer comes back with no Claude call, and the team count stays the same.
Files: `evidence/AT-29/output.txt`, `evidence/AT-29/api-log.txt`
Observation: Both requests return the same key and a text part with the id "kept", with only the check state `checked`. The log says "The personal Topic weak_spots came from the store, with no Claude call" twice and has no api.anthropic.com line for them, and the team count is 1 before, 1 after the first, and 1 after the second.

## AT-30: The Thread reads like a chat, and each older Answer stays as it rendered

App: site
Then: The weak spots Answer shows at the bottom. The week recap stays above it in full, with its data block, its text, and its link, and nothing folds.
Files: `evidence/AT-30/steps.txt`, `evidence/AT-30/api-calls-375-light.json`, `evidence/AT-30/articles-1280-dark.txt`, `evidence/AT-30/articles-1280-light.txt`, `evidence/AT-30/articles-375-dark.txt`, `evidence/AT-30/articles-375-light.txt`, `evidence/AT-30/articles-768-dark.txt`, `evidence/AT-30/articles-768-light.txt`, `evidence/AT-30/full-1280-dark.png`, `evidence/AT-30/full-1280-light.png`, `evidence/AT-30/full-375-dark.png`, `evidence/AT-30/full-375-light.png`, `evidence/AT-30/full-768-dark.png`, `evidence/AT-30/full-768-light.png`, `evidence/AT-30/recap-in-view-1280-dark.png`, `evidence/AT-30/recap-in-view-1280-light.png`, `evidence/AT-30/recap-in-view-375-dark.png`, `evidence/AT-30/recap-in-view-375-light.png`, `evidence/AT-30/recap-in-view-768-dark.png`, `evidence/AT-30/recap-in-view-768-light.png`
Observation: The weak spots Answer shows at the bottom. The week recap stays above it with its data block, its full text, and "Read the full report", and each article has 0 fold controls (aria-expanded), at each width and theme.

## AT-31: A new question scrolls to its top, and the reader scrolls up to reread

App: site
Then: The new question scrolls to its top under the Thread header. Above it, the week recap and the weak spots Answer show as they rendered, with no entrance and no stream again.
Files: `evidence/AT-31/after-send-375-light.png`, `evidence/AT-31/api-calls.json`, `evidence/AT-31/frame-16.38s-scroll-up.png`, `evidence/AT-31/frame-16.63s-scroll-up.png`, `evidence/AT-31/frame-16.88s-scroll-up.png`, `evidence/AT-31/frame-17.13s-scroll-up.png`, `evidence/AT-31/frame-17.38s-scroll-up.png`, `evidence/AT-31/frame-17.63s-scroll-up.png`, `evidence/AT-31/frame-18.88s-scrolled-up.png`, `evidence/AT-31/frame-8.13s-before-send.png`, `evidence/AT-31/frame-8.63s-after-send.png`, `evidence/AT-31/frame-9.13s-after-send.png`, `evidence/AT-31/frame-9.83s-after-send.png`, `evidence/AT-31/measures.txt`, `evidence/AT-31/recording-375-light.webm`, `evidence/AT-31/scrolled-up-2-375-light.png`, `evidence/AT-31/scrolled-up-375-light.png`, `evidence/AT-31/steps.txt`
Observation: After Send, the page scrolls until the new question "week 1 results" sits at 121 px, just under the Thread header bottom at 113 px, by about 0.47 s. In every sample of the send and of the scroll up, the Week recap and Weak spots Answers have 0 running animations and 0 stream words, and the scrolled-up shots show both in full as before the send.

## AT-32: The Thread stays for the week

App: site
Then: The Thread shows the same two Answers.
Files: `evidence/AT-32/steps.txt`, `evidence/AT-32/after-375-dark.png`, `evidence/AT-32/after-375-light.png`, `evidence/AT-32/articles-after-375-dark.txt`, `evidence/AT-32/articles-after-375-light.txt`, `evidence/AT-32/before-375-dark.png`, `evidence/AT-32/before-375-light.png`
Observation: Before and after the reopen, the Thread shows the Week recap Answer and the Power rankings Answer, and the articles file lists both after the reopen, in both themes.

## AT-33: A new week starts an empty Thread

App: site
Then: The Thread is empty.
Files: `evidence/AT-33/steps.txt`, `evidence/AT-33/after-rebuild-375-dark.png`, `evidence/AT-33/after-rebuild-375-light.png`, `evidence/AT-33/before-rebuild-375-dark.png`, `evidence/AT-33/before-rebuild-375-light.png`, `evidence/AT-33/thread-after-375-dark.txt`, `evidence/AT-33/thread-after-375-light.txt`
Observation: Before the rebuild, the Thread holds Week recap and Power rankings, under "WK 08". After the rebuild with week 9, the page shows "Week 9" and an empty Thread; the thread file counts 0 articles and `cpc.thread` is `{"3":{"week":9,"entries":[]}}`.

## AT-34: A stale Answer shows dimmed with Refresh

App: site
Then: The weak spots Answer shows dimmed with "Your roster changed since <day>. [Refresh]", and no "checked" mark.
Files: `evidence/AT-34/steps.txt`, `evidence/AT-34/after-375-dark.png`, `evidence/AT-34/after-375-light.png`, `evidence/AT-34/api-calls-after-dark.json`, `evidence/AT-34/api-calls-after-light.json`, `evidence/AT-34/api-log-after.txt`, `evidence/AT-34/before-375-dark.png`, `evidence/AT-34/before-375-light.png`, `evidence/AT-34/state-after-375-dark.txt`, `evidence/AT-34/state-after-375-light.txt`
Observation: The key check response gives `current: false` for the weak spots key after the roster seam adds a player. The Answer shows the line "Your roster changed since Wednesday." with a Refresh button, the article has `data-stale` and its text shows in a muted tone, and no "Checked" text shows in it.

## AT-35: Refresh gets a fresh Answer

App: site
Then: A fresh weak spots Answer streams with "checked", and it is no longer dimmed.
Files: `evidence/AT-35/api-calls.json`, `evidence/AT-35/api-log.txt`, `evidence/AT-35/end-375-light.png`, `evidence/AT-35/end-state.txt`, `evidence/AT-35/frame-136.42s-stale-before-tap.png`, `evidence/AT-35/frame-137.72s-after-tap.png`, `evidence/AT-35/frame-141.80s-streaming.png`, `evidence/AT-35/frame-142.80s-streaming.png`, `evidence/AT-35/frame-143.80s-checked.png`, `evidence/AT-35/recording-375-light.webm`, `evidence/AT-35/stale-375-light.png`, `evidence/AT-35/steps.txt`, `evidence/AT-35/team-count.txt`
Observation: Before the tap, the Weak spots Answer shows "Your roster changed since Wednesday." with Refresh. After the tap, the card loses data-stale and streams: "Writing…", Checking, "Fixing a number…", then a fresh text (QB now "stacked", 6th of 12) with "Checked" at 143.51 s; at the end 0 articles have data-stale and the body opacity is 1. The log shows one fresh Answer ended as checked, and the team count goes from 4 to 5.

## AT-36: Clear empties the Thread with no confirm

App: site
Then: The Thread is empty at once, with no confirm, and the opened Topics stay off the Suggestions.
Files: `evidence/AT-36/steps.txt`, `evidence/AT-36/after-375-dark.png`, `evidence/AT-36/after-375-dark.txt`, `evidence/AT-36/after-375-light.png`, `evidence/AT-36/after-375-light.txt`, `evidence/AT-36/before-375-dark.png`, `evidence/AT-36/before-375-light.png`
Observation: 150 ms after the tap on Clear, the page holds 0 articles, 0 browser dialogs, and 0 dialog elements. The row after Clear is Sell high or buy low, Waiver targets, and Weak spots, with no Week recap and no Power rankings chip.

## AT-37: The team cap shows its calm line

App: site
Then: The line "That's 25 questions today. Ask again tomorrow." shows with the 3 closest Topics, and no manager is named.
Files: `evidence/AT-37/steps.txt`, `evidence/AT-37/375-dark.png`, `evidence/AT-37/375-light.png`, `evidence/AT-37/answer-text-375-light.txt`, `evidence/AT-37/api-calls.json`, `evidence/AT-37/api-log.txt`, `evidence/AT-37/seed.txt`
Observation: The seed brings the count of Lil Fridge today to 25 (11 real Answers plus 14 seeded rows). The card says "That's 25 questions today. Ask again tomorrow." with Your season, Playoff race, and Power rankings, and names no manager; the log says "A free answer stopped at the team cap, with no Claude call".

## AT-38: The league cap shows its calm line

App: site
Then: CPC shows the line "The league's question budget is used up for this month. It resets on Dec 1." NorCal gets a free answer.
Files: `evidence/AT-38/steps.txt`, `evidence/AT-38/api-log-cpc-dark.txt`, `evidence/AT-38/api-log-cpc-light.txt`, `evidence/AT-38/api-log-norcal.txt`, `evidence/AT-38/cpc-375-dark.png`, `evidence/AT-38/cpc-375-light.png`, `evidence/AT-38/cpc-api-calls-dark.json`, `evidence/AT-38/cpc-api-calls-light.json`, `evidence/AT-38/norcal-375-dark.png`, `evidence/AT-38/norcal-375-light.png`, `evidence/AT-38/norcal-answer-text.txt`, `evidence/AT-38/norcal-api-calls-light.json`, `evidence/AT-38/seed.txt`
Observation: With CPC at $25.00, the CPC card says "The league's question budget is used up for this month. It resets on Dec 1.", and the log says "stopped at the league cap, with no Claude call". NorCal, at $0, gets a checked free answer that names Mitseeker5000 at 1,130.34 points.

## AT-39: The 80% mark logs one alert

App: api
Then: The API logs one alert, and a later answer logs no second alert.
Files: `evidence/AT-39/output.txt`, `evidence/AT-39/api-log.txt`
Observation: The seed sets $19.9970 in place of $19.90, because one free answer costs about $0.005 to $0.012. The first answer takes the month to $20.0091, and the log holds one WARNING "The league cpc used $20.01 of its $25.00 Claude budget for 2026-11, past 80%."; the second answer takes it to $20.0144 with no second WARNING, and the alerts table holds 1 row.

## AT-40: Past a cap, what costs nothing still works

App: site
Then: The power rankings Answer shows in full.
Files: `evidence/AT-40/steps.txt`, `evidence/AT-40/375-dark.png`, `evidence/AT-40/375-light.png`, `evidence/AT-40/api-log.txt`
Observation: With the team cap of AT-37 in the store, the Power rankings Answer shows in full in both themes: rank 6th, Down 5, 10-6, three rows, the text, and "Read the full report".

## AT-41: The ask endpoint needs the passphrase

App: api
Then: Both get 401, and no Jev or Claude call runs.
Files: `evidence/AT-41/output.txt`, `evidence/AT-41/api-log.txt`
Observation: Both requests get "HTTP/1.1 401 Unauthorized" with no body. The log of the two requests holds only the two 401 lines, with no typesafe_sdk line and no api.anthropic.com line.

## AT-42: The ask box glides to the bottom on the first question

App: site
Then: The ask box glides to the bottom in one move, and the question shows above it.
Files: `evidence/AT-42/api-calls.json`, `evidence/AT-42/ask-box-top.txt`, `evidence/AT-42/end-375-light.png`, `evidence/AT-42/frame-5.49s-before-send.png`, `evidence/AT-42/frame-5.85s-glide.png`, `evidence/AT-42/frame-5.91s-glide.png`, `evidence/AT-42/frame-5.97s-glide.png`, `evidence/AT-42/frame-6.03s-glide.png`, `evidence/AT-42/frame-6.09s-glide.png`, `evidence/AT-42/frame-6.15s-glide.png`, `evidence/AT-42/frame-6.21s-glide.png`, `evidence/AT-42/frame-6.27s-glide.png`, `evidence/AT-42/frame-6.33s-glide.png`, `evidence/AT-42/frame-6.39s-glide.png`, `evidence/AT-42/recording-375-light.webm`, `evidence/AT-42/steps.txt`
Observation: ask-box-top.txt shows the top of the ask box at 452 px before the send; it moves down in one run of rising values to 668 px between about 0.13 s and 0.55 s after the tap, with no rise first. The question bubble shows at 121 px to 129 px, above the ask box, from about 0.1 s after the tap.

## AT-43: A tapped Suggestion morphs into the question

App: site
Then: The chip morphs into the question bubble as one surface.
Files: `evidence/AT-43/api-calls-league.json`, `evidence/AT-43/api-calls.json`, `evidence/AT-43/end-375-light.png`, `evidence/AT-43/end-league-375-light.png`, `evidence/AT-43/frame-10.83s-first-before-tap.png`, `evidence/AT-43/frame-11.13s-first-after-tap.png`, `evidence/AT-43/frame-11.17s-first-after-tap.png`, `evidence/AT-43/frame-11.21s-first-after-tap.png`, `evidence/AT-43/frame-11.25s-first-after-tap.png`, `evidence/AT-43/frame-11.29s-first-after-tap.png`, `evidence/AT-43/frame-11.33s-first-after-tap.png`, `evidence/AT-43/frame-11.37s-first-after-tap.png`, `evidence/AT-43/frame-11.41s-first-after-tap.png`, `evidence/AT-43/frame-11.45s-first-after-tap.png`, `evidence/AT-43/frame-11.49s-first-after-tap.png`, `evidence/AT-43/frame-11.53s-first-after-tap.png`, `evidence/AT-43/frame-11.57s-first-after-tap.png`, `evidence/AT-43/frame-7.33s-league-before-tap.png`, `evidence/AT-43/frame-7.63s-league-after-tap.png`, `evidence/AT-43/frame-7.67s-league-after-tap.png`, `evidence/AT-43/frame-7.71s-league-after-tap.png`, `evidence/AT-43/frame-7.75s-league-after-tap.png`, `evidence/AT-43/frame-7.79s-league-after-tap.png`, `evidence/AT-43/frame-7.83s-league-after-tap.png`, `evidence/AT-43/frame-7.87s-league-after-tap.png`, `evidence/AT-43/frame-7.91s-league-after-tap.png`, `evidence/AT-43/frame-7.95s-league-after-tap.png`, `evidence/AT-43/frame-7.99s-league-after-tap.png`, `evidence/AT-43/frame-8.03s-league-after-tap.png`, `evidence/AT-43/frame-8.07s-league-after-tap.png`, `evidence/AT-43/recording-375-light.webm`, `evidence/AT-43/recording-league-375-light.webm`, `evidence/AT-43/run-league.txt`, `evidence/AT-43/run.txt`, `evidence/AT-43/steps.txt`
Observation: In both runs the question bubble starts on the box of the tapped chip and glides to the top in about 0.45 s while the chip fades out: Sell high or buy low (a trade Topic, chip 1) from 112,333 at 240x50 to 195,121, and Power rankings (a league Topic) from 16,390 at 168x50 to 223,121, turning dark. The frames of run 1 show the bubble pass behind the "Reading the league…" card of the Answer during the glide.

## AT-44: The words sharpen from a blur as they stream

App: site
Then: Each new word shows blurred, then sharp.
Files: `evidence/AT-44/api-calls.json`, `evidence/AT-44/api-log.txt`, `evidence/AT-44/end-375-light.png`, `evidence/AT-44/frame-6.68s-stream.png`, `evidence/AT-44/frame-6.72s-stream.png`, `evidence/AT-44/frame-6.76s-stream.png`, `evidence/AT-44/frame-6.80s-stream.png`, `evidence/AT-44/frame-6.84s-stream.png`, `evidence/AT-44/frame-6.88s-stream.png`, `evidence/AT-44/frame-6.92s-stream.png`, `evidence/AT-44/frame-6.96s-stream.png`, `evidence/AT-44/frame-7.00s-stream.png`, `evidence/AT-44/frame-7.04s-stream.png`, `evidence/AT-44/frame-7.08s-stream.png`, `evidence/AT-44/frame-7.12s-stream.png`, `evidence/AT-44/frame-7.16s-stream.png`, `evidence/AT-44/frame-7.20s-stream.png`, `evidence/AT-44/frame-7.24s-stream.png`, `evidence/AT-44/frame-7.28s-stream.png`, `evidence/AT-44/recording-375-light.webm`, `evidence/AT-44/steps.txt`, `evidence/AT-44/word-samples.txt`
Observation: word-samples.txt shows the free answer text of 51 words show at 6.69 s, all 51 blurred, then the blurred count drops by about 5 words every 50 ms to 0 at 7.39 s. The frames, 40 ms apart, show the words sharpen line by line from the top.

## AT-45: The front door wears the brand of each league

App: site
Then: Each front door uses the band and the accent of its client, in light and dark. Both clients share one font, by ADR 0024.
Files: `evidence/AT-45/steps.txt`, `evidence/AT-45/cpc-1280-dark-style.txt`, `evidence/AT-45/cpc-1280-dark.png`, `evidence/AT-45/cpc-1280-light-style.txt`, `evidence/AT-45/cpc-1280-light.png`, `evidence/AT-45/cpc-375-dark-style.txt`, `evidence/AT-45/cpc-375-dark.png`, `evidence/AT-45/cpc-375-light-style.txt`, `evidence/AT-45/cpc-375-light.png`, `evidence/AT-45/cpc-768-dark-style.txt`, `evidence/AT-45/cpc-768-dark.png`, `evidence/AT-45/cpc-768-light-style.txt`, `evidence/AT-45/cpc-768-light.png`, `evidence/AT-45/norcal-1280-dark-style.txt`, `evidence/AT-45/norcal-1280-dark.png`, `evidence/AT-45/norcal-1280-light-style.txt`, `evidence/AT-45/norcal-1280-light.png`, `evidence/AT-45/norcal-375-dark-style.txt`, `evidence/AT-45/norcal-375-dark.png`, `evidence/AT-45/norcal-375-light-style.txt`, `evidence/AT-45/norcal-375-light.png`, `evidence/AT-45/norcal-768-dark-style.txt`, `evidence/AT-45/norcal-768-dark.png`, `evidence/AT-45/norcal-768-light-style.txt`, `evidence/AT-45/norcal-768-light.png`
Observation: The CPC front door uses the accent #b8342a and the band #141414; the NorCal front door uses the accent #c2410c and the band #0a0a0a, with its own page colors in each theme. Both use the font spaceGrotesk for the body and the h1.

## AT-46: Reduced motion keeps only the fades

App: site
Then: The ask box and the Answer fade in place, with no glide, no blur, and no spring.
Files: `evidence/AT-46/api-calls.json`, `evidence/AT-46/ask-box-samples.txt`, `evidence/AT-46/end-375-light.png`, `evidence/AT-46/frame-5.35s-before-send.png`, `evidence/AT-46/frame-5.60s-after-send.png`, `evidence/AT-46/frame-5.65s-after-send.png`, `evidence/AT-46/frame-5.75s-after-send.png`, `evidence/AT-46/frame-5.95s-after-send.png`, `evidence/AT-46/frame-6.55s-after-send.png`, `evidence/AT-46/recording-375-light.webm`, `evidence/AT-46/steps.txt`
Observation: Under reduced motion, the ask box jumps from 452 px to 668 px with opacity 1, transform none, and filter none in every sample; the frames show the old place fade out and the box fade in at the bottom. Inside the Answer, elements only change opacity, with 0 transforms and 0 filters in every sample, and 0 elements on the page have a CSS filter at the end.

## AT-47: The ask box clears the home bar of an iPhone

App: site
Then: The ask box sits fully above the home bar.
Files: `evidence/AT-47/steps.txt`, `evidence/AT-47/iphone-393-dark-home-bar-marked.png`, `evidence/AT-47/iphone-393-dark.png`, `evidence/AT-47/iphone-393-light-home-bar-marked.png`, `evidence/AT-47/iphone-393-light.png`, `evidence/AT-47/measures-dark.txt`, `evidence/AT-47/measures-light.txt`
Observation: The viewport meta has `viewport-fit=cover`, and the page measures `env(safe-area-inset-bottom)` as 34 px. The ask box ends at 728 px and the bottom dock sits above the pink home bar zone, which starts at 818 px, in both themes.

## AT-48: With the front door on, the menu keeps four links

App: site
Then: The menu shows Home, Week 8, Power Rankings, and Managers, and nothing else. The dock shows the same four items with its short labels, such as Rankings, and nothing else.
Files: `evidence/AT-48/steps.txt`, `evidence/AT-48/cpc-1280-dark-links.txt`, `evidence/AT-48/cpc-1280-dark.png`, `evidence/AT-48/cpc-1280-light-links.txt`, `evidence/AT-48/cpc-1280-light.png`, `evidence/AT-48/cpc-375-dark-links.txt`, `evidence/AT-48/cpc-375-dark.png`, `evidence/AT-48/cpc-375-light-links.txt`, `evidence/AT-48/cpc-375-light.png`, `evidence/AT-48/norcal-1280-dark-links.txt`, `evidence/AT-48/norcal-1280-dark.png`, `evidence/AT-48/norcal-1280-light-links.txt`, `evidence/AT-48/norcal-1280-light.png`, `evidence/AT-48/norcal-375-dark-links.txt`, `evidence/AT-48/norcal-375-dark.png`, `evidence/AT-48/norcal-375-light-links.txt`, `evidence/AT-48/norcal-375-light.png`
Observation: With `front_door = true`, the visible menu of each client is Home, Week 8, Power Rankings, and Managers at 1280 px (Site menu), and Home, Week 8, Rankings, and Managers at 375 px (Bottom menu), with nothing else.

## AT-49: Every page stays

App: site
Then: Each page renders as before the spec.
Files: `evidence/AT-49/steps.txt`, `evidence/AT-49/front-door-analyze-375-light.png`, `evidence/AT-49/front-door-managers-375-light.png`, `evidence/AT-49/front-door-midseason-375-light.png`, `evidence/AT-49/front-door-rankings-375-light.png`, `evidence/AT-49/front-door-week-08-375-light.png`, `evidence/AT-49/main-analyze-375-light.png`, `evidence/AT-49/main-managers-375-light.png`, `evidence/AT-49/main-midseason-375-light.png`, `evidence/AT-49/main-rankings-375-light.png`, `evidence/AT-49/main-week-08-375-light.png`
Observation: Each page renders on the spec build. Each spec shot has the same size as the shot of the same page on a build of `main` (for example week 8 at 375x7129 and midseason at 375x16671).

## AT-50: `/` has no hero and no tool tiles

App: site
Then: No hero, no four numbers, no midseason takeover, and no tool tiles show.
Files: `evidence/AT-50/steps.json`, `evidence/AT-50/1280-dark.png`, `evidence/AT-50/1280-light.png`, `evidence/AT-50/375-dark.png`, `evidence/AT-50/375-light.png`, `evidence/AT-50/768-dark.png`, `evidence/AT-50/768-light.png`
Observation: Each shot of `/` shows the front door: "Ask about Lil Fridge", the Suggestions, and the ask box. No hero, no four numbers, no midseason takeover, and no tool tiles show.

## AT-51: The weekly build writes the league Topic Answers

App: pipeline
Then: The published week holds an Answer of each of the 7 league Topics for each of the 12 teams.
Files: `evidence/AT-51/output.txt`
Observation: `clients/cpc/published/2026/week-08/topics.json` holds 12 teams with 7 Answers each, 84 in all, over the 7 league Topics, and the `topics.json` of the `make page-json` run has the same count. The topic and fact of each Answer match in both files; the files differ in other fields, which round 1 traced to the your_season stats of the season `managers.json` that holds the week 9 state.

## AT-52: ADR 0031 records the manager text

App: both
Then: It says what goes to TypeSafe and to Anthropic, that the miss log lives on Fly, and that each entry stays 90 days.
Files: `evidence/AT-52/output.txt`
Observation: `docs/adr/0031-the-text-that-managers-type.md` has the sections "What goes to TypeSafe", "What goes to Anthropic", and "The miss log", which says "one SQLite file per client on the Fly volume, at `CORNERSTONE_ASK_DIR`, which is `/data/ask` on Fly" and "Each entry stays 90 days." A second file carries the number 0031: `docs/adr/0031-the-evidence-goes-to-typesafe-and-a-flag-is-not-a-verdict.md`, from main.

## AT-53: The miss log stays out of the repo

App: api
Then: No file of the miss log shows.
Files: `evidence/AT-53/output.txt`
Observation: The store of the round sits at `/private/tmp/claude-503/fd-ask/` with `cpc.sqlite` (1 miss row, from AT-14), outside the repo; `fly.toml` sets `/data/ask`, and `.gitignore` lists `data/ask/`. After the API stopped, `git status --short --untracked-files=all` prints no line, and `git ls-files` has no `.sqlite` file and no `data/ask/` file.

## AT-54: A past season gets an honest miss

App: site
Then: The honest miss shows, and no answer names a past champion.
Files: `evidence/AT-54/steps.txt`, `evidence/AT-54/375-dark.png`, `evidence/AT-54/375-light.png`, `evidence/AT-54/answer-text-375-light.txt`, `evidence/AT-54/api-calls.json`, `evidence/AT-54/api-log.txt`
Observation: The route is `miss` (fits_topic 0.03, data_can_answer 0.03). The card says "I can't answer that." with Playoff race, Week recap, and Your season, and names no past champion.

## AT-55: No control stops a stream

App: site
Then: No stop control shows.
Files: `evidence/AT-55/during-stream-375-light.png`, `evidence/AT-55/steps.txt`, `evidence/AT-55/visible-buttons-during-stream.txt`
Observation: At the shot, one article has aria-busy true and shows the live step "Reading the league…". The visible buttons are the theme switch, the team button, Clear, More, three Suggestion chips, and Send; none is a stop control.

## AT-56: The weekly report keeps its content

App: pipeline
Then: The `page.json` of week 8 is the same on both.
Files: `evidence/AT-56/output.txt`
Observation: `make page-json CLIENT=cpc WEEK=8` ran in a detached worktree of `front-door` (99d00125) and of `main` (1d7bfc0d); the full build was not run, because it writes new Claude text for each chapter. The two `page.json` files have no diff and the same SHA-256, and each equals the committed build file; `git diff 1d7bfc0d 99d00125` of the published week 8 shows only the new `topics.json`.

## AT-57: The API keeps no Thread and asks for no login

App: api
Then: No table holds a Thread, an account, or a login.
Files: `evidence/AT-57/output.txt`
Observation: The ask store holds the tables `answers` (key, topic, roster_id, answer, kept_at), `spend`, `alerts`, and `misses` for each client, and the eggs store holds `eggs` and `claims`. The `CREATE TABLE` lines of the code list only those six tables.

## AT-58: An unsure player pick opens the Trade page

App: site
Then: The Answer opens the Trade page with the form, and fills no player that Jev is unsure of.
Files: `evidence/AT-58/steps.txt`, `evidence/AT-58/answer-375-dark.png`, `evidence/AT-58/answer-375-light.png`, `evidence/AT-58/answer-text.txt`, `evidence/AT-58/api-calls.json`, `evidence/AT-58/api-log.txt`, `evidence/AT-58/trade-page-375-dark.png`, `evidence/AT-58/trade-page-375-light.png`
Observation: The picks are Derrick Henry (0.64) and Justin Jefferson (0.11), both `sure: false`, and the answer part is a `form` with empty `gives` and `gets`. The Answer says "Name the players to check that trade." and its link opens `/analyze/?team=3`, where the Trade page shows Lil Fridge as Your Team and no player in either side.

## AT-59: With the front door off, `/` keeps the old home page, and the front door hides at `/ask/`

App: site
Then: `/` shows the home page of `main`, and the menu shows the items of `main`, with Trade Analyzer. `/ask/` shows the front door with `noindex`, and no page links to `/ask/`.
Files: `evidence/AT-59/steps.txt`, `evidence/AT-59/ask-1280-dark.png`, `evidence/AT-59/ask-1280-light.png`, `evidence/AT-59/ask-375-dark.png`, `evidence/AT-59/ask-375-light.png`, `evidence/AT-59/ask-768-dark.png`, `evidence/AT-59/ask-768-light.png`, `evidence/AT-59/ask-links.txt`, `evidence/AT-59/home-1280-dark.png`, `evidence/AT-59/home-1280-light.png`, `evidence/AT-59/home-375-dark.png`, `evidence/AT-59/home-375-light.png`, `evidence/AT-59/home-768-dark.png`, `evidence/AT-59/home-768-light.png`, `evidence/AT-59/menu-1280-dark.png`, `evidence/AT-59/menu-1280-light.png`, `evidence/AT-59/menu-375-dark.png`, `evidence/AT-59/menu-375-light.png`, `evidence/AT-59/menu-768-dark.png`, `evidence/AT-59/menu-768-light.png`, `evidence/AT-59/menu-links-1280-dark.txt`, `evidence/AT-59/menu-links-1280-light.txt`, `evidence/AT-59/menu-links-375-dark.txt`, `evidence/AT-59/menu-links-375-light.txt`, `evidence/AT-59/menu-links-768-dark.txt`, `evidence/AT-59/menu-links-768-light.txt`, `evidence/AT-59/menu-vs-main.txt`, `evidence/AT-59/robots.txt`
Observation: `/` shows the old home page (the Title Race midseason card, Power Rankings, Tools, Weekly Reports), and its visible text matches the build of `main`. The menu is Home, Week 8, Power Rankings, Managers, and Trade Analyzer, the same as on `main`, with no Midseason Report link on either. `/ask/` shows the front door, `out/ask/index.html` has `<meta name="robots" content="noindex"/>`, and the only `/ask/` text in `out/` is the pageHref of the ask page itself.

## AT-60: A typed question to a personal Topic gets its own checked Answer

App: site
Then: The route is weak spots. The Answer shows the weak spots data block and a text that answers the question, with "checked".
Files: `evidence/AT-60/375-dark.png`, `evidence/AT-60/375-light.png`, `evidence/AT-60/answer-text-375-light.txt`, `evidence/AT-60/api-calls.json`, `evidence/AT-60/api-log.txt`, `evidence/AT-60/end-375-dark.png`, `evidence/AT-60/end-375-light.png`, `evidence/AT-60/steps.txt`
Observation: The route response is `topic`, `weak_spots` (fits_topic 0.91). The log shows a Claude call for the question ("ended as checked, with 2 texts") besides the head start, and no read of a stored Answer; the shots show the weak spots block of Bo Girds and a text that names the FLEX hole of Blake Corum as the place to improve, with "Checked" in the end shots.

## AT-61: A personal Topic that ends as a miss keeps its data block

App: both
Then: The weak spots data block stays, and only the text place shows "I can't answer that." The API log holds each failed sentence with its noul.
Files: `evidence/AT-61/at-61-weak-spots-bo-girds-two-failed-texts.sse`, `evidence/AT-61/end-375-dark.png`, `evidence/AT-61/end-375-light.png`, `evidence/AT-61/output.txt`, `evidence/AT-61/replay-calls-dark.json`, `evidence/AT-61/replay-calls-light.json`, `evidence/AT-61/replay-samples-dark.txt`, `evidence/AT-61/replay-samples-light.txt`, `evidence/AT-61/steps.txt`
Observation: The pytest output shows the stream: the data block, checking, fixing, checking, failed, and a miss part, with no text part; its log lines name each failed sentence, "Your weakest spot is QB, which ranks 7th of 12.", at 0.10. Both shots show the weak spots block of Bo Girds (QB, 7th of 12, 2 holes) with "I can't answer that." and the closest Topics under it in the text place.

## AT-62: A row with a hole never reads "fine"

App: site
Then: The row of that slot in the data block names its player as a hole, and its depth word is not "fine".
Files: `evidence/AT-62/375-dark.png`, `evidence/AT-62/375-light.png`, `evidence/AT-62/answer-text-375-light.txt`, `evidence/AT-62/api-calls.json`, `evidence/AT-62/api-log.txt`, `evidence/AT-62/data-block-of-the-stream.json`, `evidence/AT-62/end-375-dark.png`, `evidence/AT-62/end-375-light.png`, `evidence/AT-62/steps.txt`, `evidence/AT-62/team-survey.txt`, `evidence/AT-62/weak-spots-slice.txt`
Observation: The team is Return of T Mac (roster 8), found in team-survey.txt with one hole in one starting slot. The WR row of the data block reads "thin · hole: Carnell Tate", 7th of 12, in both themes, the same as the slice and the stream data block, and its depth word is not "fine".

## AT-63: Trade ideas around a named player keep that player on his side

App: site
Then: The Answer shows at least one idea, and each offer and each idea sends Kenneth Walker III away from Bo Girds.
Files: `evidence/AT-63/steps.txt`, `evidence/AT-63/375-dark.png`, `evidence/AT-63/375-light.png`, `evidence/AT-63/answer-text-375-light.txt`, `evidence/AT-63/api-calls.json`, `evidence/AT-63/api-log.txt`
Observation: The picks part gives Kenneth Walker III on the `gives` side, roster 6, sure (0.93). The steps read "Found Kenneth Walker III" to "Picked the best one". The pick and each offer under "Also weighed" send Kenneth Walker III away from Bo Girds, for Gibbs, Robinson, McCaffrey, or James Cook III.

## AT-64: "Who has the best roster" reads the grade of every team

App: site
Then: The route is a free answer, not How you stack up. The Answer names the team with the best roster grade and that grade, as the `roster_grades` tool result gives, with "checked".
Files: `evidence/AT-64/steps.txt`, `evidence/AT-64/375-dark.png`, `evidence/AT-64/375-light.png`, `evidence/AT-64/answer-text-375-light.txt`, `evidence/AT-64/api-calls.json`, `evidence/AT-64/api-log.txt`
Observation: The route is `free` (fits_topic 0.44, in `api-calls.json`). The stream calls `roster_grades`, which ranks Teehee 1st with an A. The Answer names Teehee with the A grade, as of today, with "Checked".

## AT-65: Every wait shows one step pattern

App: site
Then: Both waits show step lines inside the Answer card. The first line reads "Reading the league…", the live step has a braille spinner, and each done step has ✔.
Files: `evidence/AT-65/api-calls.json`, `evidence/AT-65/api-log.txt`, `evidence/AT-65/frame-20.00s-trade-done-and-live-picking.png`, `evidence/AT-65/frame-3.00s-trade-live-reading-the-league.png`, `evidence/AT-65/frame-31.00s-trade-all-done.png`, `evidence/AT-65/frame-33.40s-week-1-live-reading-the-league.png`, `evidence/AT-65/frame-34.60s-week-1-live-reading-week-1.png`, `evidence/AT-65/frame-35.60s-week-1-done-step.png`, `evidence/AT-65/frame-38.00s-week-1-end.png`, `evidence/AT-65/frame-5.00s-trade-live-checking-teams.png`, `evidence/AT-65/frame-7.00s-trade-done-and-live.png`, `evidence/AT-65/recording-375-light.webm`, `evidence/AT-65/steps-samples.txt`, `evidence/AT-65/steps.txt`, `evidence/AT-65/trade-end-375-light.png`, `evidence/AT-65/week-1-end-375-light.png`
Observation: For Bo Girds, both waits show their step lines inside the white card of the Answer (a div with a 1 px border). Each wait starts with "Reading the league…"; the live step has a braille spinner (U+2800 to U+28FF) and each done step has ✔, such as "✔ Built 13 offers" and "✔ Reading week 1".

## AT-66: A trade follow-up routes to trade ideas with its limit

App: site
Then: The route is trade ideas with the limit `keep_positions: ["WR"]`. The Answer shows at least one idea, a pick or a near idea, and no offer or idea sends a WR away from Bo Girds.
Files: `evidence/AT-66/steps.txt`, `evidence/AT-66/375-dark.png`, `evidence/AT-66/375-light.png`, `evidence/AT-66/answer-text-375-light.txt`, `evidence/AT-66/api-calls.json`, `evidence/AT-66/api-log.txt`
Observation: The route is `topic`, `trade_ideas`, and the stream sends `data-limit` with `keep_positions: ["WR"]`. The step "Left out each offer that sends away a WR" shows, and the Answer shows one idea under "Ideas, none a clear win": Bo Girds gives Trey McBride (TE) for Jaxon Smith-Njigba, with no WR sent away.

## AT-67: Trade ideas always show at least one idea with its reason

App: site
Then: The Answer shows at least one idea. Each idea that the pick did not keep shows under "Also weighed" or "Ideas, none a clear win", with its reason in plain words.
Files: `evidence/AT-67/steps.txt`, `evidence/AT-67/1280-dark.png`, `evidence/AT-67/1280-light.png`, `evidence/AT-67/375-dark.png`, `evidence/AT-67/375-light.png`, `evidence/AT-67/768-dark.png`, `evidence/AT-67/768-light.png`, `evidence/AT-67/answer-text-375-light.txt`, `evidence/AT-67/api-calls.json`, `evidence/AT-67/api-log.txt`
Observation: The log shows "Finder offers of Bo Girds: 1", and the steps read "Built one offer", "Weighed one offer", and "Kept one idea to weigh". The Answer shows that idea under "Ideas, none a clear win" with its reason in plain words, at each width and theme.

## AT-68: The trade pick reads a starter on IR as out now

App: api
Then: The pick sheet of each offer names Lamar Jackson as a starter who cannot play now, with his return week, or with the default week when Sleeper gives none. No reason in the Answer says that Bo Girds does not need a QB.
Files: `evidence/AT-68/answer.txt`, `evidence/AT-68/api-log.txt`, `evidence/AT-68/output.txt`, `evidence/AT-68/pick-sheet.txt`, `evidence/AT-68/sheet_launcher.py`, `evidence/AT-68/steps.txt`
Observation: Each of the 10 offer sheets holds `6.now`: "QB: Aaron Rodgers (QB20). Lamar Jackson is a starter who cannot play now. He is out with no return week on file, so he counts as back in week 14." The Answer keeps two offers of Drake Maye for a WR and three near ideas, and no reason says that Bo Girds does not need a QB.

## AT-69: One tap on Send sends, and the keyboard closes

App: site
Then: The question sends on that tap, and the ask box loses the focus, so the keyboard closes.
Files: `evidence/AT-69/end-375.png`, `evidence/AT-69/end-iphone15-393.png`, `evidence/AT-69/frame-375-7.01s-before-tap.png`, `evidence/AT-69/frame-375-7.41s-after-tap.png`, `evidence/AT-69/frame-375-7.71s-after-tap.png`, `evidence/AT-69/frame-375-8.51s-after-tap.png`, `evidence/AT-69/frame-iphone15-393-7.28s-before-tap.png`, `evidence/AT-69/frame-iphone15-393-7.68s-after-tap.png`, `evidence/AT-69/frame-iphone15-393-7.98s-after-tap.png`, `evidence/AT-69/frame-iphone15-393-8.78s-after-tap.png`, `evidence/AT-69/recording-375.webm`, `evidence/AT-69/recording-iphone15-393.webm`, `evidence/AT-69/steps.txt`, `evidence/AT-69/webkit-log-375.txt`, `evidence/AT-69/webkit-log-iphone15-393.txt`
Observation: In both runs, the tap on the ask box gives focus to the input and the fake keyboard opens; the one touch tap on Send gives pointerdown, touchstart, mouseup, click, and submit on the Send button, then focusout of the input with focus on BODY. 1.5 s after the tap, the keyboard is closed, the Thread holds the article "week 1 results", and the API got one /ask and one /ask/free POST.

## AT-70: The rate limit counts questions, not the reads of the page

App: api
Then: No request gets 429, and the question gets its Answer.
Files: `evidence/AT-70/output.txt`, `evidence/AT-70/api-log.txt`
Observation: With the default limit of 30, the 40 reads of `/suggestions` and `/personal/current` between 13:56:12 and 13:56:17 each get 200. The question gets 200 with route `free`, and its answer stream gets 200 and ends `checked` with the text "Bo Nix scored 4.48 fantasy points in week 6."; the log has no 429 line.

## AT-71: The empty screen says the league is fair game

App: site
Then: Under "Ask about Lil Fridge", the line "or any team in the league." shows, then "Try" with "who has the best roster" and "week 1 results". The ask box reads "Ask about your team or the league".
Files: `evidence/AT-71/steps.txt`, `evidence/AT-71/1280-dark.png`, `evidence/AT-71/1280-light.png`, `evidence/AT-71/375-dark.png`, `evidence/AT-71/375-light.png`, `evidence/AT-71/768-dark.png`, `evidence/AT-71/768-light.png`, `evidence/AT-71/text-1280-dark.txt`, `evidence/AT-71/text-1280-light.txt`, `evidence/AT-71/text-375-dark.txt`, `evidence/AT-71/text-375-light.txt`, `evidence/AT-71/text-768-dark.txt`, `evidence/AT-71/text-768-light.txt`
Observation: Under "Ask about Lil Fridge", the line "or any team in the league." shows, then "Try" with "who has the best roster" and "week 1 results". The ask box reads "Ask about your team or the league" at each width and theme.

## AT-72: A ranking of teams shows as a checked list

App: site
Then: The Answer shows a lead sentence and a list of teams by points for, most first, with "checked". Each total matches the live standings that the `standings` tool reads.
Files: `evidence/AT-72/steps.txt`, `evidence/AT-72/1280-dark.png`, `evidence/AT-72/1280-light.png`, `evidence/AT-72/375-dark.png`, `evidence/AT-72/375-light.png`, `evidence/AT-72/768-dark.png`, `evidence/AT-72/768-light.png`, `evidence/AT-72/answer-text-375-light.txt`, `evidence/AT-72/api-calls.json`, `evidence/AT-72/api-log.txt`, `evidence/AT-72/standings-points-for.txt`
Observation: The stream calls `standings` and sends a `data-block` list "Points scored this season" of 5 teams, most first, with "Checked". Each of the 5 totals matches the live `standings` tool result in `standings-points-for.txt`, which reads through week 8. Against the week 8 `page.json`, the first three match, and two differ: Maye d'force B with U 900.65 against 901.65, and Teehee 885.98 against 885.88.

## AT-73: A comparison of two teams shows as a table

App: site
Then: The route is a free answer, not How you stack up. The Answer shows a table that sets Bo Girds and Teehee side by side.
Files: `evidence/AT-73/steps.txt`, `evidence/AT-73/1280-dark.png`, `evidence/AT-73/1280-light.png`, `evidence/AT-73/375-dark.png`, `evidence/AT-73/375-light.png`, `evidence/AT-73/768-dark.png`, `evidence/AT-73/768-light.png`, `evidence/AT-73/answer-text-375-light.txt`, `evidence/AT-73/api-calls.json`, `evidence/AT-73/api-log.txt`
Observation: The route is `free` (fits_topic 0.05), not stack_up. The `data-block` is a table "Bo Girds vs Teehee (as of today)" with a column for each team, and the Answer shows it with "Checked".

## AT-74: A question about one player shows a player card

App: site
Then: The Answer shows a player card of Lamar Jackson, with Bo Girds as his fantasy team and a status that says he cannot play now.
Files: `evidence/AT-74/steps.txt`, `evidence/AT-74/1280-dark.png`, `evidence/AT-74/1280-light.png`, `evidence/AT-74/375-dark.png`, `evidence/AT-74/375-light.png`, `evidence/AT-74/768-dark.png`, `evidence/AT-74/768-light.png`, `evidence/AT-74/answer-text-375-light.txt`, `evidence/AT-74/api-calls.json`, `evidence/AT-74/api-log.txt`
Observation: The `data-block` is a player card of Lamar Jackson (QB, BAL) with `fantasy_team` Bo Girds and `can_play_now` false. The card shows "Can't play now" and "on IR", with "Checked".

## AT-75: Each roster grade says when it is from

App: site
Then: The grade in the data block shows "as of today". The grade on the manager page of Bo Girds shows "after week 9", from `through` of `managers.json`.
Files: `evidence/AT-75/steps.txt`, `evidence/AT-75/answer-375-dark.png`, `evidence/AT-75/answer-375-light.png`, `evidence/AT-75/api-calls.json`, `evidence/AT-75/managers-through.txt`, `evidence/AT-75/page-375-dark.png`, `evidence/AT-75/page-375-light.png`, `evidence/AT-75/text-375-dark.txt`, `evidence/AT-75/text-375-light.txt`
Observation: The data block of the How you stack up Answer shows "as of today" under the grade B. The manager page of Bo Girds shows "GRADE after week 9" next to the grade B, and `through` of `managers.json` is 9.
