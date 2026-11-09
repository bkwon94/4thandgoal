# Jev: acceptance tests

Spec: `.scratch/jev/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

The week 8 rebuild: several tests read one real run. In the worktree of the Spec branch, with `~/.secrets` sourced, run `uv run --exact --package cornerstone cornerstone build --client cpc --season 2026 --week 8 --no-fetch`. It reads the saved raw data of 2026 week 8 and makes the real Claude calls and the real Jev calls. Save its log. Do not commit the files it changes under `clients/cpc/`, and do not publish.

## Tests

AT-1: Each checked attempt saves its sentences and its Jev answers
App: pipeline
Stories: 4, 7, 10, 11, 15
Given: the CPC client, 2026 week 8, with `TYPESAFE_API_KEY` from `~/.secrets`
When: the week 8 rebuild runs.
Then: in `clients/cpc/data/2026/week-08/verify.json`, every attempt with no code failure has `sentences` with the text of each sentence, and `jev` with one Jev answer per sentence index. Each answer is between 0 and 1, and the model id starts with `jev-`.
Evidence: the rebuild log, and a script output that lists, for each prose block and attempt, the count of sentences, the count of Jev answers, the lowest and the highest answer, and the model id.

AT-2: The Jev check never skips the Claude check
App: pipeline
Stories: 5, 13
Given: the `verify.json` of the week 8 rebuild of AT-1
When: a reader compares the Claude verdicts and `passed` of each attempt with its Jev answers.
Then: every attempt with no code failure has one Claude verdict per sentence. `passed` equals "every Claude verdict is supported", for every attempt, whatever the Jev answers are.
Evidence: a script output that lists, for each attempt, the count of sentences, the count of Claude verdicts, `passed`, the result of the rule, and the lowest Jev answer.

AT-3: A missing key leaves the build whole
App: pipeline
Stories: 12, 13, 14
Given: the CPC client, 2026 week 8, with `TYPESAFE_API_KEY` unset in the shell
When: the week 8 rebuild runs with `env -u TYPESAFE_API_KEY`.
Then: the build exits 0 and writes `clients/cpc/build/2026/week-08/page.json`. In `verify.json`, every attempt with no code failure has a `jev` with an error text and no answers. The log shows one warning per checked attempt that names the Jev error.
Evidence: the command, its exit code, its log, and a script output of the `jev` field of each attempt.

AT-4: A code-failed attempt has no Jev check
App: pipeline
Stories: 6
Given: the week 6 fixtures of the pipeline tests, with `FakeWriter` writing a first attempt that fails the code check, and `FakeJev`
When: the test drives `run_build`.
Then: the attempt with the code failure has `jev` None in `verify.json`, and `FakeJev` recorded no request for it. The second attempt, which passes the code check, has a `jev`.
Evidence: the name of the test, its source, and the pytest output.

AT-5: One request per blurb, with one question per sentence
App: pipeline
Stories: 7
Given: the week 6 fixtures of the pipeline tests, with `FakeWriter` and `FakeJev`
When: the test drives `run_build`.
Then: `FakeJev` recorded exactly one request for each attempt that passed the code check. Each request has one question key per sentence of that attempt, and no other key.
Evidence: the name of the test, its source, and the pytest output.

AT-6: The state holds all chapter facts and the vocabulary
App: pipeline
Stories: 8
Given: the week 6 fixtures of the pipeline tests, with `FakeWriter` and `FakeJev`
When: the test drives `run_build`.
Then: the state of each recorded request holds every fact id of its chapter and the vocabulary text of the client.
Evidence: the name of the test, its source, and the pytest output.

AT-7: The build log shows the Jev line
App: pipeline
Stories: 17
Given: the log of the week 8 rebuild of AT-1
When: a reader searches the log for the Jev line.
Then: the log has one Jev line for the build. It gives the count of Jev checks, the count of errors, and the token use. The count of checks equals the count of attempts with a `jev` in `verify.json`.
Evidence: the Jev line from the log, and the count from `verify.json`.

AT-8: An old verify.json still loads
App: pipeline
Stories: 16
Given: the `clients/cpc/data/2026/week-08/verify.json` of `main`, which has no `sentences` and no `jev`, in the worktree of the Spec branch
When: `uv run --exact --package cornerstone cornerstone page-json --client cpc --season 2026 --week 8` runs.
Then: the command exits 0, and `clients/cpc/build/2026/week-08/page.json` is the same as on `main`.
Evidence: the command, its exit code, and the output of `git diff --stat main -- clients/cpc/build/2026/week-08/page.json`.

AT-9: No test calls TypeSafe
App: pipeline
Stories: 3
Given: the Spec branch, with `TYPESAFE_API_KEY` unset in the shell
When: `env -u TYPESAFE_API_KEY make -C apps/pipeline check` runs.
Then: every check passes. `FakeJev` is annotated as the `Jev` port, and no test patches the port.
Evidence: the command output, the definition of `FakeJev`, and the output of a `git grep` for a patch of the port under `apps/pipeline/tests/` and `packages/`.

AT-10: Only the league package imports the SDK
App: pipeline
Stories: 1, 2
Given: the Spec branch
When: a reader runs `git grep -n typesafe_sdk -- '*.py'`.
Then: the only match outside the tests is the one adapter module in the league package, and the layer rule maps the port module to the provider layer. `make -C apps/pipeline rules` passes.
Evidence: the output of the `git grep`, the layer map entry, and the output of the rule tests.

AT-11: All question text sits in one module
App: pipeline
Stories: 9
Given: the Spec branch
When: a reader runs a `git grep` for the text of the Jev question.
Then: the text appears in one module of the facts package, outside the tests.
Evidence: the output of the `git grep`.

AT-12: The ADR records the vendor, the data sent, and the pass rule
App: pipeline
Stories: 18
Given: the Spec branch
When: a reader opens the new ADR in `docs/adr/`, numbered after 0028.
Then: it states that TypeSafe Jev is the second model vendor, that blurbs and fact sheets with names go to TypeSafe and that TypeSafe does not train on them, and that a Jev answer passes no check alone and a failed call never counts as a pass. It names the Jev port as the third port with one fake.
Evidence: the path and the text of the ADR.

AT-13: The glossary and the README match the code
App: pipeline
Stories: 19, 22
Given: the Spec branch
When: a reader opens `GLOSSARY.md` and the README of the pipeline package.
Then: **Jev check** says that it runs beside the Claude check in the weekly build and logs only. The README lists the Jev port beside the `Writer` port and names `TYPESAFE_API_KEY` beside `ANTHROPIC_API_KEY`.
Evidence: the lines of `GLOSSARY.md` and of the README.

AT-14: Out of scope: no other app or command changes
App: pipeline
Stories: none
Given: the Spec branch
When: a reader runs `git diff --stat main...jev`.
Then: no file changes under `apps/site/`, `apps/api/`, `packages/analyzer/`, or `packages/midseason/`. The `publish` command does not change. No change adds a cascade, a tone question, or a cause question.
Evidence: the output of `git diff --stat main...jev`, and the diff of `apps/pipeline/src/cornerstone/cli.py` if it changed.

## Trace

Story 1: AT-10
Story 2: AT-10
Story 3: AT-9
Story 4: AT-1
Story 5: AT-2
Story 6: AT-4
Story 7: AT-1, AT-5
Story 8: AT-6
Story 9: AT-11
Story 10: AT-1
Story 11: AT-1
Story 12: AT-3
Story 13: AT-2, AT-3
Story 14: AT-3
Story 15: AT-1
Story 16: AT-8
Story 17: AT-7
Story 18: AT-12
Story 19: AT-13
Story 20: no test. Reason: AT-1 shows the saved labels. Their use belongs to a later spec.
Story 21: no test. Reason: AT-5 shows the shape of a request. A fit for later questions is a judgment, not a behavior.
Story 22: AT-13
Out of scope "The live cascade and its bar": AT-2, AT-14
Out of scope "The tone and cause questions and the flags at publish": AT-5, AT-14
Out of scope "The midseason build and its re-check": AT-14
Out of scope "The analyzer, the API, the Fly deploy, and the app key": AT-14

## Revisions

None yet.
