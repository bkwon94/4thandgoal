# Manager brain: acceptance tests

Spec: `.scratch/manager-brain/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

The live tests run on the local API pair (`make api` in the pipeline, `make dev-local` in the site) with the current cpc rosters of season 2026, and with the real Advisor, the real Jev, and the real Sleeper news feed. The live eval runs on the 28 trades of the test set of decision 04: real trades of 2026 weeks 6 and 7, and trades of 2026 week 8. The test set stays out of the repo. The eval saves the fact sheet of each trade with its read, and the fact tests use those sheets as evidence. A Lean comes from a model, so a test that checks a Lean accepts a range of Leans.

## Tests

AT-1: The chart cache trusts the hash of the PNG
App: pipeline
Stories: 51
Given: the cpc chart of 2026 week 8 is read, and its saved read holds the hash of its PNG.
When: touch the PNG so that its file time is newer than the JSON, and run `cornerstone chart --client cpc --week 8`. Then change one byte of a copy of the PNG, put it in place, and run the command again.
Then: the first run reads nothing again. The second run reads the chart again.
Evidence: the output of both runs, and the hash in the saved read before and after.

AT-2: The build log says when a week has no chart
App: pipeline
Stories: 50
Given: the chart cache of cpc holds no PNG for one week of 2026.
When: run the build of that week.
Then: the build log has one plain line that says the week has no chart.
Evidence: the command and the log line.

AT-3: The manual chart step reads a placed chart
App: pipeline
Stories: 49
Given: the PNG of 2026 week 8 is placed by hand in the chart cache of cpc.
When: `cornerstone chart --client cpc --week 8`
Then: the command reads the PNG and prints the count of chart rows it read.
Evidence: the command output.

AT-4: The sheet states the RB depth after the trade for each side
App: pipeline
Stories: 16, 17, 47
Given: the live eval sheet of trade 6, behold the lamb gets Omar Cooper Jr. and Puka Nacua and gives Saquon Barkley and CeeDee Lamb.
When: read the depth facts of both sides on the sheet.
Then: each side has a fact in the shape "RBs in the top 36 go from N to M", and N and M match the rosters before and after the trade. The sheet also states the depth of the other team at the positions of the trade.
Evidence: the depth facts of the sheet and the two rosters.

AT-5: The sheet gives the past-season splits with their game counts
App: pipeline
Stories: 22, 23
Given: the live eval sheet of trade 12, Lil Fridge gives Derrick Henry.
When: read the history facts of Derrick Henry.
Then: for each of 2023, 2024, and 2025, the sheet gives his half-PPR points per game in weeks 1 to 8 and in weeks 9 to 17, and in cold games, each with its game count.
Evidence: the history facts of the sheet.

AT-6: A player with no past season gets no number
App: pipeline
Stories: 24
Given: the live eval read of trade 6, which holds the rookie Omar Cooper Jr.
When: read his facts and every Bullet and the Case.
Then: the sheet has no split fact for him, and no Bullet and no sentence of the Case gives him a number from a past season.
Evidence: his facts and the read.

AT-7: A past-season file downloads once
App: pipeline
Stories: 67
Given: the live eval ran once, so the nflverse files of 2023 to 2025 are in the cache.
When: run one analyze press of a trade with a veteran player.
Then: the log shows no download of a past-season file.
Evidence: the log of the press and the file times of the cache.

AT-8: The sheet holds the quality of the NFL team
App: pipeline
Stories: 18
Given: the live eval sheet of trade 24, NFC Least gets Omarion Hampton.
When: read the facts of Omarion Hampton.
Then: the sheet has a fact on the quality of his NFL team.
Evidence: the fact.

AT-9: The sheet holds the race group, the odds, and the bye of each side
App: pipeline
Stories: 19, 20, 21
Given: a live analyze press of a cpc trade in the current week, where one side starts a player whose NFL team has a bye in the trade week.
When: read the team facts of the sheet.
Then: each side has its race group (In, Bubble, or Out) and its playoff odds. The side with the bye has a bye fact.
Evidence: the team facts of the sheet.

AT-10: A week with no chart still grades
App: pipeline
Stories: 28
Given: the local API with the chart of the current week moved out of the cache.
When: POST `/analyze` with the trade of AT-16.
Then: the response is a read with a Lean, and the Case says the chart is missing.
Evidence: the request and the response.

AT-11: A player who is not on the chart stays in play
App: pipeline
Stories: 27, 29
Given: a cpc player on a roster who has no row on the chart of the current week.
When: read his fact on a sheet, and press Find for his team with no partner.
Then: his fact says he is not on the chart, and the target step of the Finder log lists him among the players it asks about.
Evidence: the fact and the Finder log.

AT-12: The sheet holds the news of a trade player
App: pipeline
Stories: 25
Given: the live eval sheet of trade 30, Unsolicited Dak Picks gives Jonathan Taylor, run on a live press.
When: read the facts of Jonathan Taylor whose id starts with `NEWS.6813.`.
Then: there are at most 2, newest first. Each text starts "Reported on <YYYY-MM-DD> by <Source>:", each date is in the last 7 days, and no URL is in the numbers.
Evidence: the news facts and the time of the press.

AT-13: A Bullet that cites news names the report
App: pipeline
Stories: 26, 56
Given: the live eval reads.
When: list every Bullet that cites a `NEWS.` fact.
Then: each one holds "reported", "report", "per", "according to", "rumor", or the source name.
Evidence: the list of those Bullets.

AT-14: A failed news fetch never stops a grade
App: pipeline
Stories: 66
Given: the local API with the host of the Sleeper news feed blocked on the machine.
When: POST `/analyze` with the trade of AT-16.
Then: the response is 200 with a read, and the sheet has no `NEWS.` fact.
Evidence: the block, the request, the response, and the log.

AT-15: The news of a player is cached for 1 hour
App: pipeline
Stories: 65
Given: the local API after one press of the trade of AT-16.
When: press a different trade with one of the same players within 1 hour.
Then: the log shows no news fetch for that player on the second press.
Evidence: the log of both presses.

AT-16: The analyze document holds the Lean, the Case, and the Bullets
App: pipeline
Stories: 1, 9, 10, 11, 62
Given: the local API with the current cpc rosters.
When: POST `/analyze` with Maye d'force B with U giving Jahmyr Gibbs to Return of T Mac for Bijan Robinson.
Then: the document has a `lean` of Send it, Lean yes, Gut call, Lean no, or Pass, a `case`, and a fairness block. Each side has 3 to 5 Bullets, each with `text`, `mark`, `fact_id`, and `fact_text`. No key holds a letter, a factor, a decision, or an answer.
Evidence: the request and the response.

AT-17: A clear loss reads as a loss
App: pipeline
Stories: 1, 9
Given: the local API with the current cpc rosters.
When: POST `/analyze` with All You Need Is Love giving Ja'Marr Chase to NFC Least for Xavier Worthy.
Then: the Lean is Pass or Lean no, and the fairness is lopsided with All You Need Is Love as the side that gives more.
Evidence: the request and the response.

AT-18: The Case leads with its condition
App: pipeline
Stories: 5
Given: the response of AT-16.
When: read the first sentence of the Case.
Then: it holds a condition, with "if" or "as long as".
Evidence: the Case.

AT-19: Every number, name, and fact id comes from the sheet
App: pipeline
Stories: 53, 54
Given: the 28 live eval reads and their sheets.
When: check each Bullet and each Case against its sheet.
Then: each cited fact id is on its sheet, and each number and each player name in a Bullet or a Case is in a cited fact.
Evidence: the check output for the 28 reads.

AT-20: No inner word reaches a read
App: pipeline
Stories: 55
Given: the 28 live eval reads.
When: search each Bullet and each Case for the inner words.
Then: no read holds "trade value" or "return bet".
Evidence: the search output.

AT-21: A failed Advisor gives an honest error that costs no grade
App: pipeline
Stories: 30, 31, 58
Given: the local API started with an Anthropic key that is not valid.
When: POST `/analyze` with the trade of AT-16.
Then: the response is a plain error with no read, the log shows two Advisor calls, and the grade count of the passphrase does not change.
Evidence: the response, the log, and the grade count before and after.

AT-22: A repeat press gives the same read
App: pipeline
Stories: 32
Given: the local API after one press of the trade of AT-16.
When: press the same trade again.
Then: the second document is the same as the first, and the log shows a cache hit.
Evidence: the two documents and the log.

AT-23: The document version changes
App: pipeline
Stories: 63
Given: `main` and the Spec branch.
When: read the version of the analyze document on each.
Then: the two versions differ.
Evidence: the two values.

AT-24: The Jev checks log and never block
App: pipeline
Stories: 57
Given: the live eval run.
When: read its log.
Then: the log has the result of the Jev faithfulness check and of the Jev rumor check for the Bullets, and each of the 28 trades still has a read.
Evidence: the log lines.

AT-25: Jev requests stay under the rate limit
App: pipeline
Stories: 64
Given: the local API.
When: press Find for Maye d'force B with U with no partner.
Then: the log shows the Jev requests in waves and no 429 response.
Evidence: the log of the press.

AT-26: Find with no partner searches the whole league
App: pipeline
Stories: 33, 35, 39
Given: the local API with the current cpc rosters.
When: POST `/find` for Maye d'force B with U with no partner.
Then: the log shows the partner filter on all 11 other teams. The document has 1 to 3 picks, each with a headline and 2 to 4 Bullets, or a plain empty line.
Evidence: the request, the response, and the log.

AT-27: Find with one partner keeps to that partner
App: pipeline
Stories: 34
Given: the local API with the current cpc rosters.
When: POST `/find` for Maye d'force B with U with The Blue Tent as the partner.
Then: every pick is a trade with The Blue Tent.
Evidence: the request and the response.

AT-28: No offer breaks a hard rule
App: pipeline
Stories: 38
Given: the log of the press of AT-26.
When: list every offer that code built.
Then: no offer holds a kicker, a defense, a player out with no return week, or a handcuff.
Evidence: the offer list.

AT-29: Every offer is a small trade
App: pipeline
Stories: 37
Given: the offer list of AT-28.
When: count the players on each side of each offer.
Then: every offer is 1-for-1, 2-for-1, or 1-for-2.
Evidence: the counts.

AT-30: A failed Advisor in the Finder gives the shortlist
App: pipeline
Stories: 44
Given: the local API started with an Anthropic key that is not valid.
When: POST `/find` for Maye d'force B with U with no partner.
Then: the document has the fallback flag true and the shortlist offers, each with plain fact lines.
Evidence: the request and the response.

AT-31: The Finder no longer offers Gibbs for Bijan
App: pipeline
Stories: 42
Given: the local API with the current cpc rosters.
When: POST `/find` for Maye d'force B with U with Return of T Mac as the partner.
Then: no pick sends Jahmyr Gibbs for Bijan Robinson.
Evidence: the request and the response.

AT-32: The analyzer agrees with a Finder pick
App: pipeline
Stories: 41, 42
Given: the picks of AT-26.
When: POST `/analyze` with each pick.
Then: each read has a Lean of Send it, Lean yes, or Gut call.
Evidence: the requests and the responses.

AT-33: A press stays in time and in cost
App: pipeline
Stories: 45, 52
Given: the local API with a cold result cache.
When: press the trade of AT-16 5 times, then press Find for Maye d'force B with U with no partner 5 times, each with a cold result cache.
Then: at least 4 of the 5 analyze presses take 30 s or less, and all 5 cost $0.15 or less. At least 4 of the 5 Finder presses take 35 s or less, and all 5 cost $0.15 or less.
Evidence: the log lines with the time and the cost of each press.

AT-34: The live eval reads all 28 trades
App: pipeline
Stories: 3, 4, 7, 8, 46, 47, 48
Given: the test set of 28 trades.
When: run the live eval script.
Then: each trade has a Lean, a Case, and 3 to 5 Bullets per side, with no check failure after the retry. The Leans cover at least 3 of the 5 steps of the scale. The output has the cost and the time of the run.
Evidence: the eval summary, with the 28 Leans, the cost, and the time. The full output stays out of the repo.

AT-35: Each client has a Playbook
App: pipeline
Stories: 46, 47
Given: the Spec branch.
When: open the voice folders of cpc and of NorCal.
Then: cpc has a Playbook with its tips: RBs first in half PPR, contenders firm up, bubble teams take risks, a top 3 to 5 player beats two good ones, and managers here chase recent points. NorCal has a Playbook with general tips and no league-specific claim.
Evidence: the two files.

AT-36: The rubric and its words are gone
App: both
Stories: 60, 61
Given: the Spec branch.
When: search the code and the page copy of the analyzer and the Finder.
Then: no code or copy holds a rubric, a start letter, a breakdown, an adjuster step, a verdict, a factor row, or a letter of a side. Each old adjuster writes facts as a Measure.
Evidence: the search commands and their output.

AT-37: ADR 0030 is accepted
App: pipeline
Stories: 68
Given: the Spec branch at the PR.
When: open ADR 0030 and `GLOSSARY.md`.
Then: the ADR status reads accepted, and the glossary holds no term that the ADR drops.
Evidence: the status line and a search of the glossary.

AT-38: The hero shows the Lean on its scale
App: site
Stories: 1, 2
Given: the local site and API, after the press of AT-16.
When: read the hero.
Then: the hero shows the Lean word, and under it the 5-step scale from Pass to Send it with the step of that Lean lit.
Evidence: screenshots of the analyzer result at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-39: The Case is clamped on the phone
App: site
Stories: 6
Given: the result of AT-38 at 375 px.
When: tap "Read the full case".
Then: before the tap the Case shows 3 lines. After the tap it shows in full.
Evidence: screenshots at 375 px before and after the tap, in the light theme and the dark theme.

AT-40: The hero shows the fairness line
App: site
Stories: 9
Given: the local site after the press of AT-17.
When: read the hero.
Then: the hero shows "Lopsided: All You Need Is Love gives more."
Evidence: screenshots of the hero at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-41: One tab per team, the asker first
App: site
Stories: 10, 13
Given: the result of AT-38.
When: tap the tab of Return of T Mac.
Then: before the tap, the tab of Maye d'force B with U is open. After the tap, the Bullets of Return of T Mac show.
Evidence: screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-42: The Bullets sit in bands with their Marks
App: site
Stories: 11, 12
Given: the result of AT-38.
When: read the open tab.
Then: the Bullets sit in For, then Against, then Even bands, with ▲, ▼, and – Marks. A band with no Bullet does not show.
Evidence: screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-43: A tap on a Bullet shows its fact
App: site
Stories: 14
Given: the result of AT-38.
When: tap the first Bullet row.
Then: its fact text opens under the row.
Evidence: screenshots at 375, 768, and 1280 px after the tap, each in the light theme and the dark theme.

AT-44: A screen reader hears the Mark as a word
App: site
Stories: 11
Given: the result of AT-38.
When: read the accessibility tree of a Bullet row.
Then: the row reads "for", "against", or "even", and the glyph is hidden.
Evidence: the accessibility tree of three rows, one per Mark.

AT-45: A 3-team trade shows three tabs
App: site
Stories: 13
Given: the local site and API with the current cpc rosters.
When: grade a trade of three cpc teams.
Then: the switcher shows one tab per team, three in all.
Evidence: screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-46: No letter shows
App: site
Stories: 15
Given: the results of AT-38 and AT-47.
When: read the analyzer result and the Finder cards.
Then: no letter grade shows on either page.
Evidence: the screenshots of AT-38 and AT-47, and a search of the rendered text for a letter grade.

AT-47: The Finder card uses the same rows
App: site
Stories: 39, 40, 41
Given: the local site and API, after Find for Maye d'force B with U with no partner.
When: read a card, then tap "See the full result".
Then: the card shows a headline, the swap, and 2 to 4 Bullet rows with the same Marks and tap as the analyzer. The tap opens the analyzer read of that trade.
Evidence: screenshots of the card and of the read at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-48: Find works with no partner picked
App: site
Stories: 33, 34
Given: the local site and API.
When: press Find with no partner picked.
Then: the button is on, and the press shows picks or the plain empty line.
Evidence: screenshots before and after the press at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-49: The page shows the honest error
App: site
Stories: 30
Given: the local site with the API of AT-21.
When: grade the trade of AT-16.
Then: the page shows a plain error and Try Again, and no Lean.
Evidence: screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-50: The copy says no "rival" and no name of the commissioner
App: both
Stories: 59
Given: the Spec branch and the 28 live eval reads.
When: search the page copy and the reads for "rival" and for "Brian" as the name of the commissioner.
Then: neither appears. A player whose name holds "Brian", such as Brian Robinson, does not count.
Evidence: the search commands and their output.

AT-51: Reduced motion shows the page at rest
App: site
Stories: none
Given: the result of AT-38 with reduced motion on.
When: load the result.
Then: the Lean word and the Bullets show at once, with no rise.
Evidence: screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme, with reduced motion on.

AT-52: The Finder builds no 2-for-2 trade
App: pipeline
Stories: none
Given: the offer list of AT-28.
When: count the players on each side of each offer.
Then: no offer is 2-for-2 or larger.
Evidence: the counts.

AT-53: A press makes no web search
App: pipeline
Stories: none
Given: the logs of AT-16 and AT-26.
When: search the logs for a web search call.
Then: neither press makes a web search call.
Evidence: the search output.

## Trace

Story 1: AT-16, AT-17, AT-38
Story 2: AT-38
Story 3: AT-34
Story 4: AT-34. Brian reacts to the voice of the eval reads.
Story 5: AT-18
Story 6: AT-39
Story 7: AT-34. Brian reacts to the voice of the eval reads.
Story 8: AT-34. Brian reacts to the voice of the eval reads.
Story 9: AT-16, AT-17, AT-40
Story 10: AT-16, AT-41
Story 11: AT-16, AT-42, AT-44
Story 12: AT-42
Story 13: AT-41, AT-45
Story 14: AT-43
Story 15: AT-46
Story 16: AT-4
Story 17: AT-4
Story 18: AT-8
Story 19: AT-9
Story 20: AT-9
Story 21: AT-9
Story 22: AT-5
Story 23: AT-5
Story 24: AT-6
Story 25: AT-12
Story 26: AT-13
Story 27: AT-11
Story 28: AT-10
Story 29: AT-11
Story 30: AT-21, AT-49
Story 31: AT-21
Story 32: AT-22
Story 33: AT-26, AT-48
Story 34: AT-27, AT-48
Story 35: AT-26
Story 36: no test. Reason: the targets come from Jev judgments, and Brian checked them in prototype 04. AT-11 shows that a player with no chart row still reaches the target step.
Story 37: AT-29
Story 38: AT-28
Story 39: AT-26, AT-47
Story 40: AT-47
Story 41: AT-32, AT-47
Story 42: AT-31, AT-32
Story 43: no test. Reason: no real cpc asker gives an empty Finder now. The route tests of the API cover the empty line.
Story 44: AT-30
Story 45: AT-33
Story 46: AT-34, AT-35
Story 47: AT-4, AT-34, AT-35
Story 48: AT-34. Brian reacts to the voice of the eval reads.
Story 49: AT-3
Story 50: AT-2
Story 51: AT-1
Story 52: AT-33
Story 53: AT-19
Story 54: AT-19
Story 55: AT-20
Story 56: AT-13
Story 57: AT-24
Story 58: AT-21
Story 59: AT-50
Story 60: AT-36
Story 61: AT-36
Story 62: AT-16
Story 63: AT-23
Story 64: AT-25
Story 65: AT-15
Story 66: AT-14
Story 67: AT-7
Story 68: AT-37
Out of scope "Finder trades of 2-for-2 and larger": AT-52
Out of scope "The waiver web search for trade players": AT-53
Out of scope "A Jev check that blocks a read": AT-24
Out of scope "A free-text trade request": no test. Reason: no part of the spec builds a text input.
Out of scope "The Jev checks of the weekly copy": no test. Reason: no ticket of this spec touches the weekly copy.
Out of scope "Suggested counters": no test. Reason: no ticket of this spec touches the slot.

## Revisions

- 2026-11-10, AT-50, by Brian: the search for "Brian" is for the name of the commissioner. An NFL player whose name holds "Brian", such as Brian Robinson, does not count. Reason: the live reads name Brian Robinson as a trade player, and the rule of story 59 is about the commissioner.
- 2026-11-10, AT-26 and AT-47, by Brian: a Finder pick holds 2 to 4 Bullets, not 2 to 3. Reason: the API does not enforce an array count, so a pick with a 4th Bullet made the guard retry, and the retry put the Finder press over the time and cost limits of AT-33. The PRD (story 39 and the press output) and ticket 10 say the same.
- 2026-11-10, AT-33, by Brian: the test takes 5 cold presses of each kind. At least 4 of 5 hold the time limit, and all 5 hold the cost cap. Reason: the time of one call varies by a few seconds, and one cold analyze press took 30.9 s while others took 24 to 27 s with no change to the code.
- 2026-11-10, AT-34, by Brian: the Leans cover at least 3 of the 5 steps of the scale, in place of at least one Gut call. Reason: the point is that the Advisor uses the scale, not one fixed word, and one run had no Gut call while the runs before each had one.
