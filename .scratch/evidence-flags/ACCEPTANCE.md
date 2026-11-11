# Evidence flags: acceptance tests

Spec: `.scratch/evidence-flags/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

A past round: several tests read the real evidence of one past Judge round. In the worktree of the Spec branch, make a temp root and copy the feature folder at the commit of that round into it: `T=$(mktemp -d) && git archive <commit> .scratch/<feature> | tar -x -C "$T"`. Then run the command with `--root "$T"`. Source `~/.secrets` first, so `TYPESAFE_API_KEY` is set. The run makes real Jev calls. Commit nothing under the temp root.

## Tests

AT-1: Motion with only still shots gets a flag
App: pipeline
Stories: 1, 5, 8
Given: the past round of easter-eggs at `566d11e7`, where the Judge failed AT-32 because the files show only a still egg card and a still tile
When: `uv run --exact --package cornerstone cornerstone evidence-flags easter-eggs AT-32 --root "$T"` runs.
Then: `"$T"/.scratch/easter-eggs/FLAGS.md` has an entry for AT-32 and question (b), with a probability of 0.7 or more, a reason, and `Action: open`.
Evidence: the command and its full output, and the `FLAGS.md` that it wrote.

AT-2: An Observation that misstates a file gets a flag
App: pipeline
Stories: 1, 6
Given: the past round of easter-eggs at `9582a573`, where the Observation of AT-54 says the grade took 17 s and `site-N.txt` shows 8 s
When: `uv run --exact --package cornerstone cornerstone evidence-flags easter-eggs AT-54 --root "$T"` runs.
Then: `FLAGS.md` has an entry for AT-54 and question (d), with a probability of 0.7 or more and a reason.
Evidence: the command and its full output, and the `FLAGS.md` that it wrote.

AT-3: A fact that no file shows gets a flag
App: pipeline
Stories: 1, 3, 4
Given: the past round of easter-eggs at `8d646bd0`, where `output.txt` of AT-3 shows only a pytest line "1 passed" and no time inside 23:00 to 00:00 ET
When: `uv run --exact --package cornerstone cornerstone evidence-flags easter-eggs AT-3 --root "$T"` runs.
Then: `FLAGS.md` has an entry for AT-3 and question (a), with a probability of 0.7 or more and a reason.
Evidence: the command and its full output, and the `FLAGS.md` that it wrote.

AT-4: Only the questions in the flow are asked
App: pipeline
Stories: 7, 22, 27
Given: the past round of easter-eggs at `8d646bd0`, where the banner text of AT-41 is cut at 375 px
When: `uv run --exact --package cornerstone cornerstone evidence-flags easter-eggs AT-41 --root "$T"` runs.
Then: the question keys that the command prints as asked equal the keys that the questions module marks as in the flow.
Evidence: the command and its full output, and the lines of the module with the mark of each question.

AT-5: A whole round gives one log line
App: pipeline
Stories: 2, 19
Given: the past round of hero-slots at `f9304b5e`, with every test at PASS
When: `uv run --exact --package cornerstone cornerstone evidence-flags hero-slots --root "$T"` runs, with no test id.
Then: the command exits 0 and logs one line `Evidence flags: <tests> tests, <flags> flags, <errors> errors, <tokens> input tokens`. The test count equals the count of entries in `EVIDENCE.md` that do not say `Files: none`. The flag count equals the count of entries in `FLAGS.md`.
Evidence: the command, its exit code, its full output, the `FLAGS.md` that it wrote, and a script output with the two counts.

AT-6: A missing key leaves the evidence stage whole
App: pipeline
Stories: 18
Given: the past round of easter-eggs at `566d11e7`, with `TYPESAFE_API_KEY` unset
When: `env -u TYPESAFE_API_KEY uv run --exact --package cornerstone cornerstone evidence-flags easter-eggs AT-32 AT-34 --root "$T"` runs.
Then: the command exits 0, writes no entry to `FLAGS.md`, and logs `Evidence flags: 2 tests, 0 flags, 2 errors, 0 input tokens`.
Evidence: the command, its exit code, its full output, and the state of `FLAGS.md` after the run.

AT-7: The eval gives the rates of the final questions
App: pipeline
Stories: 20, 21, 22, 23
Given: the label file of the spec and the worktree of the Spec branch, with `TYPESAFE_API_KEY` set
When: `uv run --exact --package cornerstone cornerstone evidence-flags-eval` runs.
Then: for each of the four questions (a), (b), (c), and (d), it prints the hits, the misses, and the false flags at its cut, and `meets the bar: yes` or `meets the bar: no`. The in-flow mark of each question in the module equals its bar result.
Evidence: the command and its full output, and the lines of the module with the mark of each question.

AT-8: The label file holds the past labels and no manager
App: pipeline
Stories: 20, 26
Given: the label file of the spec, and `clients/cpc/build/2026/managers.json`
When: a script counts the labels of the file and searches it for each manager name of `managers.json`.
Then: the file has 56 tests: 7 `gap`, 5 `defect`, and 44 `pass`. No manager name is in it.
Evidence: the script and its output.

AT-9: A Jev error is never a "no flag" in the eval
App: pipeline
Stories: 18, 20
Given: a temp git repo with a small feature folder at two commits and a label file, and a `FakeJev` that raises `JevError`
When: the test runs `evidence-flags-eval` through the CLI entry.
Then: the eval counts each test as an error. It counts no test as a hit, a miss, a false flag, or a pass.
Evidence: the test name and the output of its pytest run.

AT-10: Every shot goes to Jev as tiles that fit
App: pipeline
Stories: 28, 29, 30
Given: a temp `.scratch/<slug>/` with the real PNG shots of easter-eggs AT-32 at `566d11e7`, and a `FakeJev`
When: the test runs `evidence-flags` through the CLI entry.
Then: the request of `FakeJev` holds a tile of every shot that `Files:` lists, and each tile is 280 to 1568 px on each side.
Evidence: the test name, the output of its pytest run, and a list of each shot with its tile count and sizes.

AT-11: A state over 32 MiB is cut and logged
App: pipeline
Stories: 19, 29
Given: a temp `.scratch/<slug>/` with one test whose shots add up to more than 32 MiB, and a `FakeJev`
When: the test runs `evidence-flags` through the CLI entry.
Then: the request holds the text and the shots that fit, in the order of `Files:`, and the log line ends with `, 1 cut`.
Evidence: the test name and the output of its pytest run.

AT-12: A test with no files gets no request
App: pipeline
Stories: 1
Given: a temp `.scratch/<slug>/` with one test at `Files: none` and one test with files, and a `FakeJev`
When: the test runs `evidence-flags` through the CLI entry.
Then: `FakeJev` records one request, for the test with files, and none for the test at `Files: none`.
Evidence: the test name and the output of its pytest run.

AT-13: Only the adapter imports the SDK
App: pipeline
Stories: 28
Given: the worktree of the Spec branch
When: `rg -l 'typesafe_sdk' apps packages` runs.
Then: the only file outside tests is `packages/league/python/src/league/jev.py`.
Evidence: the command and its full output.

AT-14: The questions, the cuts, the marks, and the bar sit in one module
App: pipeline
Stories: 27
Given: the worktree of the Spec branch
When: a search runs for the text of each question, for each cut, and for the bar values.
Then: each one is in one module only, outside tests.
Evidence: the search commands and their full output.

AT-15: The evidence stage runs the command at the right time
App: pipeline
Stories: 1, 2, 3, 16
Given: `.claude/plugin/skills/implement/evidence.md` on the Spec branch
When: a reader reads its diff against `main`.
Then: it runs `evidence-flags` on every site test after the runner round, and on each pipeline test after its output is saved. It commits `FLAGS.md` with `EVIDENCE.md` in the evidence commit.
Evidence: the output of `git diff main -- .claude/plugin/skills/implement/evidence.md`.

AT-16: The evidence stage gives one action for each kind of flag
App: pipeline
Stories: 9, 11, 12
Given: `.claude/plugin/skills/implement/evidence.md` on the Spec branch
When: a reader reads its diff against `main`.
Then: an evidence gap gets a new recording, a product defect goes to the orchestrator as a fix group, and a false flag gets one disagreement line. No entry stays `open` at the evidence commit.
Evidence: the output of `git diff main -- .claude/plugin/skills/implement/evidence.md`.

AT-17: The evidence stage has no stop on a flag and one loop per test
App: pipeline
Stories: 9, 10, 13
Given: `.claude/plugin/skills/implement/evidence.md` on the Spec branch
When: a reader reads its diff against `main`.
Then: it says never to ask Brian about a flag. It gives one loop per test, and a flag that stays gets a disagreement line. A product defect is outside the limit, and the limit starts again after its fix merges.
Evidence: the output of `git diff main -- .claude/plugin/skills/implement/evidence.md`.

AT-18: The PR body counts the flags
App: pipeline
Stories: 17
Given: `.claude/plugin/skills/implement/pr.md` on the Spec branch
When: a reader reads its diff against `main`.
Then: the PR body gets one line of counts from `FLAGS.md`, in the shape "9 flags: 5 new recordings, 1 fix group, 3 disagreements".
Evidence: the output of `git diff main -- .claude/plugin/skills/implement/pr.md`.

AT-19: The Judge does not change
App: pipeline
Stories: 14, 15
Given: the Spec branch
When: `git diff main -- .claude/plugin/skills/implement/judge.md` runs.
Then: the output is empty.
Evidence: the command and its full output.

AT-20: The ADR records the new data that goes to TypeSafe
App: pipeline
Stories: 26
Given: `docs/adr/` on the Spec branch
When: a reader reads the new ADR.
Then: it says that the evidence of the acceptance tests and its screenshots go to TypeSafe, and that the shots show the names of managers. It says that an Evidence flag is never a Test verdict and never reaches the Judge.
Evidence: the path and the full text of the new ADR.

AT-21: Out of scope: no Jev in the review, the routing, or the Judge
App: pipeline
Stories: none
Given: `.claude/plugin/skills/` on the Spec branch
When: `rg -il 'jev|evidence-flags' .claude/plugin/skills` runs.
Then: the only files are `implement/evidence.md` and `implement/pr.md`.
Evidence: the command and its full output.

AT-22: The checks pass with no TypeSafe call
App: pipeline
Stories: 30
Given: the Spec branch, with `TYPESAFE_API_KEY` unset
When: `env -u TYPESAFE_API_KEY make -C apps/pipeline check` runs.
Then: the check passes.
Evidence: the command, its exit code, and the last lines of its output.

## Trace

Story 1: AT-1, AT-2, AT-3, AT-12, AT-15
Story 2: AT-5, AT-15
Story 3: AT-3, AT-15
Story 4: AT-3
Story 5: AT-1
Story 6: AT-2
Story 7: AT-4, AT-7. The (c) flag on cut text gets no test of its own, because (c) may miss the bar and leave the flow.
Story 8: AT-1
Story 9: AT-16, AT-17
Story 10: AT-17
Story 11: AT-16
Story 12: AT-16
Story 13: AT-17
Story 14: AT-19
Story 15: AT-19
Story 16: AT-15
Story 17: AT-18
Story 18: AT-6, AT-9
Story 19: AT-5, AT-11
Story 20: AT-7, AT-8, AT-9
Story 21: AT-7
Story 22: AT-4, AT-7
Story 23: AT-7
Story 24: no test. Reason: it is a rule for later tickets, and this spec has no new spec to add labels from.
Story 25: no test. Reason: it is a rule for later tickets, with no behavior to check in this spec.
Story 26: AT-8, AT-20
Story 27: AT-4, AT-14
Story 28: AT-10, AT-13
Story 29: AT-10, AT-11
Story 30: AT-10, AT-22
Out of scope "Jev triage of the review findings": AT-21
Out of scope "Jev routes each ticket to a model tier": AT-21
Out of scope "Any Jev use by the Judge": AT-19, AT-21

## Revisions

None yet.
