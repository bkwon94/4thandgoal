# Uneven trade: acceptance tests

Spec: `.scratch/uneven-trade/PRD.md`.

The Test verdict: only Brian gives one. He writes one PR comment on the Spec branch PR, with one line for each test: the id, then PASS, FAIL, or BLOCKED, then an optional note. The PR merges when every test has PASS (ADR 0020). An agent records the evidence and gives no Test verdict.

The grade reads the live snapshot, so a value can move after the week 9 games of 2026-11-08. Each value named below comes from the week 9 chart of `1QB0.5PPR4pt`: Walker 64.0, Washington 27.5, Higgins 38.5, Tuten 28.5, Pollard 17.5. The evidence agent records the values on the day of the run, and the trades of AT-2 and AT-7.

Run each pipeline command from the worktree of the Spec branch. Trade W is Brian's trade: `SIDES="6:9487@12,8151@12 12:6801@6,12490@6,5967@6" ASKER=6`. Roster 6 is Bo Girds. Roster 12 is Teehee.

## Tests

AT-1: A 3-for-2 trade uses the 1.10 margin
App: pipeline
Stories: 1, 5
Given: `2026` week 9, client `cpc`, trade W.
When: `make -C apps/pipeline analyze CLIENT=cpc SIDES="6:9487@12,8151@12 12:6801@6,12490@6,5967@6" ASKER=6`
Then: Bo Girds starts at D, 76.8 against 91.5. Teehee starts at B, 91.5 against 76.8. Each start reason names the discount of the extra player.
Evidence: the command and its output.

AT-2: A 4-for-3 trade uses the 1.10 margin
App: pipeline
Stories: 2
Given: `2026` week 9, client `cpc`, a real 4-for-3 trade that the evidence agent picks and records.
When: The `analyze` target grades the trade.
Then: The sum of the side with 4 players is divided by 1.10 in both ratios, and each start reason names the discount.
Evidence: the command, its output, and the sums by hand.

AT-3: One for two keeps the 1.25 margin
App: pipeline
Stories: 3
Given: `2026` week 9, client `cpc`. Roster 6 gives Kenneth Walker III (`8151`) to roster 12 for Tee Higgins (`6801`) and Bhayshul Tuten (`12490`). Roster 6 asks.
When: `make -C apps/pipeline analyze CLIENT=cpc SIDES="6:8151@12 12:6801@6,12490@6" ASKER=6`
Then: Teehee starts at B, 64 against 53.6. Bo Girds starts at D, 53.6 against 64.
Evidence: the command and its output.

AT-4: A 2-for-2 trade gets no margin
App: pipeline
Stories: 4
Given: `2026` week 9, client `cpc`. Trade W without Tony Pollard.
When: `make -C apps/pipeline analyze CLIENT=cpc SIDES="6:9487@12,8151@12 12:6801@6,12490@6" ASKER=6`
Then: No start reason names a margin. Bo Girds starts at F, 67 against 91.5. Teehee starts at A, 91.5 against 67.
Evidence: the command and its output.

AT-5: The side that gets a superstar steps up
App: pipeline
Stories: 6, 7, 8, 10, 12
Given: `2026` week 9, client `cpc`, trade W.
When: The command of AT-1 grades trade W.
Then: Teehee's Superstar row is one step up: "Kenneth Walker III is a superstar, a top 8 trade value this week." Bo Girds' Superstar row is no step: "No player it gets is a superstar."
Evidence: the command and its output.

AT-6: No superstar step with the 1.25 margin
App: pipeline
Stories: 11
Given: `2026` week 9, client `cpc`, the trade of AT-3.
When: The command of AT-3 grades the trade.
Then: Teehee's Superstar row is no step: "Kenneth Walker III is a superstar, but the one-for-many margin already counts him."
Evidence: the command and its output.

AT-7: A superstar to each side
App: pipeline
Stories: 9, 13
Given: `2026` week 9, client `cpc`, a real trade of two week 9 superstars on two rosters, which the evidence agent picks and records.
When: The `analyze` target grades the trade.
Then: Each side's Superstar row is one step up and names the superstar it gets.
Evidence: the command, its output, and the rank of each superstar on the week 9 chart.

AT-8: No chart this week reads the week before
App: pipeline
Stories: 14, 15
Given: `2026` week 9 with no week 9 chart, and the real saved read of the week 8 chart in place. The week 9 chart exists, so a rubric test removes it. We do not wait for week 10.
When: The rubric test grades trade W.
Then: Teehee's Superstar row reads "Kenneth Walker III is a superstar, a top 8 trade value last week." Both sides start at C.
Evidence: the test name, the test command, and its output.

AT-9: The fairness line of trade W
App: pipeline
Stories: 16, 18
Given: `2026` week 9, client `cpc`, trade W.
When: The command of AT-1 grades trade W.
Then: The line reads "Fairness: Fair." Teehee's reason is the superstar reason, then ", but ", then its roster-fit reason. Bo Girds' reason is its roster-fit reason.
Evidence: the command and its output.

AT-10: A net below zero shows the first down step
App: pipeline
Stories: 17
Given: `2026` week 9, a side whose adjuster steps sum below zero.
When: The grade writes the fairness line.
Then: The side's reason is the text of its first down step in rubric order.
Evidence: the rubric test output, and a real trade with the command and its output if the agent finds one.

AT-11: No steps shows the deal row
App: pipeline
Stories: 19
Given: `2026` week 9, a side with no adjuster step.
When: The grade writes the fairness line.
Then: The side's reason is the deal row of its start letter.
Evidence: the rubric test output, and a real trade with the command and its output if the agent finds one.

AT-12: A side at A shows its up step
App: pipeline
Stories: 20
Given: `2026` week 9, a side that starts at A and has a net above zero.
When: The grade writes the fairness line.
Then: The final letter stays A, and the side's reason is its first up step.
Evidence: the rubric test output, and a real trade with the command and its output if the agent finds one.

AT-13: The form names no chart while the analyzer runs
App: site
Stories: 21
Given: The analyze route of client `cpc`, with trade W in the form.
When: The reader taps the button that grades the trade, and the grade is still in progress.
Then: The form reads "This can take up to a minute early in the week."
Evidence: screenshots of the form while it runs at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-14: The finder names no chart while it runs
App: site
Stories: 22
Given: The finder of client `cpc`, with roster 6 chosen.
When: The reader starts a search, and the search is still in progress.
Then: The finder reads "The search tries every small swap. This can take up to a minute early in the week."
Evidence: screenshots of the finder while it runs at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-15: The finder stays inside its speed bound
App: pipeline
Stories: 25
Given: The finder speed test in `apps/pipeline/tests/test_finder.py`, with the Superstar adjuster in rubric order.
When: The test runs on the Mac and in CI.
Then: The test passes under its 5 s bound on both.
Evidence: the test command, its output with the time, and the CI job link.

## Trace

Story 1: AT-1
Story 2: AT-2
Story 3: AT-3
Story 4: AT-4
Story 5: AT-1
Story 6: AT-5
Story 7: AT-5
Story 8: AT-5
Story 9: AT-7
Story 10: AT-5
Story 11: AT-6
Story 12: AT-5
Story 13: AT-7
Story 14: AT-8
Story 15: AT-8
Story 16: AT-9
Story 17: AT-10
Story 18: AT-9
Story 19: AT-11
Story 20: AT-12
Story 21: AT-13
Story 22: AT-14
Story 23: no test. Reason: no reader sees the tunables. The code review checks the names.
Story 24: no test. Reason: no reader sees the match. The code review checks the rubric text and the glossary.
Story 25: AT-15
Out of scope "A change to `CLAMP_STEPS = 1`": no test. Reason: no ticket touches the clamp.
Out of scope "A change to the fairness block of the site": no test. Reason: no ticket touches the block.
Out of scope "A superstar rank that grows with the league size": no test. Reason: no ticket touches the league settings.
Out of scope "A down step for the side that gives a superstar": AT-5

## Revisions

None yet.
