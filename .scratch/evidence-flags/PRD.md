# Evidence flags: Jev reads each acceptance test and its evidence before the Judge

Status: ready-for-agent
Date: 2026-11-10
Apps: pipeline. The pipeline CLI gets the commands `evidence-flags` and `evidence-flags-eval`, and the `Jev` port gets an image type. The workflow skills of `cpc:implement` run the command in the evidence stage. The site does not change.
Spec branch: `evidence-flags`.
Source: the map `.scratch/evidence-flags/MAP.md` and decision tickets 01 to 06, from the sessions of 2026-11-10. ADR 0026 (the Judge), ADR 0029 (Jev is the second vendor).
Tickets: none yet. `cpc:to-tickets` writes them.

## Problem Statement

The evidence stage of `cpc:implement` records each acceptance test, and then a fresh Judge gives each Test verdict. When the evidence has a gap, the Judge gives FAIL or BLOCKED. Then the flow loops: a fix, a new evidence pass, and a new Judge pass. By then the evidence agent has stopped, its server is down, and its context is gone. Each loop costs about 25 to 45 min.

In easter-eggs, four Judge rounds had a FAIL or BLOCKED. AT-50 caused a hard stop and a wait overnight. AT-32 and AT-34 failed because still shots cannot show motion. Of the 12 FAIL and BLOCKED results in past rounds, 7 were evidence gaps, not product defects. The agent could have closed most of them while its server still ran, if something had told it.

Brian wants Jev in the dev workflow to make the flow faster from end to end, with no check that gets weaker.

## Solution

After the evidence agent records an acceptance test, it runs `cornerstone evidence-flags <slug> AT-<n>`. Jev reads the test, its entry in `EVIDENCE.md`, and its files, and answers typed questions. Each yes past the cut of its question is an Evidence flag, with a reason. The agent acts on each flag at once: it records the test again, hands a product defect to a fix group, or writes why it disagrees. Then it goes on.

The flags go into `FLAGS.md`, which the Judge never reads. The Judge stays fresh, strict, and all Claude, and it still gives every Test verdict. A Jev miss costs what it costs now, because the Judge still catches the gap. A false flag costs about 1 to 3 min and can never cause a FAIL.

A second command, `cornerstone evidence-flags-eval`, runs the final questions on labeled past rounds. A question enters the flow only if it meets the bar on that run. If no question meets the bar, the flow stays as it is now.

The expected gain is fewer Judge loops and fewer hard stops on a spec that goes badly, about 30 to 90 min on a spec like easter-eggs. A spec that passes in the first round gains nothing. The replays found that Jev misses AT-50, so the worst past stop is not covered.

## User Stories

1. As the evidence agent, I want one command per acceptance test that gives me each Evidence flag and its reason, so that I find a gap while my server still runs.
2. As the evidence agent, I want to run the command on many tests at once, so that one call covers the whole round of site tests after the runner.
3. As the evidence agent, I want the command on a pipeline test right after I save its output, so that I can run the command of the When line again at once.
4. As the evidence agent, I want a flag when the evidence holds no file that shows a fact the Then line names, so that I add the missing file before the Judge sees it.
5. As the evidence agent, I want a flag when the test asks for motion and the evidence holds only still shots, so that I record a video or timed frames.
6. As the evidence agent, I want a flag when a sentence of my Observation claims more than the files show, so that I fix the Observation or add the file.
7. As the evidence agent, I want a flag when a screenshot shows the text that the Then line names cut off or overflowed, so that the defect goes to a fix group before the Judge runs.
8. As the evidence agent, I want each flag to name the test, the question, the probability, and the reason, so that I can judge the flag in about 1 min.
9. As the evidence agent, I want a clear rule for each kind of flag, so that I never stop to ask Brian about a flag.
10. As the evidence agent, I want a limit of one loop per test, so that a false flag that stays cannot trap me.
11. As the evidence agent, I want to write one line of disagreement for a false flag and go on, so that the evidence stays honest and the round keeps its pace.
12. As the orchestrator, I want each product-defect flag as a fix group before the Judge runs, so that a defect costs one fix and not a Judge loop.
13. As the orchestrator, I want the loop limit of a test to start again after its fix merges, so that a real defect gets a new look.
14. As the Judge, I want no flag and no disagreement line in any file I read, so that I judge each test fresh from its evidence alone.
15. As the Judge, I want my brief and my read paths to stay the same, so that no check gets weaker.
16. As Brian, I want `FLAGS.md` committed with the evidence, so that I can read every flag and action on the PR.
17. As Brian, I want one line of counts in the PR body, such as "9 flags: 5 new recordings, 1 fix group, 3 disagreements", so that I see the effect of Jev at a glance.
18. As Brian, I want the evidence stage to go on with no flags when Jev is down or the key is missing, so that a vendor outage never blocks a spec.
19. As Brian, I want each run to log one line with the count of tests, flags, errors, and input tokens, so that I see the cost and the failures.
20. As Brian, I want an eval command that runs the final questions on labeled past rounds, so that the Judge sees the real rates of the final questions, not the rates of tuned drafts.
21. As Brian, I want a question to enter the flow only if it catches at least half of the past gaps of its kind and flags 10% or fewer of the PASS tests, so that the flags are worth the time.
22. As Brian, I want a question that misses the bar to stay out of the flow, so that a weak question costs nothing.
23. As Brian, I want the flow to stay as it is now if no question meets the bar, so that the spec can fail safely.
24. As Brian, I want each new spec to add its flags and Test verdicts as labels, so that the bar gets more honest with each spec.
25. As Brian, I want a cut to change only through a later ticket, so that the rules do not move in the middle of a spec.
26. As Brian, I want a record of the data that now goes to TypeSafe, so that a reader knows what leaves the repo and why.
27. As a developer, I want the questions, the criteria, the cuts, and the bar in one module, so that a later ticket tunes them in one place.
28. As a developer, I want the `Jev` port to carry an image with no SDK import, so that the caller code stays apart from the vendor.
29. As a developer, I want each tall screenshot cut into parts that the API takes, so that a request never fails on size.
30. As a developer, I want `FakeJev` to take the image type, so that the tests run with no call to TypeSafe.

## Implementation Decisions

### The commands

- `cornerstone evidence-flags <slug> [AT-<n> ...]` reads `.scratch/<slug>/ACCEPTANCE.md`, `EVIDENCE.md`, and `evidence/AT-<n>/` of the Spec worktree. With no test ids, it reads every test that has an entry in `EVIDENCE.md`. It makes one Jev request per test, with every question of the flow in that request.
- For each yes past the cut of its question, the command adds an entry to `.scratch/<slug>/FLAGS.md`, with `Action: open`. It prints the same entries. The agent then sets the action of each entry.
- A test with `Files: none`, a skipped test, and a `Retired` test get no request.
- `--root <path>` sets the folder that holds `.scratch/`. The default is the current worktree. A test of a past round copies its feature folder into a temp root.
- The command prints the question keys that it asked for each test.
- `cornerstone evidence-flags-eval` reads a label file, runs the questions of the module on each labeled test at its commit, and prints, per question, the hits, the misses, and the false flags at its cut, and `meets the bar: yes` or `meets the bar: no`. It reads the past files through `git show <commit>:<path>`, so it needs no checkout of an old commit.
- Both commands take the Jev by injection, in the shape of `advisor_eval` and its `MeteredJev`, so a test passes a `FakeJev`.

### The questions module

One module holds each question, its criteria, its cut, its "in the flow" mark, and the bar. Judgments go to Jev. Decisions go to code (ADR 0030). The drafts are in the notes of tickets 02 and 06. The build starts from them.

- (a) The facts: the evidence holds a file that shows each fact that the Then line names. Cut 0.7.
- (b) Motion: code first finds a video or timed frames among the files. Jev only answers whether the test asks for motion, and whether a text log holds animation values. Cut 0.7.
- (c) Cut-off text: a screenshot shows the text that the Then line names cut off or overflowed. The build gives it one more draft, scoped to that text. Cut 0.9. As drafted it misses the bar, at 14% false flags.
- (d) The Observation: one Noul per sentence of the Observation asks if the files show it. A second Noul asks if the sentence reports a result that the Then line asks for. Cut 0.7.
- The bar is at least half of the past gaps of its kind, and 10% or fewer of the PASS tests flagged, on the eval run in the build. The mark "in the flow" of each question follows that run. `evidence-flags` asks only the questions in the flow.

### The state that Jev reads

- The text of the test from `ACCEPTANCE.md`, its entry in `EVIDENCE.md`, the list of its files, and each text file in full: `steps.json`, `steps.txt`, `output.txt`, `fields.diff`.
- Every screenshot of the test, as images. Ticket 06 found that most false flags came from a cut state: a cap of 4 shots, or a file cut at 3000 characters. So the state sends all of it, up to the request limit of 32 MiB.
- If a test is over the limit, the command sends the text and the shots that fit, in the order of `Files:`, and the log line says the state was cut.

### The image type and the cut of a shot

- The `Jev` port gets its own image type, PNG bytes, that a state can hold. A caller never imports the SDK. `TypeSafeJev` wraps each image in `typesafe_sdk.Image` before it calls `system_one`. `FakeJev` accepts it and keeps it in its requests.
- The API takes PNG and JPEG, 280 to 1568 px per side, 16 MiB per image, and never resizes. The installed `typesafe-sdk` 0.7.5 has `Image`, so no upgrade is needed.
- The command scales each shot to a width of 280 to 1568 px, then cuts tiles of 1568 px or less from the top. It uses Pillow, which the pipeline already depends on. A tile edge can cut a line of text, which (c) may flag.
- One image costs about one input token per 380 px. The replays cost about $0.05 for 200 requests.

### The failure and the log

- A `JevError`, or a missing `TYPESAFE_API_KEY`, gives no flags for that test. The command exits 0, and the evidence goes on. A failed call never counts as "no flag" in the eval (ADR 0029).
- Each run logs one line: `Evidence flags: <tests> tests, <flags> flags, <errors> errors, <tokens> input tokens`. It follows the shape of the weekly build line `Jev: ... checks, ... errors, ... input tokens`. A cut state adds `, <n> cut`.

### FLAGS.md

- The path is `.scratch/<slug>/FLAGS.md`, outside the read paths of the Judge. `judge.md` does not change.
- Each entry gives the test, the question, the probability, the reason, and the action. The action is one of `recorded again`, `fix group`, `disagree: <one line>`, or `open`. No entry stays `open` at the evidence commit.
- It is committed with `EVIDENCE.md` in the evidence commit of stage 3.

### The workflow skills

- `evidence.md`: after the runner round, run `evidence-flags` on every site test. Run it on each pipeline test after its output is saved. Then act on each flag by its kind:
  - An evidence gap: change `steps.json` or the command, then record that test again.
  - A product defect: hand it to the orchestrator as a fix group, then record the test again after the fix merges.
  - A false flag: write the disagreement line, then go on.
- The agent never stops to ask Brian about a flag. The limit is one loop per test. After one new recording, the command runs once more. A flag that stays gets a disagreement line. A product defect is outside the limit, and the limit starts again after its fix merges.
- `pr.md`: the PR body gives one line of counts from `FLAGS.md`.
- `judge.md`: no change. The Judge never reads `FLAGS.md`.

### The labels

- A label file lists each past test with its spec, its round commit, and its label: `gap` with its kind, `defect`, or `pass`. The first set is the 12 FAIL and BLOCKED results and the 44 PASS tests of tickets 02 and 06. It names no league manager, so it stays in the repo, beside the module.
- After each later spec, a ticket adds its tests from `FLAGS.md` and `VERDICTS.md`. A cut changes only through a later ticket.

### The record

- A new ADR records that the evidence of the acceptance tests, with its screenshots, now goes to TypeSafe. The screenshots show the names of managers on the site. It also records that an Evidence flag is never a Test verdict and never reaches the Judge. It extends ADR 0029, which covers blurbs and fact sheets only.
- `GLOSSARY.md` has the term Evidence flag, from stage 1.

## Testing Decisions

A good test runs a command as a user does and checks what it prints and writes. It never checks the inner calls. No test calls TypeSafe. The adapter runs against the live API by hand, for the evidence (ADR 0029).

The seams, from the highest:

1. **The CLI.** The main test seam. A test writes a real `.scratch/<slug>/` of `ACCEPTANCE.md`, `EVIDENCE.md`, and `evidence/AT-<n>/` files with real PNG shots into a temp folder. It runs `evidence-flags` through the CLI entry with a `FakeJev`. It checks the printed flags, the `FLAGS.md` entries, the log line, the skip of a `Files: none` test, and the behavior on a `JevError`. The `answer` callback of `FakeJev` says yes to the questions that a case needs.
2. **The eval.** The same CLI seam. A test makes a temp git repo with two commits of a small feature folder and a label file. It runs `evidence-flags-eval` with a `FakeJev` and checks the hits, misses, false flags, and the bar result.
3. **The `Jev` port.** One test of `FakeJev` with a state that holds an image. One test of the cut of a tall PNG: each tile has each side in 280 to 1568 px.

Prior art: `tests/test_cli.py` for a CLI run, `tests/test_advisor_eval.py` for an eval with an injected Jev, `tests/test_jev_check.py` for questions and `FakeJev`, and `scripts/test_changed_apps.py` for a real temp workspace.

The proof of the bar is a live run of `evidence-flags-eval` on the label file, recorded as evidence of an acceptance test.

## Out of Scope

- Jev triage of the review findings, and the model tier of each fix group. It gets its own spec, after this one shows the bar works in the flow.
- Jev routes each ticket to a model tier and predicts merge conflicts. It gets its own spec, for the same reason.
- Any Jev use by the Judge. The Judge stays fresh and all Claude.
- A change of a cut in the middle of a spec. Only a later ticket changes a cut.
- A question that catches AT-50 or AT-47 of the past rounds. No draft caught them. A later ticket may try again on new labels.

## Further Notes

- The drafts of (b) and (d) were tuned on the same cases that scored them, so their replay rates are optimistic. The eval run in the build is the honest number.
- The pipeline package is `cpc-league`, not `league`. `uv run --exact` strips other members from the shared `.venv`, so a run of the eval beside the background check must use a detached worktree (`evidence.md`, "One `uv run` for each checkout").
- The replay scripts of tickets 02 and 06 are in the session scratchpad, not the repo. Their code is in the notes of each ticket.
