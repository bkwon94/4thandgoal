# Grade clarity: evidence

Spec: `.scratch/grade-clarity/PRD.md`. Acceptance tests: `.scratch/grade-clarity/ACCEPTANCE.md`.
Built from: `099b004`, on 2026-11-05. The agent gives no Test verdict. Brian gives one for each test.

## How the evidence was made

- The grades read the live snapshot of `cpc` on Thursday 2026-11-05, about 08:35Z. The trade window is week 9, and the stats run through week 8.
- The live data moved after the build of the tickets. A new depth chart has `dt` 2026-11-05T07:01:33Z. Mike Evans, Deebo Samuel Sr., and Emeka Egbuka are now Questionable, not Out. Emanuel Wilson and Chris Godwin Jr. are on no `cpc` roster now.
- The local API ran with `make -C apps/api api` and `CORNERSTONE_ALLOWED_ORIGINS=http://localhost:4173,http://localhost:3000`, so the served site could call it. The passphrase is `localtest`, from `apps/api/Makefile`.
- Claude grade calls: 3 with an answer. Trade A (`evidence/AT-1/tradeA.document.json`), the three-side trade (`evidence/AT-5/three.document.json`), and one finder call on `norcal` (AT-33). The fallback run (AT-29) made 2 failed attempts with a bad key. The site grades of trade A and of the three-side trade hit the result cache and made no call.
- Trade A's document serves AT-1 to AT-4, AT-6 to AT-8, AT-10 to AT-13, AT-17, AT-19 to AT-24, AT-26, AT-27, AT-34, and AT-35.
- `evidence/scripts/probe.py` loads the live snapshot through the API `Sources`, with the real fetches. It takes a grade time for the `Sources` clock, the time of the request in the code. It makes no grade call. `probe3.py` loads the saved week 8 data as `cornerstone analyze --week 8` does. `pick.js` drives the team pickers of the form.
- Site screenshots: a reload clears the graded result. So the theme was set with no reload, as the boot script does it: `cpc.theme` in local storage and the `dark` class on the root. Element screenshots of `agent-browser` came out blank, because each chapter fades in on scroll. So each file is a crop of a `--full` screenshot, cut to the box of the element.
- After the week 8 build of AT-32, `git restore clients/` put back every tracked file, and the new untracked `clients/cpc/data/2026/week-08/raw/nflverse.json` was deleted. No week output stays changed.

## AT-1: Layout A order

App: site
Then: The page shows the decision with its "why" sentence, then the trade card, then one card for each side, then the as-of line, in one column.
Files: `evidence/AT-1/375-light.png`, `evidence/AT-1/375-dark.png`, `evidence/AT-1/768-light.png`, `evidence/AT-1/768-dark.png`, `evidence/AT-1/1280-light.png`, `evidence/AT-1/1280-dark.png`, `evidence/AT-1/tradeA.request.json`, `evidence/AT-1/tradeA.document.json`
Observation: Each full-page screenshot shows the form, then "Decision for behold the lamb", "Yes", and its reason, then "Fairness", then "The Trade", then the roster 10 card, then the roster 6 card, then "Suggested Counters" with the as-of line. At each width the chapters sit in one column. The fairness block sits under the decision, between the decision and the trade card.

## AT-2: The side card before a tap

App: site
Then: Each side card shows Cooper and Washington with a headshot, the position, the NFL team, and the Season rank, then 2 or 3 bullets, then the "This week and next" box. The fold is closed.
Files: `evidence/AT-2/375-light.png`, `evidence/AT-2/375-dark.png`, `evidence/AT-2/768-light.png`, `evidence/AT-2/768-dark.png`, `evidence/AT-2/1280-light.png`, `evidence/AT-2/1280-dark.png`
Observation: The crop holds the whole result. Each side card shows Washington ("WR · JAX", "Season rank WR21") and Cooper ("WR · NYJ", "Season rank WR60 · Recent rank WR18") with headshots. Then it shows 3 bullets, then the "This week and next" box, then the closed summary "How the grade adds up · 5 rows".

## AT-3: The fold

App: site
Then: The fold opens and shows each row with a mark, up, down, or even. <n> equals the count of rows that show.
Files: `evidence/AT-3/375-light.png`, `evidence/AT-3/375-dark.png`, `evidence/AT-3/768-light.png`, `evidence/AT-3/768-dark.png`, `evidence/AT-3/1280-light.png`, `evidence/AT-3/1280-dark.png`
Observation: The agent clicked the summary of the roster 10 card. The fold reads "How the grade adds up · 5 rows" and shows 5 rows: The Deal, Roster, Standing, Usage, and Schedule. The Deal, Roster, Standing, and Schedule have an up mark, and Usage has an even mark ("–").

## AT-4: The players stack on a phone

App: site
Then: At 375 px the two players of a side stack. At 768 and 1280 px they stand next to each other. The two side cards never stand next to each other.
Files: `evidence/AT-4/375-light.png`, `evidence/AT-4/375-dark.png`, `evidence/AT-4/768-light.png`, `evidence/AT-4/768-dark.png`, `evidence/AT-4/1280-light.png`, `evidence/AT-4/1280-dark.png`
Observation: At 375 px "You get" (Washington) sits above "You give" (Cooper). At 768 and 1280 px the two groups stand next to each other. The AT-1 and AT-2 files show the roster 6 card under the roster 10 card at each width.

## AT-5: Three sides

App: both
Then: The document has three sides, each with bullets, Week lines, and factors. The page shows three side cards in the same form.
Files: `evidence/AT-5/output.txt`, `evidence/AT-5/three.request.json`, `evidence/AT-5/three.document.json`, `evidence/AT-5/375-light.png`, `evidence/AT-5/375-dark.png`, `evidence/AT-5/768-light.png`, `evidence/AT-5/768-dark.png`, `evidence/AT-5/1280-light.png`, `evidence/AT-5/1280-dark.png`
Observation: The document has sides 4, 12, and 7. Each side has 3 bullets, Week lines for weeks 9 and 10, and 5 factors. The page shows three side cards, NFC Least, Teehee, and To Infinity and Bijan, each with players, bullets, the "This week and next" box, and a closed fold of 5 rows.

## AT-6: The Season rank

App: pipeline
Then: Cooper has `season_rank` WR60, the rank by total points through week 8, as Sleeper sorts it.
Files: `evidence/AT-6/output.txt`
Observation: The document gives Cooper (`13276`) `season_rank` "WR60". The `make analyze` output prints no rank, so the value comes from the `POST /analyze` document.

## AT-7: The Recent rank on a large gap

App: pipeline
Then: Cooper has `recent_rank` WR18. His gap is 42, and `RECENT_RANK_GAP` is 12.
Files: `evidence/AT-7/output.txt`
Observation: Cooper has `season_rank` "WR60" and `recent_rank` "WR18", a gap of 42. `tunables.py` line 39 reads `RECENT_RANK_GAP = 12`.

## AT-8: No Recent rank on a small gap

App: pipeline
Then: Each traded player whose Recent rank is 11 spots or fewer from his Season rank has `recent_rank` null.
Files: `evidence/AT-8/output.txt`
Observation: Washington has Season rank WR21 and a raw Recent rank of 19, a gap of 2, and his `recent_rank` is null. Cooper is the other traded player, and his gap is 42.

## AT-9: The Position rank by season points per game

App: pipeline
Then: The grade reads Cooper as WR26, by season points per game over the games played, not WR18.
Files: `evidence/AT-9/output.txt`
Observation: `position_rank("13276")` gives WR27, not WR26. Cooper's season points per game is 10.70. WR26 is Michael Wilson (`10232`) at 10.77, and WR28 is Tre Tucker at 10.66. In this table no player from WR20 to WR30 has a due-back week. Ticket 01 named A.J. Brown as the player at 10.77 above Cooper, but the live table now has Michael Wilson there.

## AT-10: The bullets

App: pipeline
Then: Each side has 2 or 3 `bullets`, and each bullet is one sentence.
Files: `evidence/AT-10/output.txt`
Observation: Each side has 3 bullets. Each bullet has one sentence end.

## AT-11: The Week line counts

App: pipeline
Then: Each side has a Week line for week 9 and week 10. Each line gives the count of WRs in the top 36 who play, before and after the trade.
Files: `evidence/AT-11/output.txt`
Observation: Roster 10 reads "Week 9: WRs in the top 36 who play stay at 4." and "Week 10: WRs in the top 36 who play stay at 3." Roster 6 reads "stay at 3" in both weeks. A count with no change reads "stay at N", with one number for before and after.

## AT-12: The Week line opponent

App: pipeline
Then: The line of each week names the opponent of the player the side gets, with its rank in points allowed to WRs, rank 1 the most.
Files: `evidence/AT-12/output.txt`
Observation: Roster 10 names Washington "at BAL, 9th most points to WRs" and "at TEN, the most points to WRs". Roster 6 names Cooper "at KC, 31st most points to WRs" and "BUF at home, 3rd most points to WRs". The points allowed table of the snapshot gives TEN 1, BUF 3, BAL 9, and KC 31.

## AT-13: Byes

App: pipeline
Then: The line of each week names each WR of the side who has a bye that week. A side with no bye names none.
Files: `evidence/AT-13/output.txt`
Observation: Roster 10 WR byes: Bernard week 9, Egbuka week 10, Samuel week 8, Nacua week 11, Cooper and Allen week 13. Roster 10 week 9 names "Bernard has a bye", and week 10 names "Egbuka has a bye". Roster 6 WRs have byes in weeks 6, 7, 11, and 13, and Cooper's is 13, so neither roster 6 line names a bye.

## AT-14: Out last week

App: pipeline
Then: The week 9 line names the Out player as "listed Out last week". The week 10 line names him only when his status is IR, PUP, NA, or Sus.
Files: `evidence/AT-14/output.txt`
Observation: The run date is Thursday 2026-11-05, and no WR of roster 6 or 10 is Out or on IR now: Egbuka and Samuel are Questionable. So the trade A lines name no Out player. With the grade time set to Wednesday 2026-11-04T17:00Z, trade T (Tate for Robinson) gives roster 2 "Tate was listed Out last week." in week 9 and does not name Tate in week 10. Roster 8 names "Pierce is on IR." in both weeks. On the saved week 8 data with no grade time, roster 10 reads "Egbuka and Samuel are listed Out."

## AT-15: Steps up

App: pipeline
Then: The week 9 line of the side that holds the SF WR says he steps up. If no roster holds that WR, the test is BLOCKED.
Files: `evidence/AT-15/output.txt`, `evidence/AT-15/tate.document.json`
Observation: Mike Evans (`2216`, roster 1) is Questionable now, not Out. The SF WR directly behind him is Deebo Samuel Sr. (`5872`, roster 10), also Questionable. Jordan Watkins is not in the snapshot. A trade of Samuel to roster 6 for Washington names no step-up. The trade of ticket 07 (roster 8 gives Carnell Tate `13279` to roster 2 for Wan'Dale Robinson `8126`) also names no step-up now. Robinson is behind Tate, who is Out, but TEN has its bye in week 9. Godwin is on no roster, and roster 8 holds Makai Lemon (`13294`), not "Malik Lemon". A search of every rostered player found no step-up in week 9 or 10 at any of the three grade times.

## AT-16: A stale depth chart names no step-up

App: pipeline
Then: No Week line names a step-up.
Files: `evidence/AT-16/output.txt`
Observation: The newest depth chart `dt` is now 2026-11-05T07:01:33Z, not 2026-11-03T07:02Z. At the real grade time (about 08:37Z) the chart is 1 h 36 min old and `chart_is_fresh` is True. With the grade time set to 2026-11-07T08:00Z the chart is 2 days 0 h 58 min old and `chart_is_fresh` is False. No Week line names a step-up at either time. AT-15 found no live step-up case, so the stale run does not show a step-up taken away.

## AT-17: The Week line moves no letter

App: pipeline
Then: `factors` has no Week line row, and the breakdown holds the same adjusters as on `main`, with no new one.
Files: `evidence/AT-17/output.txt`
Observation: The factors of each side are deal, roster fit, standing, trend and usage, and schedule, and `week_lines` sits outside `factors`. `rubric_adjusters` gives the same tuple on `main` and on the branch: `_fit, _standing, _trend, _injury, _upside, _handcuff, _schedule`, plus `_expected_gap` only when it is on.

## AT-18: The verdict can name the Week line

App: pipeline
Then: The fact sheet holds one Week line fact for each side, with the text of its two lines.
Files: `evidence/AT-18/output.txt`
Observation: `trade_fact_sheet` of trade A holds `10.week_line` and `6.week_line`. Each holds the text of the week 9 line and then the week 10 line.

## AT-19: Silent rows hide

App: pipeline
Then: No side has a handcuff row, because no player in trade A is a handcuff.
Files: `evidence/AT-19/output.txt`
Observation: The factor names of both sides are deal, roster fit, standing, trend and usage, and schedule. No side has a handcuff row. The injury and upside rows are also hidden.

## AT-20: No banned word

App: pipeline
Then: No bullet, factor reason, or verdict reason holds "trade value", "highest-value", "best lineup", "the line", "hole", "win-now move", "return bet", "star", "opportunity", "one step", "no step", "takes RB", "takes WR", or "sits on the bench".
Files: `evidence/AT-20/output.txt`
Observation: The scan covers 17 texts: the verdict reason, 6 bullets, and 10 factor reasons. It finds 0 hits for each of the 14 words. The fairness reasons are outside the scan, because the Then line does not name them.

## AT-21: The deal row

App: pipeline
Then: The first factor of each side is the deal row, in a form such as "You get far more than you give." It names no source. No `chart` block stays on a side.
Files: `evidence/AT-21/output.txt`
Observation: The first factor of roster 10 is deal, "You get far more than you give.", and of roster 6 is deal, "You give far more than you get." The keys of each side are `bullets`, `factors`, `roster_id`, and `week_lines`, with no `chart`.

## AT-22: The roster row

App: pipeline
Then: The roster row of each side counts its WRs in the top 36 before and after, such as "You keep 3 WRs in the top 36, and you get the better player."
Files: `evidence/AT-22/output.txt`
Observation: Roster 10 reads "You keep 4 WRs in the top 36, and you get the better player." Roster 6 reads "You keep 3 WRs in the top 36."

## AT-23: The standing row

App: pipeline
Then: The standing row of each side names its race, its need, and whether the trade meets it, in one sentence.
Files: `evidence/AT-23/output.txt`
Observation: Roster 10 reads "Out of the playoff race, so you want the better player for the rest of the season, and you get him." Roster 6 reads "In a playoff spot, so you need points now, and this trade keeps your points about the same."

## AT-24: The usage row

App: pipeline
Then: The usage row has one clause for Cooper and one for Washington, each with the snap share, the target share, and the air yards per target. It names no week and no route share.
Files: `evidence/AT-24/output.txt`
Observation: Both sides read "Washington plays 70% of the snaps (down), sees 22% of the targets, and averages 3.2 air yards per target; Cooper plays 72% of the snaps (up), sees 8% of the targets (down), and averages 10.2 air yards per target." Roster 6 lists Cooper first. The row names no week and no route share.

## AT-25: The handcuff and upside rows

App: pipeline
Then: The handcuff row reads "Spears backs up your RB, Pollard, on the Titans depth chart." An upside row, when it shows, is one plain sentence such as "Spears gets more work while Pollard is out." If no such trade exists, the test is BLOCKED.
Files: `evidence/AT-25/output.txt`, `evidence/AT-25/spears.document.json`
Observation: Emanuel Wilson is on no roster now, so the trade is roster 4 gives Spears (`9508`) to roster 12 for Kenny Gainwell (`7567`). Roster 12 holds Pollard (`5967`), and the chart puts Pollard directly ahead of Spears. Roster 12's handcuff row reads "Spears backs up your RB, Pollard, on the Titans depth chart." No upside row shows, because Pollard is not out. The document comes from the same code with no Claude call.

## AT-26: The schedule row

App: pipeline
Then: The schedule row names each playoff opponent of weeks 15 to 17 with its rank at the position. It has no sentence "The schedule leans for this side".
Files: `evidence/AT-26/output.txt`
Observation: Roster 10 reads "Washington faces HOU (5th most points to WRs), DAL (7th), and WAS (14th) in weeks 15 to 17." Roster 6 reads "Cooper has his bye in week 13 and faces ARI (10th most points to WRs), NE (11th), and MIN (29th) in weeks 15 to 17." Neither has the sentence "The schedule leans for this side".

## AT-27: The as-of line

App: site
Then: The as-of line names the stats and the fetch time of the rosters, and no "Chart week".
Files: `evidence/AT-27/375-light.png`, `evidence/AT-27/375-dark.png`, `evidence/AT-27/768-light.png`, `evidence/AT-27/768-dark.png`, `evidence/AT-27/1280-light.png`, `evidence/AT-27/1280-dark.png`
Observation: The line reads "Stats through week 8 · rosters fetched Nov 5, 3:35 AM", under "Suggested Counters" and "No counters yet." It has no "Chart week".

## AT-28: The no-values note

App: pipeline
Then: `as_of.no_chart_note` reads "This week's player values are not out yet, so both sides start even."
Files: `evidence/AT-28/output.txt`
Observation: The saved week 8 data has no chart read, so its `chart_week` is null. Trade A on that snapshot gives `no_chart` true and `no_chart_note` "This week's player values are not out yet, so both sides start even." The deal row of each side has the same text. The live week 9 snapshot with its chart taken off gives the same note.

## AT-29: The fallback

App: pipeline
Then: `fallback` is true. Each side has no bullets, and still has its Week lines and its factors.
Files: `evidence/AT-29/output.txt`, `evidence/AT-29/fallback.document.json`
Observation: A second local API ran with a bad `ANTHROPIC_API_KEY` and an empty result cache. The log shows "analysis attempt 1 failed" and "analysis attempt 2 failed", each with `authentication_error`. The document has `fallback` true. Each side has empty `bullets`, Week lines for weeks 9 and 10, and 5 factors.

## AT-30: The cache key

App: pipeline
Then: Each change gives a new key.
Files: `evidence/AT-30/output.txt`
Observation: Key 1 of trade A is `4ba5a7b9…`. With `depth_chart_dt` one hour later, key 2 is `1969622d…`. With Germie Bernard (`13274`, roster 10 WR) also set from no status to Out, key 3 is `8dd0c870…`. The three keys differ. The steps change a copy of the live snapshot in memory.

## AT-31: The finder facts

App: pipeline
Then: The facts of each traded player give the Season rank, such as WR60, and no slot fact.
Files: `evidence/AT-31/output.txt`
Observation: The finder found 1 trade for asker 10 and partner 6: Keenan Allen and Deebo Samuel Sr. for Blake Corum. Its fact sheet gives Allen "Season rank is WR39", Samuel "Season rank is WR47" and "Recent rank is WR122", and Corum "Season rank is RB19". No fact id or text holds "slot".

## AT-32: The weekly report keeps its Position rank

App: pipeline
Then: The Position ranks in the two `page.json` files are the same.
Files: `evidence/AT-32/output.txt`, `evidence/AT-32/fields.diff`
Observation: `make -C apps/pipeline build CLIENT=cpc WEEK=8` ran on the branch and exited 0. The When line has no `CLIENT`, and the target needs it. The main side is the committed `main` week 8 `page.json`; no build ran on `main`. The rank fields (leaders rows, standing `rank`, `strength_rank`) are the same. The other changes of `page.json` are `publish_date` and Claude prose. In `managers.json` only the `trade_value` part ranks and three letters (A to B) changed. The build log says "no saved chart read for week 8: the roster grade has no trade value". The slot Position ranks of `managers.json` are the same.

## AT-33: The finder prompt and view stay

App: site
Then: The finder prompt file has no change, and the finder cards look the same as on `main`.
Files: `evidence/AT-33/output.txt`, `evidence/AT-33/375-light.png`, `evidence/AT-33/375-dark.png`, `evidence/AT-33/768-light.png`, `evidence/AT-33/768-dark.png`, `evidence/AT-33/1280-light.png`, `evidence/AT-33/1280-dark.png`
Observation: `git diff main` of `finder.md`, `trade-finder.tsx`, and `trade-side.tsx` is empty. The finder imports `AsOfLine`, `FairnessBlock`, `NoChartLine`, and `SwapCard` from `analyze-result.tsx`, which changed. The screenshots show the `norcal` finder for Bo Girds and puurdygood: 3 cards, each with the swap card, the fairness block, one reason, and "See the Full Result", then the as-of line. No screenshot of `main` was taken, so the files show only the branch.

## AT-34: No Week line past the next week

App: pipeline
Then: Each side has Week lines for week 9 and week 10 only.
Files: `evidence/AT-34/output.txt`
Observation: The weeks of `week_lines` are [9, 10] for roster 10 and for roster 6.

## AT-35: The expected gap row stays off

App: pipeline
Then: No side has an expected gap row, and `EXPECTED_ADJUSTER_ON` is False.
Files: `evidence/AT-35/output.txt`
Observation: No side has an "expected gap" factor. `tunables.py` line 74 reads `EXPECTED_ADJUSTER_ON = False`.

## AT-36: The injury row

App: pipeline
Then: The injury row names the return week and the count of weeks on the injury report, such as "Cooper is out until week 11. He was on the injury report in 5 of 8 weeks."
Files: `evidence/AT-36/output.txt`
Observation: The trade of AT-25 moves Spears, who is Out with weeks on the injury report. Roster 12's injury row reads "Spears is out with no return week on file. He was on the injury report in 5 of 8 weeks." The Returns file holds only `5850` with week 7, so no rostered player has a return week ahead, and no row names one.
