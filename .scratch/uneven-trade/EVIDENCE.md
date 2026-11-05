# Uneven trade: evidence

Spec: `.scratch/uneven-trade/PRD.md`. Acceptance tests: `.scratch/uneven-trade/ACCEPTANCE.md`.
Built from: `d3f9449e`, on 2026-11-05. The agent gives no Test verdict. Brian gives one for each test.

Each pipeline command fetched the rosters live from Sleeper on 2026-11-05 between 11:59 and 12:01 (-05:00).
The trade values come from the week 9 chart of `1QB0.5PPR4pt`, dated 2026-11-03, at `data/nfl/cache/charts/1QB0.5PPR4pt/week-09.json`.
On the day of the run: Walker 64.0, Washington 27.5, Higgins 38.5, Tuten 28.5, Pollard 17.5.
The `analyze` output prints no sums. Each `values.txt`, `sums.txt`, or `ranks.txt` holds the chart values and the arithmetic by hand.

## AT-1: A 3-for-2 trade uses the 1.10 margin

App: pipeline
Then: Bo Girds starts at D, 76.8 against 91.5. Teehee starts at B, 91.5 against 76.8. Each start reason names the discount of the extra player.
Files: `evidence/AT-1/output.txt`, `evidence/AT-1/values.txt`
Observation: Bo Girds shows "Start letter: D" and Teehee shows "Start letter: B". Both start reasons end "The side with more players counts its extra player at a discount before the sides count as even." By hand, 84.5 / 1.10 = 76.82 against 91.5.

## AT-2: A 4-for-3 trade uses the 1.10 margin

App: pipeline
Then: The sum of the side with 4 players is divided by 1.10 in both ratios, and each start reason names the discount.
Files: `evidence/AT-2/output.txt`, `evidence/AT-2/sums.txt`
Observation: The trade is Teehee (roster 12) gives Garrett Wilson, Luther Burden III, DJ Moore, and Sam LaPorta to London Cooking (roster 5) for Drake London, Michael Wilson, and Denzel Boston. By hand, 74.0 / 1.10 = 67.27 against 66.0, so both ratios fall in the C band, and the output shows C for both sides. Both start reasons name the discount; with no margin, London Cooking would read 1.12, the B band.

## AT-3: One for two keeps the 1.25 margin

App: pipeline
Then: Teehee starts at B, 64 against 53.6. Bo Girds starts at D, 53.6 against 64.
Files: `evidence/AT-3/output.txt`, `evidence/AT-3/values.txt`
Observation: Teehee shows "Start letter: B" and Bo Girds shows "Start letter: D". Both start reasons name the one-for-many margin. By hand, 67.0 / 1.25 = 53.6 against 64.0.

## AT-4: A 2-for-2 trade gets no margin

App: pipeline
Then: No start reason names a margin. Bo Girds starts at F, 67 against 91.5. Teehee starts at A, 91.5 against 67.
Files: `evidence/AT-4/output.txt`, `evidence/AT-4/values.txt`
Observation: Bo Girds shows "Start letter: F" with the reason "It gives far more trade value than it gets." Teehee shows "Start letter: A" with the reason "It gets far more trade value than it gives." Neither reason names a margin or a discount.

## AT-5: The side that gets a superstar steps up

App: pipeline
Then: Teehee's Superstar row is one step up: "Kenneth Walker III is a superstar, a top 8 player this week." Bo Girds' Superstar row is no step: "No player it gets is a superstar."
Files: `evidence/AT-5/output.txt`
Observation: Teehee shows "Superstar: one step up. Kenneth Walker III is a superstar, a top 8 player this week." Bo Girds shows "Superstar: no step. No player it gets is a superstar."

## AT-6: No superstar step with the 1.25 margin

App: pipeline
Then: Teehee's Superstar row is no step: "Kenneth Walker III is a superstar, but the one-for-many margin already counts him."
Files: `evidence/AT-6/output.txt`
Observation: Teehee shows "Superstar: no step. Kenneth Walker III is a superstar, but the one-for-many margin already counts him."

## AT-7: A superstar to each side

App: pipeline
Then: Each side's Superstar row is one step up and names the superstar it gets.
Files: `evidence/AT-7/output.txt`, `evidence/AT-7/ranks.txt`
Observation: The trade is Bo Girds (roster 6) gives Kenneth Walker III, rank 2, to Return of T Mac (roster 8) for Bijan Robinson, rank 5. Bo Girds shows "Superstar: one step up. Bijan Robinson is a superstar, a top 8 player this week." Return of T Mac shows "Superstar: one step up. Kenneth Walker III is a superstar, a top 8 player this week."

## AT-8: No chart this week reads the week before

App: pipeline
Then: Teehee's Superstar row reads "Kenneth Walker III is a superstar, a top 8 player last week." Both sides start at C.
Files: `evidence/AT-8/output.txt`
Observation: The test `test_with_no_chart_this_week_the_superstar_reads_the_saved_read_of_last_week` in `apps/pipeline/tests/test_rubric.py` shows PASSED, "1 passed in 0.22s". It checks both start letters at C and the Teehee reason "Kenneth Walker III is a superstar, a top 8 player last week."

## AT-9: The fairness line of trade W

App: pipeline
Then: The line reads "Fairness: Fair." Teehee's reason is the superstar reason, then ", but ", then its roster-fit reason. Bo Girds' reason is its roster-fit reason.
Files: `evidence/AT-9/output.txt`
Observation: The line reads "Fairness: Fair", with no period. Teehee reads "Kenneth Walker III is a superstar, a top 8 player this week, but you go from 2 RBs in the top 36 to 1 and keep 4 WRs in the top 36." Bo Girds reads its roster-fit reason, "You go from 3 RBs in the top 36 to 4 and keep 3 WRs in the top 36, and your lineup scores more."

## AT-10: A net below zero shows the first down step

App: pipeline
Then: The side's reason is the text of its first down step in rubric order.
Files: `evidence/AT-10/rubric-tests.txt`, `evidence/AT-10/output.txt`
Observation: The test `test_a_net_below_zero_gives_the_first_step_down_in_rubric_order` shows PASSED. In the real trade of AT-2, London Cooking has one step down, Injury, and no step up; its fairness reason is "Moore was on the injury report in 4 of 8 weeks.", the text of that step.

## AT-11: No steps shows the deal row

App: pipeline
Then: The side's reason is the deal row of its start letter.
Files: `evidence/AT-11/rubric-tests.txt`, `evidence/AT-11/output.txt`
Observation: The test `test_a_side_with_no_step_gets_the_deal_row_of_its_start_letter` shows PASSED. In the real trade of AT-4, Bo Girds starts at F with no adjuster step, and its fairness reason is "You give far more than you get."

## AT-12: A side at A shows its up step

App: pipeline
Then: The final letter stays A, and the side's reason is its first up step.
Files: `evidence/AT-12/rubric-tests.txt`, `evidence/AT-12/output.txt`
Observation: The test `test_a_side_at_a_with_a_net_above_zero_keeps_a_and_gives_its_step_up` shows PASSED. In the real trade of AT-4, Teehee starts at A with Roster fit and Superstar one step up each, shows "Final letter: A", and its fairness reason is the Roster fit text "You keep 2 RBs in the top 36 and keep 4 WRs in the top 36, and you get the better player."

## AT-13: The form names no chart while the analyzer runs

App: site
Then: The form reads "This can take up to a minute early in the week."
Files: `evidence/AT-13/375-light.png`, `evidence/AT-13/375-dark.png`, `evidence/AT-13/768-light.png`, `evidence/AT-13/768-dark.png`, `evidence/AT-13/1280-light.png`, `evidence/AT-13/1280-dark.png`, `evidence/AT-13/setup.txt`
Observation: Each screenshot shows trade W in the form, the button "Grading…", the heading "Grading the Trade", and the line "This can take up to a minute early in the week." The export called a local API of this branch with the test passphrase, and an `agent-browser` route held the analyze call open; `setup.txt` holds the commands.

## AT-14: The finder names no chart while it runs

App: site
Then: The finder reads "The search tries every small swap. This can take up to a minute early in the week."
Files: `evidence/AT-14/375-light.png`, `evidence/AT-14/375-dark.png`, `evidence/AT-14/768-light.png`, `evidence/AT-14/768-dark.png`, `evidence/AT-14/1280-light.png`, `evidence/AT-14/1280-dark.png`, `evidence/AT-14/norcal/375-light.png`, `evidence/AT-14/norcal/375-dark.png`, `evidence/AT-14/norcal/768-light.png`, `evidence/AT-14/norcal/768-dark.png`, `evidence/AT-14/norcal/1280-light.png`, `evidence/AT-14/norcal/1280-dark.png`, `evidence/AT-13/setup.txt`
Observation: For client `cpc`, `clients/cpc/client.toml` has `finder = false`, so each screenshot with Bo Girds (roster 6) chosen shows no "Find a Trade" section and no finder text. A second record on client `norcal`, which has `finder = true`, shows "Finding…" and "The search tries every small swap. This can take up to a minute early in the week." in all six files; the norcal brand has one dark set, so its light files show the dark theme.

## AT-15: The finder stays inside its speed bound

App: pipeline
Then: The test passes under its 5 s bound on both.
Files: `evidence/AT-15/output.txt`
Observation: On the Mac, `test_the_pair_with_the_most_candidates_runs_in_a_few_seconds` shows PASSED, with "2.14s call" and "1 passed in 2.29s". CI job link: added in the PR after the CI check runs.
