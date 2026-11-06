# Midseason report: acceptance tests

Spec: `.scratch/midseason-report/PRD.md`.

The Test verdict: only Brian gives one. He writes one PR comment on the Spec branch PR, with one line for each test: the id, then PASS, FAIL, or BLOCKED, then an optional note. The PR merges when every test has PASS (ADR 0020). An agent records the evidence and gives no Test verdict.

The expected values come from the real data run of 2026-11-05 on CPC 2026 week 8, with the rules of the decision tickets. The site tests run after the merge of `site-redesign` into `main`.

## Tests

AT-1: The build writes the draft
App: pipeline
Stories: 59
Given: CPC 2026 week 8, with nothing of the report in `clients/cpc/build/2026/` or `clients/cpc/published/2026/`.
When: `make midseason CLIENT=cpc WEEK=8`
Then: The build folder of the season holds `midseason.json`, `sim.json`, and the review file. `clients/cpc/published/2026/` does not change.
Evidence: The command output, and `git status` of `clients/cpc/`.

AT-2: NorCal builds the report
App: pipeline
Stories: 65, 24
Given: NorCal 2026 week 8.
When: `make midseason CLIENT=norcal WEEK=8`
Then: Each week counts one game with no median game, Position top 10 has no DEF list, and the sim's bracket is fixed with no reseed.
Evidence: The command output and the fields of `midseason.json` and `sim.json` for the record, the positions, and the bracket rule.

AT-3: A rerun gives the same sim
App: pipeline
Stories: 60
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Run `make midseason CLIENT=cpc WEEK=8` again.
Then: The two `sim.json` files are the same, byte for byte.
Evidence: The two command outputs and a `diff` of the two files.

AT-4: Points for is the sum of the weekly scores
App: pipeline
Stories: 9
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read the state of the league in `midseason.json`.
Then: Maye d'force B with U has 900.65 points for, not 901.65. All You Need Is Love is 11-5.
Evidence: The command output and the named fields of `midseason.json` in the build folder.

AT-5: Arcs
App: pipeline
Stories: 10, 11, 12
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read the arcs in `midseason.json`.
Then: Return of T Mac has Roller coaster and Turnaround, each with its numbers, and no third arc. Bo Girds has Snakebit and Collapse.
Evidence: The command output and the named fields of `midseason.json` in the build folder.

AT-6: Schedule luck
App: pipeline
Stories: 13, 17
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read schedule luck in `midseason.json`.
Then: All You Need Is Love has +2.73 with Smoke and mirrors. Bo Girds has -2.18 with Snakebit. Each team shows points against with its rank and its close-game record.
Evidence: The command output and the named fields of `midseason.json` in the build folder.

AT-7: Schedule swap
App: pipeline
Stories: 15, 16
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read the schedule swap in `midseason.json`.
Then: Each cell of the diagonal equals the team's standings record. Bo Girds with the schedule of Maye d'force B with U is 14-2.
Evidence: The command output and the named fields of `midseason.json` in the build folder.

AT-8: Luck is explained in plain words
App: site
Stories: 14
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026` and scroll to schedule luck.
Then: A card above the luck table explains the idea with the worked example of All You Need Is Love: 9 of 11 teams outscored in week 3, and 4.27 wins in all. The word "All-play" shows nowhere on the page.
Evidence: Screenshots of the schedule luck chapter at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-9: Injury toll
App: pipeline
Stories: 18
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read the injury toll in `midseason.json`.
Then: behold the lamb lost 9 starter games, the most in the league.
Evidence: The command output and the named fields of `midseason.json` in the build folder.

AT-10: Position top 10
App: pipeline
Stories: 19, 20
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read Position top 10 in `midseason.json`.
Then: The QB #1 is Josh Allen with 189.32. The DEF #3 is the Buccaneers with the tag "Free agent".
Evidence: The command output and the named fields of `midseason.json` in the build folder.

AT-11: The position switch
App: site
Stories: 21
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026` and scroll to Position top 10.
Then: The chapter shows the RB list only, with a switch for QB, RB, WR, TE, and DEF.
Evidence: Screenshots of the Position top 10 chapter at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-12: Draft value in the auction
App: pipeline
Stories: 22, 23, 25
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read draft steals and busts in `midseason.json`.
Then: A steal is Matthew Golden, $2. A bust is A.J. Brown, $39, with the tag "just bad".
Evidence: The command output and the named fields of `midseason.json` in the build folder.

AT-13: Draft value in the snake
App: pipeline
Stories: 24
Given: NorCal 2026 week 8, after `make midseason CLIENT=norcal WEEK=8`.
When: Read draft steals and busts in `midseason.json`.
Then: Each pick's cost is its pick number, and no pick shows a dollar amount.
Evidence: The command output and the named fields of `midseason.json` in the NorCal build folder.

AT-14: The one that got away
Retired: decision 15 removed the "the one that got away" line, and story 26 with it.
App: pipeline
Stories: 26
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read the draft steals in `midseason.json`.
Then: Tyler Allgeier, drafted by Bo Girds for $2 and dropped before his rise, carries the "the one that got away" line.
Evidence: The command output and the named fields of `midseason.json` in the build folder.

AT-15: Waiver hits, misses, and the outbid
App: pipeline
Stories: 27, 28, 29
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read waiver hits and misses in `midseason.json`.
Then: The top hit is Ollie Gordon II, $40 to Unsolicited Dak Picks. The top miss is Joe Mixon, $40. The outbid list has The Blue Tent's $36 bid on Ollie Gordon II.
Evidence: The command output and the named fields of `midseason.json` in the build folder.

AT-16: Trade results
App: pipeline
Stories: 30, 31
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read the trade report card in `midseason.json`.
Then: It lists 20 trades. The week 1 trade of Maye d'force B with U and NFC Least is a Robbery. The week 8 trade is Too soon.
Evidence: The command output and the named fields of `midseason.json` in the build folder.

AT-17: Trade cards
App: site
Stories: 31, 32, 33
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026` and scroll to the trade report card.
Then: The top 3 trades are full cards, each with the record of each team since the trade, such as "5-3 since". A player who was out in the first week after his trade has the tag "hurt on arrival".
Evidence: Screenshots of the trade report card at 375, 768, and 1280 px, each in the light theme and the dark theme. Name the hurt-on-arrival player, if any.

AT-18: Lineup choices
App: pipeline
Stories: 34
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read lineup choices in `midseason.json`.
Then: London Cooking in week 2 lost by 1.67 with 27.54 points on the bench, and its best lineup would have won.
Evidence: The command output and the named fields of `midseason.json` in the build folder.

AT-19: Record book
App: pipeline
Stories: 35
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read the record book in `midseason.json`.
Then: The high is 158.96 by Maye d'force B with U in week 5. The closest game is 0.4, All You Need Is Love over The Blue Tent in week 3.
Evidence: The command output and the named fields of `midseason.json` in the build folder.

AT-20: Awards
App: pipeline
Stories: 36
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read the awards in `midseason.json`.
Then: The MVP is Jahmyr Gibbs. Most active is Bo Girds with 42 moves. Set and forget is London Cooking with 3 moves. All seven awards have a winner and a fact.
Evidence: The command output and the named fields of `midseason.json` in the build folder.

AT-21: Each game shows once
App: site
Stories: 37
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026` and scroll to the record book.
Then: Heartbreak of the year and Beatdown of the year each show once, inside the record book, and not again among the awards.
Evidence: Screenshots of the record book with the awards at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-22: The spread rule
App: pipeline
Stories: 5, 6
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Count the headlines of each team in `midseason.json`.
Then: Each team has 1 to 3 headlines. Bo Girds keeps its 2 arcs and Most active, and both swap callouts name another team.
Evidence: The command output and the named fields of `midseason.json` in the build folder. List the headlines of each team.

AT-23: Players to watch
Retired: decision 15 removed the Players to watch chapter, and story 39 with it.
App: pipeline
Stories: 39
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read players to watch in `midseason.json`.
Then: Due to fall has Jaxon Smith-Njigba. Grab him now has Kyler Murray. Each list has 3 players.
Evidence: The command output and the named fields of `midseason.json` in the build folder.

AT-24: Look ahead
App: pipeline
Stories: 38
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read the look ahead in `midseason.json`.
Then: Maye d'force B with U has the softest schedule, at a .44 win rate of its opponents. behold the lamb has the hardest, at .56.
Evidence: The command output and the named fields of `midseason.json` in the build folder.

AT-25: The opener is the title race
App: pipeline
Stories: 1
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read the opener in `midseason.json`.
Then: The opener is the title race. It names the title odds of the leaders and of All You Need Is Love, the record leader at 11-5.
Evidence: The command output and the named fields of `midseason.json` in the build folder.

AT-26: Three acts
App: site
Stories: 2, 3
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026` and scroll from the top to the end.
Then: The report has three acts in this order: How we got here, The moves, What comes next. Each act opens with a dark title page.
Evidence: Screenshots of each act title page at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-27: The chapter rail
App: site
Stories: 4
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026`, scroll to Act II, and tap "What comes next" in the rail.
Then: The rail stays at the top, and the page moves to Act III.
Evidence: Screenshots of the rail before and after the tap at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-28: The look at each width
App: site
Stories: 7, 8
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026`.
Then: The report renders in the redesign look with no clipped text and no sideways scroll.
Evidence: Screenshots of the opener and one chapter of each act at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-29: The sim is the finale
App: site
Stories: 40
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026` and scroll to the end.
Then: The sim is the last chapter of the report.
Evidence: Screenshots of the end of the report at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-30: The replay: the regular season and the split
App: site
Stories: 41, 42, 43, 44
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026` and press "Sim the season".
Then: Each week of 9 to 14 shows a lower third with the scores, and the standings reorder. After week 14 a red PLAYOFFS wipe plays, then the final standings with the cut under seed 6 and BYE on seeds 1 and 2.
Evidence: A screen recording at 375 px, and screenshots of a week, the wipe, and the final standings at 375 and 1280 px, in the dark theme.

AT-31: The replay: the bracket
App: site
Stories: 45, 46
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026`, press "Sim the season", and wait for the playoffs.
Then: The bracket draws in. Each winner slides along its line to its next slot. In the semifinal, seed 1 meets the lowest seed left.
Evidence: A screen recording at 375 px, and a screenshot of the semifinal at 375 and 1280 px, in the dark theme.

AT-32: The champion card
App: site
Stories: 47
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026`, press "Sim the season", and wait for the end.
Then: A full champion card shows the team and "Wins the title in N% of all 10,000 runs", where N is the team's title odds in `sim.json`.
Evidence: Screenshots of the champion card at 375, 768, and 1280 px, each in the light theme and the dark theme. Name N and the value in `sim.json`.

AT-33: The odds of all runs
App: site
Stories: 48
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026` and scroll to the sim.
Then: The playoff, bye, and title odds of all 10,000 runs show below the replay at every width.
Evidence: Screenshots of the sim chapter at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-34: Skip to the end
App: site
Stories: 49
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026`, press "Sim the season", then press "Skip to the end".
Then: The final state shows at once: the bracket complete and the champion card.
Evidence: Screenshots before and after the skip at 375 and 1280 px, in the dark theme.

AT-35: A fresh run
App: site
Stories: 50
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026`, press "Sim the season", and press it again in week 11.
Then: A new run starts at week 9, with no part of the old run left on the screen.
Evidence: A screen recording at 375 px.

AT-36: Reduced motion
App: site
Stories: 51
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published. The browser asks for reduced motion.
When: Open the report at `/midseason/2026` and press "Sim the season".
Then: Each beat changes with a fade or at once, with no movement, and the same facts show.
Evidence: A screen recording at 375 px with reduced motion on.

AT-37: The sim file
App: pipeline
Stories: 41, 48
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read `sim.json`.
Then: It holds 200 sim runs, the odds of 10,000 runs per team, and the seed odds. Its gzip size is 50 KB or less.
Evidence: The command output and the named fields of `sim.json` in the build folder. Give the gzip size.

AT-38: Sim parity
App: pipeline
Stories: 67
Given: CPC and NorCal 2026 week 8.
When: Run the sim parity test.
Then: For each team of each client, the sim's playoff odds are within 2 points of the published week 8 odds.
Evidence: The test output with the largest gap per client.

AT-39: The review file
App: pipeline
Stories: 61
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Open the review file in the build folder.
Then: Each blurb shows its prose block, the facts it cites, and the verifier result.
Evidence: The first 40 lines of the review file.

AT-40: Each prose block cites a fact
App: pipeline
Stories: 54, 53
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read the prose blocks in the review file.
Then: Each prose block cites at least one fact, and the verifier passes it.
Evidence: The review file entries of three prose blocks.

AT-41: Savage is the default
App: pipeline
Stories: 55, 76
Given: CPC 2026 week 8, with no `roast` value for `midseason` in a local copy of `client.toml`.
When: `make midseason CLIENT=cpc WEEK=8`
Then: The build runs at `savage`, and the review file names the level `savage`.
Evidence: The command output and the head of the review file. Put the config back after the run.

AT-42: An edit that adds an uncited number
App: pipeline
Stories: 62, 63
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`. One blurb in the draft is edited to add the number 999.
When: `make midseason-publish CLIENT=cpc WEEK=8`
Then: The publish refuses and names the blurb. `clients/cpc/published/2026/` does not change.
Evidence: The command output and `git status` of `clients/cpc/`.

AT-43: The publish
App: pipeline
Stories: 64
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`. Brian has read the review file.
When: `make midseason-publish CLIENT=cpc WEEK=8`
Then: The commit holds `midseason.json` and `sim.json` in `clients/cpc/published/2026/` and no file outside the client's season folders.
Evidence: The command output and `git show --stat` of the commit.

AT-44: The takeover
App: site
Stories: 56
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the home page.
Then: The top of the home page shows the takeover: the opener and a link to the report.
Evidence: Screenshots of the home page at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-45: The report tile
App: site
Stories: 57
Given: The CPC site with the midseason report of week 8 and 2026 week 10 published.
When: Open the home page.
Then: The home page shows its usual top and the report tile with one big fact and a link to the report.
Evidence: Screenshots of the home page at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-46: The menu
App: site
Stories: 58
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the home page and the menu.
Then: The dock and the menu have the same items as before the report.
Evidence: Screenshots of the dock and the open menu at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-47: The layers
App: pipeline
Stories: 66
Given: The Spec branch after the last ticket.
When: `make check` in `apps/pipeline/`.
Then: `test_layers.py` passes, and `midseason` and `sim` import only `league` and `facts`.
Evidence: The command output of the layer test.

AT-48: The config check
App: pipeline
Stories: 65, 66
Given: A local copy of `clients/cpc/client.toml` with `midseason` in the package list and no `sim`.
When: Run the config check of the client.
Then: The check fails and names the missing package `sim`.
Evidence: The command output. Put the file back after the run.

AT-49: No weekly rebuild
App: pipeline
Stories: none
Given: CPC 2026 week 8 with the report published.
When: `make build CLIENT=cpc WEEK=8`
Then: `midseason.json` and `sim.json` in `published/` do not change.
Evidence: The command output and `git status` of `clients/cpc/published/2026/`.

AT-50: No picks in the replay
App: site
Stories: none
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026` and look at the sim chapter.
Then: The sim chapter has no control to pick the winner of a game.
Evidence: Screenshots of the sim chapter at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-51: The weekly odds do not change
App: pipeline
Stories: none
Given: CPC 2026 week 8, before and after the report build.
When: `make midseason CLIENT=cpc WEEK=8`
Then: `clients/cpc/published/2026/rankings.json` does not change.
Evidence: The command output and `git status` of the file.

AT-52: Lean chapters
App: pipeline
Stories: 68
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Count the words of each prose block in `midseason.json`.
Then: Each prose block has 40 words or fewer.
Evidence: The command output and the word count of each block.

AT-53: Quick hits and Act III
App: site
Stories: 69, 18
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026` and scroll through Act II and Act III.
Then: Act II ends with Quick hits, which holds lineup choices and the injury toll. Act III holds the look ahead, then the sim.
Evidence: Screenshots of the end of Act II and all of Act III at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-54: The link to the sim
App: site
Stories: 70
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report and tap "See the sim" in the opener.
Then: The page moves to the sim chapter.
Evidence: Screenshots of the opener, and the page after the tap, at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-55: Quiet tags
App: site
Stories: 71, 20
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report and switch the Position top 10 to DEF.
Then: The DEF #3 row, the Buccaneers, reads "Free agent" in its second line. No tag in the report has a fill or a border.
Evidence: Screenshots of the DEF list, the draft busts, and the trade rows at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-56: Corners and controls
App: site
Stories: 72, 21
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report and look at the cards, the position switch, and "Show all".
Then: Cards have 8 px corners, and the report has no full pill. The switch is text with an underline under the chosen position. "Show all" is a text control with a chevron and no border.
Evidence: Screenshots of the Position top 10 and a long list at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-57: The awards as lines
App: site
Stories: 73
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report and scroll to the record book.
Then: Each award is one line, such as "MVP — Jahmyr Gibbs, Maye d'force B with U — 135.1 points over the line in his starts." No award is a card.
Evidence: Screenshots of the record book and the awards at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-58: Decimal places
App: site
Stories: 74
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report and read the DEF list and the record book.
Then: The DEF #3 shows 77.8 points. The highest score shows 158.96.
Evidence: Screenshots of the DEF list and the record book at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-59: The swap as best and worst
App: site
Stories: 15, 16
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report and scroll to the schedule swap.
Then: The swap is one text row per team, with no grid and no bar. The row of Bo Girds reads "Real 9-7", with "Best 14-2 on the schedule of Maye d'force B with U" and "+5".
Evidence: Screenshots of the schedule swap at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-60: The words of luck
App: site
Stories: 14, 13
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report and read the luck table.
Then: All You Need Is Love reads "+2.73" with "lucky" in the accent color. The Blue Tent at −0.09 reads "even".
Evidence: Screenshots of the luck table at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-61: No roast block
App: both
Stories: 75
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Read the chapters of `midseason.json`, then open the report on the site.
Then: No chapter in `midseason.json` has a `roast` field, and the page has no "The roast" heading.
Evidence: The named fields of `midseason.json`, and screenshots of two chapters at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-62: Four levels only
App: pipeline
Stories: 55
Given: CPC, with the `roast` value of `midseason` set to `nuclear` in a local copy of `client.toml`.
When: Run the config check.
Then: The check fails and names the four levels: `off`, `warm`, `hot`, and `savage`.
Evidence: The command output. Put the config back after the run.

AT-63: A fact from another chapter
App: pipeline
Stories: 77
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`.
When: Edit the luck blurb in the draft to cite the lineup fact "four wins over teams with the winning lineup benched", then run `make midseason-publish` in a clone whose remote is a local bare repo.
Then: The verifier passes the blurb, and the publish goes on.
Evidence: The edited blurb, the command output, and the verifier result.

AT-64: No Players to watch
App: site
Stories: none
Given: The CPC site with 2026 week 8 published and the midseason report of week 8 published.
When: Open the report at `/midseason/2026` and scroll through Act III.
Then: The report has no Players to watch chapter and no Grab him now.
Evidence: Screenshots of Act III at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-65: The letdowns
App: both
Stories: 25a
Given: CPC 2026 week 8, after `make midseason CLIENT=cpc WEEK=8`, with the report published on the site.
When: Read the draft facts of `midseason.json`, then open the report and scroll to the draft.
Then: Bijan Robinson shows as a letdown: $81, the top price of the draft, RB3 for the season, and no top 17 RB week since week 4. He is not in the busts.
Evidence: The named fields of `midseason.json`, and screenshots of the draft chapter at 375, 768, and 1280 px, each in the light theme and the dark theme.

## Trace

Story 1: AT-25
Story 2: AT-26
Story 3: AT-26
Story 4: AT-27
Story 5: AT-22
Story 6: AT-22
Story 7: AT-28
Story 8: AT-28
Story 9: AT-4
Story 10: AT-5
Story 11: AT-5
Story 12: AT-5
Story 13: AT-6
Story 14: AT-8, AT-60
Story 15: AT-7, AT-59
Story 16: AT-7, AT-59
Story 17: AT-6
Story 18: AT-9, AT-53
Story 19: AT-10
Story 20: AT-10, AT-55
Story 21: AT-11, AT-56
Story 22: AT-12
Story 23: AT-12
Story 24: AT-2, AT-13
Story 25: AT-12
Story 25a: AT-65
Story 26: removed by decision 15. AT-14 is retired.
Story 27: AT-15
Story 28: AT-15
Story 29: AT-15
Story 30: AT-16
Story 31: AT-16, AT-17
Story 32: AT-17
Story 33: AT-17
Story 34: AT-18
Story 35: AT-19
Story 36: AT-20
Story 37: AT-21
Story 38: AT-24
Story 39: removed by decision 15. AT-23 is retired.
Story 40: AT-29
Story 41: AT-30, AT-37
Story 42: AT-30
Story 43: AT-30
Story 44: AT-30
Story 45: AT-31
Story 46: AT-31
Story 47: AT-32
Story 48: AT-33, AT-37
Story 49: AT-34
Story 50: AT-35
Story 51: AT-36
Story 52: no test. Reason: the heat of the roast is a matter of taste, so Brian judges it in the review file.
Story 53: AT-40
Story 54: AT-40
Story 55: AT-41, AT-62
Story 56: AT-44
Story 57: AT-45
Story 58: AT-46
Story 59: AT-1
Story 60: AT-3
Story 61: AT-39
Story 62: AT-42
Story 63: AT-42
Story 64: AT-43
Story 65: AT-2, AT-48
Story 66: AT-47, AT-48
Story 67: AT-38
Story 68: AT-52
Story 69: AT-53
Story 70: AT-54
Story 71: AT-55
Story 72: AT-56
Story 73: AT-57
Story 74: AT-58
Story 75: AT-61. The voice itself has no test. Reason: it is a matter of taste, so Brian judges it in the review file.
Story 76: AT-41. The heat of savage has no test. Reason: it is a matter of taste, so Brian judges it in the review file.
Story 77: AT-63
Story 78: no test. Reason: the writer prompt holds the rule, and Brian checks the units in the review file.
Out of scope "A weekly rebuild of the report": AT-49
Out of scope "A live sim, on a server or in the browser, and a pick of a game's winner": AT-50
Out of scope "A move of the weekly odds onto the `sim` package": AT-51
Out of scope "A dock item for the report": AT-46
Out of scope "Players to watch, with Grab him now": AT-64

## Revisions

- 2026-11-06: Brian approved the changes of decisions 14 to 17. AT-14 and AT-23 are retired. AT-8, AT-40, and AT-41 changed. AT-52 to AT-64 are new.
