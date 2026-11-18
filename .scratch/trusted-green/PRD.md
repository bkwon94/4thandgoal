# Trusted green: the checks that let a green PR merge with no second look

Status: ready-for-agent
Date: 2026-11-18
Apps: both. The site gets the smoke run, the verb `expect` of the evidence runner, and grade-bar in CI. The pipeline gets the pinned build inputs, the base and head rebuild, and the property tests of the grades. The root gets the re-run job, the flaky-test rule, and the changes to the `4ag` skills.
Spec branch: `trusted-green`.
Source: the map `.scratch/trusted-green/MAP.md` and decision tickets 01 to 11. The article "How the Claude Code team thinks about verification" (https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/). ADRs 0015, 0019, 0025, 0026, 0033.
Tickets: 01 to 11, in `issues/`.

## Problem Statement

Brian merges each PR. A green `Check` does not yet tell him that the change works. So he looks at the diff again before the merge, and he still finds work to fix after it, such as #65 after #64 and #47 after #46.

The checks have five gaps:

1. No agent runs the app before the PR opens. The unit tests can pass while the flow is broken.
2. The quick Judge trusts the Red and Green blocks that the builder pastes. No one runs those commands again.
3. A flaky test gets a second run, not a fix. The AT-5 wait-dips test is one example.
4. A check exists that CI never runs: grade-bar.
5. No check compares the output of the pipeline before and after a change. No property test covers the grades.

## Solution

Each PR that changes code carries its own proof, and a change cannot edit the check that judges it. When the PR opens, five things hold:

1. The `verify` skill booted the site and the API, and drove each flow that the diff touches. The smoke run was green, and the Judge saw its shots.
2. For a quick run, CI ran each Red command at its red commit and each Green command at its fix commit, with a script from `main`.
3. CI rebuilt the facts and the render of the latest week from the saved inputs, with the code of `main` and with the code of the PR. Each difference is on a list of approved diffs, and each listed reason names the change.
4. CI ran grade-bar, the property tests of the grades, and a rule that fails on each retry setting.
5. A PR of records only gets the plain `Check`.

Brian then reads the evidence, not the diff, and merges.

## User Stories

1. As Brian, I want a green PR to mean the change works in the running app, so that I merge with no second look at the diff.
2. As Brian, I want each PR that changes code to get the same proof, so that the proof does not depend on the skill that opened the PR.
3. As Brian, I want a PR of records only to skip the heavy checks, so that a tracker change stays fast.
4. As an agent, I want one `verify` skill that boots the site and the API, so that I can drive a flow the way a person does.
5. As an agent, I want the flow list to pick the flows from my diff, so that I do not invent the rubric that judges my own work.
6. As an agent, I want to add steps for my change to a picked flow, so that the smoke run covers what I changed.
7. As an agent, I want the smoke run to fail on a missing element, a failed `expect`, a page error, a console error, an API error, or an overlap, so that a broken flow cannot give a green run.
8. As an agent in Codex, I want to find `verify` through the same path as the `4ag` skills, so that both harnesses run one skill.
9. As Brian, I want the smoke run to use the iPhone WebKit size and the desktop size, so that it checks the phone first.
10. As Brian, I want a flow marked as a layout change to add the two iPad sizes, so that a layout change gets each size.
11. As Brian, I want a flow that calls Claude to run once at one width, so that a smoke run costs a few cents.
12. As Brian, I want the smoke run to call the real API and the real Claude, so that no mock hides a break.
13. As the Judge, I want the shots and the log of the smoke run, so that I see the running app and not only test output.
14. As the quick Judge, I want a third question for each item that touches the site or the API, so that an item with a broken flow gets no PASS.
15. As Brian, I want a red smoke run to stop the work before the Judge, so that a broken flow never reaches a PR.
16. As Brian, I want CI to run the Red and Green commands of a quick run again, so that a pasted block cannot hide a loop that never went red.
17. As Brian, I want the re-run job to read its script from `main`, so that a PR cannot edit the check that judges it.
18. As an agent, I want the re-run job to pass a PR with no quick file, so that a spec PR does not wait on it.
19. As Brian, I want CI to rebuild the latest week with the code of `main` and with the code of the PR, so that each change of output shows.
20. As an agent, I want the rebuild to need no secret and no network, so that it runs in CI in seconds.
21. As an agent, I want to list each change of output on purpose with a reason, so that a planned change passes.
22. As the Judge, I want the list of approved diffs as evidence, so that I check each reason against the test or the done condition.
23. As Brian, I want an unlisted change of output to fail the PR, so that a side effect never merges unseen.
24. As the pipeline, I want each build to save its inputs into the week folder, so that a later build can give the same facts.
25. As the publish, I want to commit the saved inputs with the week, so that CI has them.
26. As an agent, I want property tests on the pure functions of the grades, so that edge cases that I did not think of get tested.
27. As Brian, I want CI to run grade-bar, so that each check that exists also runs.
28. As Brian, I want a rule that fails on each retry setting, so that a flaky test gets a fix of its cause or a delete with a reason.
29. As an agent, I want the flaky-test rule in `AGENTS.md`, so that I know the rule before I hit a flaky test.
30. As an agent, I want the first commit of a facts diff to pass when `main` cannot rebuild yet, so that the change that adds the rebuild can merge.

## Implementation Decisions

**The scope.** Verification follows the diff, not the flow (decision 01). Each PR with a change outside the records gets each check of this spec. The records are `.scratch/`, `docs/`, and Markdown files at the root. A PR of records only gets the plain `Check`. The weekly `publish` has no PR, so it is out.

**The `verify` skill** (decisions 01, 02, 04).

- One skill lives in the repo skill folder of Claude Code, with one section per app. A tracked symlink in the repo skill folder of Codex points to it, the same way the `4ag` skills are linked now.
- The skill boots the local API in its evidence mode and the export of each client, through the evidence runner. Then it runs the picked flows.
- The flow list is one JSON file in the skill. Each flow has a name, the globs of the code it covers, a route, its steps in the step-list shape of the evidence runner, its expected results, a flag for a Claude call, and a flag for a layout flow.
- The globs of the diff since the merge base pick the flows. A diff that matches no glob picks no flow. A diff of the pipeline only picks no flow, because the rebuild covers it.
- The agent may add steps to a picked flow for its change. It cannot drop a picked flow.

**The first flow list** (decision 08). Each flow has its route, its expected result, and the globs of its code:

| Flow | Route | Expected result | Claude | Layout |
| --- | --- | --- | --- | --- |
| Front door | `/` | The site name in the h1, and the topic chips | yes, one question | yes |
| Passphrase | `/`, then open the sheet | The field "League passphrase" has focus above the keyboard | no | no |
| Week report | the latest week | The title "Week N" and the chapter rail | no | yes |
| Manager page | the managers index, then one manager | The team name and the Season So Far dial | no | yes |
| Analyzer | `/analyze/`, then "Grade the Trade" | The status "Grading the trade", then a Lean word and a Case | yes, one grade | yes |
| Power rankings | `/rankings/` | The title "Power Rankings" and the Ladder | no | no |
| Midseason report | the midseason route of the season | The title of the report | no | no |

A change to a shared part, such as the design package or the shell, picks each flow.

**The evidence runner** (decision 04). The step list gets one more verb, `expect`. It asserts that a text or an element is visible, and it fails the run if not. The runner also fails on a page error, a console error, an API response of 4xx or 5xx, and an overlap of two elements. A smoke run uses 390x660 iPhone WebKit and 1280x800 desktop, in the light theme. A layout flow adds 810x980 and 1080x740. The acceptance-test defaults of the runner stay as they are.

**The smoke run in the flows** (decision 04).

- `4ag:implement` runs one smoke run after the last ticket, before the Judge. A green run writes its shots and its log into the smoke folder of the evidence, and the Judge may open them for any test.
- `4ag:quick` runs one smoke run after the last item, before the quick Judge. The quick file names the shots and the log in a `Smoke:` block.
- A red smoke run counts as a red check: one fix round, then a stop.
- The quick Judge gets a third question for each item that touches the site or the API: "Does the smoke run show the changed flow at work?"

**The re-run job** (decision 07).

- A CI workflow on each PR to `main` reads its script from `main`, the way `verdict.yml` does.
- The script finds the quick file that the PR adds, under the Bugs folder or the Quick wins folder. A PR with no quick file passes, with a note.
- For each item that is not text only, it reads the commit and the command of the Red line and of the Green line. It also reads the form "at the parent, with the loop file of the fix commit".
- It sets up each member that the command needs, with the same steps as the member jobs of `Check`, plus the client build for a site loop.
- It runs the Red command at the red commit and expects a failure. It runs the Green command at the fix commit and expects a pass. It checks that the failure line quoted in the Red block shows in its own output.
- One item that does not hold fails the job, and the job names the item.

**The pinned build inputs** (decisions 03, 10, 11).

- Each build saves the nflverse extract of the week into the raw folder of the week, also a degraded extract. A later build of the same week before the publish may replace it. The publish commits the last one.
- Each build saves the values of the slow sources into the week folder, as one small file. It never commits the shared cache of about 24 MB.
- Each build saves the Sleeper news of the week into the raw folder.
- A facts-only rebuild reads the build clock from the saved `verify.json`, the three saved inputs, and the research claims of the saved facts. It makes no Claude call, no TypeSafe call, and no network call.

**The base and head rebuild** (decisions 03, 05, 09, 10).

- A CI job runs on each PR that changes the pipeline, the API, or a package. It reads its script from `main`.
- It picks the latest published week of each client whose folder holds every saved input.
- It runs the facts-only rebuild and `page-json` two times, once with the code of `main` and once with the code of the PR, then diffs the facts, `page.json`, `topics.json`, and `waiver.json`.
- The oracle is the code of `main`, not `published/`. Otherwise each merged change of output fails each later PR until the next publish.
- If `main` cannot run the facts-only rebuild yet, or no week holds every saved input yet, the job runs only the render diff and says so. The first week that holds every input is the first week built after this spec.

**The list of approved diffs** (decision 05).

- A PR that changes the output on purpose lists each changed value: the client, the file, the JSON path, and one sentence of reason.
- A spec puts the list in its folder as `REBUILD.md`. A quick run puts it in its quick file as a `Rebuild:` block.
- The job passes only if the set of changed paths equals the listed set. An unlisted path fails, and so does a listed path that does not change.
- The Judge gets the list and the diff as evidence.

**Property tests** (decision 06). Hypothesis goes into the Python dev dependencies. Each test lives beside the package of its function:

1. The manager grade score stays in 0 to 100 when each part is in 0 to 1, and the grade weights sum to 100.
2. The grade letter never gets worse as the score goes up, and it is only A, B, C, or D.
3. The depth word is "thin" for each roster with a hole.
4. The scale against the league stays in 0 to 1, the lowest total gets 0 and the highest gets 1, and the same shift of all totals changes nothing.
5. The ranks of the rosters run 1 to N, with no tie and no gap.
6. The ranks at each position run 1 to n with no tie, and the order of the input does not change them.
7. The star ranks are never negative, and a position with no slot is absent.
8. A handcuff in a trade always has a trade value of 0.

**grade-bar in CI** (decision 01). The full site check runs the grade-bar project in its norcal pass, where the export already holds the client with the Finder on. The test needs no live API, because it answers each API call itself.

**The flaky-test rule** (decision 01). `AGENTS.md` says: a flaky test gets a fix of its cause, or a delete with the reason written in the commit. A second run is never the fix. A rule test of the root scripts fails on a `retries` value above 0 in a Playwright config, on `pytest-rerunfailures` in a lock file or a config, and on a `retry` in a Vitest config.

**An ADR.** The rule that each PR that changes code carries a smoke run, a re-run of its loop, and a base and head rebuild is hard to reverse, and a reader may find it surprising. The first ticket writes it as ADR 0037.

## Testing Decisions

A good test checks behavior that a reader can see from the outside: the exit code of a job, the output files of a run, and the text of a page. It does not check the inside of a function. It uses real data or the one fake of a port (ADR 0015), and never a mock.

The seams, from the highest down:

1. **The evidence runner.** It is an existing seam. A test feeds it a step list with an `expect` that holds and one that does not. It checks the exit code and the log. Prior art: the evidence-rules spec of the site.
2. **The re-run script.** It is a new seam with one entry point: a quick file and a git repo in, a pass or a named failure out. A test of the root scripts builds a small real git repo in a temp folder, with a red commit and a fix commit, and runs the script on it. Prior art: the tests of the verdict script.
3. **The rebuild command.** It is a new command of the pipeline CLI, with saved week inputs in and a diff out. A pipeline test runs it on a saved week, then on the same week with one seeded change of code, and checks the diff. Prior art: the golden tests of the pipeline.
4. **The pinned inputs.** A pipeline test builds the facts of a saved week two times and compares them byte for byte. Prior art: the research of ticket 10.
5. **The property tests.** Each one is its own test, with Hypothesis.
6. **The flaky-test rule.** A rule test of the root scripts reads the config files. Prior art: the rule tests named `test_rule_<topic>.py`.
7. **The skill text.** A change to `4ag:implement` and `4ag:quick` is text. A rule test checks that the quick file format and the Judge brief name the `Smoke:` block, the `Rebuild:` block, and the third question.

The acceptance tests prove each check with a direct run now. They never wait for the build of week 11.

## Out of Scope

- Spec 2, "the record": the Proof trailer and its gate with off, observe, and enforce modes, the reliability checklist with triggers read from the diff, and the score of the Judge from a replay of past FAIL items. It gets its own map after this spec merges.
- A measure of the rate of fix PRs after a merge. Brian chose no measure.
- The weekly `publish`. It has no PR.
- A fix of the flaky AT-5 wait-dips test. It goes to its own quick run.
- A full rebuild with Claude. It never gives the same output twice.
- A flow of the egg board. The board writes to a live store, so a smoke run would leave claims on it.

## Further Notes

- The rebuild diffs the code of `main` against the code of the PR, not the PR against `published/`. This refines decision 09, which named `published/`. The reason: after a merge, `published/` keeps the old output until the next publish, so a diff against it fails each later PR.
- The site job of `Check` has a limit of 25 min. grade-bar adds one project to the norcal pass. If the job gets near the limit, the ticket names the time.
- `GLOSSARY.md` has the terms Smoke run, Flaky test, and Flow list on this branch.
