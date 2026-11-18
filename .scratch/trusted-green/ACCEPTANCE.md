# Trusted green: acceptance tests

Spec: `.scratch/trusted-green/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

App `root` names the root scripts, the CI workflows, and the `4ag` skills.

## Tests

AT-1: Both harnesses find the `verify` skill
App: root
Stories: 4, 8
Given: the Spec branch `trusted-green` after the last ticket.
When: the agent lists the skills of Claude Code and of `codex` at the root of the worktree.
Then: each list names `verify` once, and both resolve to the same `SKILL.md` file.
Evidence: the output of each skill list, and `git ls-files -s` of the link under the repo skill folder of Codex, with mode `120000`.

AT-2: A diff of the analyzer picks its flow
App: site
Stories: 5
Given: a diff that changes one file under the analyzer site folder only.
When: the agent runs the flow pick of `verify` on that diff.
Then: the pick names the flow "Analyzer" and no other flow.
Evidence: the diff stat and the output of the flow pick.

AT-3: A diff of the pipeline picks no flow
App: site
Stories: 5
Given: a diff that changes one file under `apps/pipeline/` only.
When: the agent runs the flow pick of `verify` on that diff.
Then: the pick names no flow and says that the rebuild covers the change.
Evidence: the diff stat and the output of the flow pick.

AT-4: A change to a shared part picks each flow
App: site
Stories: 5
Given: a diff that changes one file of the design package only.
When: the agent runs the flow pick of `verify` on that diff.
Then: the pick names all seven flows: Front door, Passphrase, Week report, Manager page, Analyzer, Power rankings, and Midseason report.
Evidence: the diff stat and the output of the flow pick.

AT-5: A green smoke run of cpc 2026 week 10
App: site
Stories: 1, 4, 9
Given: the client cpc with the published week 10 of 2026, the local API in its evidence mode, and a flow pick of all seven flows.
When: the agent runs one smoke run.
Then: the log shows each of the seven flows as passed, with shots at 390x660 in WebKit and 1280x800, in the light theme.
Evidence: the smoke log and the shots of each flow.

AT-6: A failed `expect` fails the smoke run
App: site
Stories: 7
Given: the flow "Week report" of cpc 2026 week 10, with one seeded step `expect` of the text "Week 99".
When: the agent runs one smoke run of that flow.
Then: the run exits red, and the log names the flow "Week report" and the failed `expect`.
Evidence: the smoke log and its exit code.

AT-7: An API error fails the smoke run
App: site
Stories: 7, 12
Given: the flow "Analyzer" of cpc 2026 week 10, with the local API stopped.
When: the agent runs one smoke run of that flow.
Then: the run exits red, and the log names the failed request to the API.
Evidence: the smoke log and its exit code.

AT-8: An overlap fails the smoke run
App: site
Stories: 7
Given: the flow "Week report" of cpc 2026 week 10, with one seeded style that puts one element over another.
When: the agent runs one smoke run of that flow.
Then: the run exits red, and the log names the two elements that overlap.
Evidence: the smoke log, its exit code, and the shot of the overlap.

AT-9: A layout flow adds the iPad sizes
App: site
Stories: 10
Given: the flows "Week report", a layout flow, and "Passphrase", not a layout flow, of cpc 2026 week 10.
When: the agent runs one smoke run of the two flows.
Then: the Week report has shots at 390x660, 810x980, 1080x740, and 1280x800, and the Passphrase flow has shots at 390x660 and 1280x800 only.
Evidence: the list of shot files of each flow.

AT-10: A flow that calls Claude runs once
App: site
Stories: 11, 12
Given: the flow "Analyzer" of cpc 2026 week 10, with the real local API.
When: the agent runs one smoke run of that flow.
Then: the flow has shots at one width only, and the API log shows one grade call.
Evidence: the list of shot files and the lines of the API log for the grade route.

AT-11: The acceptance defaults of the evidence runner stay
App: site
Stories: none
Given: a step list of the route `/2026/week-10/` with no widths and no themes.
When: the agent runs one evidence round of it.
Then: the round takes shots at 375, 768, and 1280 px, each in the light theme and the dark theme.
Evidence: the step list and the list of shot files.

AT-12: `4ag:implement` runs a smoke run before the Judge
App: root
Stories: 13, 15
Given: the skill text of `4ag:implement` on the Spec branch.
When: the agent runs the rule test of the skill text.
Then: the test passes, and the skill names a smoke run after the last ticket, the smoke folder of the evidence, and a stop on a red run before the Judge.
Evidence: the output of the rule test and the lines of the skill text that it reads.

AT-13: The quick Judge gets a third question
App: root
Stories: 14, 22
Given: `format.md` and `judge.md` of `4ag:quick` on the Spec branch.
When: the agent runs the rule test of the skill text.
Then: the test passes, `format.md` names the `Smoke:` block and the `Rebuild:` block, and the Judge brief holds "Does the smoke run show the changed flow at work?"
Evidence: the output of the rule test and the lines of the skill text that it reads.

AT-14: The re-run job passes a true quick file
App: root
Stories: 2, 16
Given: a real git repo in a temp folder, with a red commit whose loop fails and a fix commit whose loop passes, and a quick file that names both.
When: the agent runs the re-run script on it.
Then: the script exits 0 and names each item as held.
Evidence: the command, its output, and its exit code.

AT-15: A fake red fails the re-run job
App: root
Stories: 16
Given: the repo of AT-14, with a Red block whose command passes at the red commit.
When: the agent runs the re-run script on it.
Then: the script exits 1 and names the item whose red commit did not fail.
Evidence: the command, its output, and its exit code.

AT-16: A missing failure line fails the re-run job
App: root
Stories: 16
Given: the repo of AT-14, with a Red block that quotes a failure line that the command does not print.
When: the agent runs the re-run script on it.
Then: the script exits 1 and names the item and the missing line.
Evidence: the command, its output, and its exit code.

AT-17: A PR with no quick file passes the re-run job
App: root
Stories: 18
Given: the PR of the Spec branch `trusted-green`, which adds no quick file.
When: CI runs the re-run job on the PR.
Then: the job passes with the note "no quick file".
Evidence: the log of the job on the PR.

AT-18: The re-run job reads its script from `main`
App: root
Stories: 17
Given: the re-run workflow on the Spec branch.
When: the agent reads the checkout step of the workflow and the log of its run on the PR.
Then: the step checks out the script from the default branch, and the log shows a pass with a note while `main` has no re-run script.
Evidence: the lines of the workflow and the log of the job on the PR.

AT-19: A build saves its inputs before the first Claude call
App: pipeline
Stories: 24
Given: a detached scratch worktree of the Spec branch, the client cpc, 2026 week 10, and no API key in the environment.
When: the agent runs `build --no-fetch` of cpc week 10.
Then: the build stops at the first Claude call, and the week folder holds a new nflverse extract, a slow-source file, and a news file.
Evidence: the command, its last lines of output, and the size of each of the three files.

AT-20: A facts-only rebuild gives the same facts each time
App: pipeline
Stories: 20
Given: the three saved inputs of AT-19 for cpc 2026 week 10, and no secret in the environment.
When: the agent runs the facts-only rebuild two times.
Then: both runs give the same sha256 of `facts.json`, and neither run makes a network call.
Evidence: the two commands, the two sha256 values, and the log line that names the saved inputs.

AT-21: No change of code gives no diff
App: pipeline
Stories: 19
Given: the saved inputs of cpc and norcal 2026 week 10, and the Spec branch as both the base and the head.
When: the agent runs the base and head rebuild.
Then: the output reports 0 diffs for each client.
Evidence: the command and its output.

AT-22: An unlisted change of output fails
App: pipeline
Stories: 19, 23
Given: the inputs of AT-21, and a head with one seeded change that moves one waiver score of cpc.
When: the agent runs the base and head rebuild with no list of approved diffs.
Then: the run exits 1, and the output names cpc, `waiver.json`, and the JSON path of the score.
Evidence: the seeded diff, the command, its output, and its exit code.

AT-23: A listed change of output passes
App: pipeline
Stories: 21
Given: the seeded change of AT-22, and a `REBUILD.md` that lists cpc, `waiver.json`, that JSON path, and one sentence of reason.
When: the agent runs the base and head rebuild with that list.
Then: the run exits 0 and prints the listed diff with its reason.
Evidence: the list, the command, its output, and its exit code.

AT-24: A listed path that does not change fails
App: pipeline
Stories: 23
Given: the list of AT-23, with one extra path in norcal `page.json` that the change does not touch.
When: the agent runs the base and head rebuild with that list.
Then: the run exits 1, and the output names the extra path as listed but not changed.
Evidence: the list, the command, its output, and its exit code.

AT-25: The first PR runs the render diff only
App: pipeline
Stories: 30
Given: `main` at the start of the Spec branch, which has no facts-only rebuild.
When: the agent runs the base and head rebuild with `main` as the base.
Then: the run diffs the render only, prints "render only", and exits 0 when the render has no diff.
Evidence: the command, its output, and its exit code.

AT-26: The render diff is fast
App: pipeline
Stories: 20
Given: the saved facts of cpc and norcal 2026 week 10.
When: the agent runs the render diff of `page-json`, base and head, for both clients.
Then: the output reports 0 diffs, and the run takes under 60 s in total.
Evidence: the command, its output, and its time.

AT-27: Eight property tests pass
App: pipeline
Stories: 26
Given: the Spec branch after the last ticket.
When: the agent runs the property tests.
Then: the output lists eight properties as passed: score range and weight sum, letter order, thin depth, league scale, roster ranks, position ranks, star ranks, and handcuff value.
Evidence: the command and its output.

AT-28: A property test catches a seeded bug
App: pipeline
Stories: 26
Given: a scratch copy where `grade_letter` gives B for a score of 80.
When: the agent runs the property test of the letter order.
Then: the test fails, and the output shows a counterexample with two scores and their letters.
Evidence: the seeded diff, the command, and its output.

AT-29: CI runs grade-bar
App: root
Stories: 1, 27
Given: the PR of the Spec branch.
When: CI runs the site job of `Check`.
Then: the log shows the grade-bar project as passed in the norcal pass, and the job ends in under 25 min.
Evidence: the lines of the job log and the time of the job.

AT-30: A retry setting fails the rule test
App: root
Stories: 28
Given: a scratch copy of the Playwright config of the site with `retries: 1`.
When: the agent runs the rule test of the retry settings on it, then on the clean config.
Then: the rule test fails on the seeded copy and names the file, and it passes on the clean config.
Evidence: the seeded diff, the two commands, and their output.

AT-31: `AGENTS.md` states the flaky-test rule
App: root
Stories: 29
Given: `AGENTS.md` at the root of the Spec branch.
When: the agent reads it.
Then: it says to fix the cause of a flaky test or to delete it with the reason in the commit, and that a second run is never the fix.
Evidence: the lines of `AGENTS.md`.

AT-32: A PR of records only skips the heavy checks
App: root
Stories: 2, 3
Given: commit `c9b6282c` of the Spec branch, which changes only the map, the decision tickets, and `GLOSSARY.md`.
When: the agent runs the scope script of the checks on the diff of that commit.
Then: the script prints "records only", and it selects no smoke run, no re-run, and no rebuild.
Evidence: the command and its output.

AT-33: ADR 0037 records the rule
App: root
Stories: none
Given: `docs/adr/` on the Spec branch.
When: the agent reads ADR 0037.
Then: it states that each PR that changes code carries a smoke run, a re-run of its loop, and a base and head rebuild.
Evidence: the path and the lines of the ADR.

AT-34: Out of scope: the flow list has no egg board
App: site
Stories: none
Given: the flow list of `verify` on the Spec branch.
When: the agent reads each route of it.
Then: no flow names the route of the egg board.
Evidence: the routes of the flow list.

AT-35: Out of scope: no Proof trailer and no commit gate
App: root
Stories: none
Given: the Spec branch after the last ticket.
When: the agent diffs the hook config and the commit scripts against `main`.
Then: the diff adds no trailer check and no commit gate.
Evidence: the diff of the hook config and of the scripts that the hook calls.

AT-36: Out of scope: no Claude in the rebuild or the re-run
App: root
Stories: none
Given: the workflows of the rebuild job and the re-run job on the Spec branch.
When: the agent searches them for secrets.
Then: neither workflow names `ANTHROPIC_API_KEY` or `TYPESAFE_API_KEY`.
Evidence: the search command and its output.

## Trace

Story 1: AT-5, AT-29
Story 2: AT-14, AT-32
Story 3: AT-32
Story 4: AT-1, AT-5
Story 5: AT-2, AT-3, AT-4
Story 6: no test. Reason: added steps use the existing step list of the evidence runner, so no new behavior exists to check.
Story 7: AT-6, AT-7, AT-8
Story 8: AT-1
Story 9: AT-5
Story 10: AT-9
Story 11: AT-10
Story 12: AT-7, AT-10
Story 13: AT-12
Story 14: AT-13
Story 15: AT-12
Story 16: AT-14, AT-15, AT-16
Story 17: AT-18
Story 18: AT-17
Story 19: AT-21, AT-22
Story 20: AT-20, AT-26
Story 21: AT-23
Story 22: AT-13
Story 23: AT-22, AT-24
Story 24: AT-19
Story 25: no test. Reason: the publish already stages `clients/<slug>/data/<season>/`, so the saved inputs commit with no change to the publish.
Story 26: AT-27, AT-28
Story 27: AT-29
Story 28: AT-30
Story 29: AT-31
Story 30: AT-25
Out of scope "Spec 2, the record": AT-35
Out of scope "A full rebuild with Claude": AT-36
Out of scope "A flow of the egg board": AT-34
Out of scope "A measure of the rate of fix PRs": no test. Reason: no agent builds a measure by mistake, because no ticket names one.
Out of scope "The weekly publish": no test. Reason: the publish has no PR, so no check of this spec runs on it.
Out of scope "A fix of the flaky AT-5 wait-dips test": no test. Reason: it goes to its own quick run.

## Revisions

None yet.
