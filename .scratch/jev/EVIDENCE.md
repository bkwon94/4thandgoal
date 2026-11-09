# Jev: evidence

Spec: `.scratch/jev/PRD.md`. Acceptance tests: `.scratch/jev/ACCEPTANCE.md`.
Built from: `3f0301ff`, on 2026-11-09. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: no site round. All 14 tests are pipeline tests, so no test has a `steps.json`.

The week 8 rebuilds ran in a detached worktree at `3f0301ff`, so the background `make check` and the rebuilds did not share one `.venv`. The rebuilds wrote under `clients/cpc/`, and each file was put back with `git restore` after its copy went into `evidence/`. `scripts/attempts.py` reads a `verify.json` and prints one line per attempt.

## AT-1: Each checked attempt saves its sentences and its Jev answers

App: pipeline
Then: in `clients/cpc/data/2026/week-08/verify.json`, every attempt with no code failure has `sentences` with the text of each sentence, and `jev` with one Jev answer per sentence index. Each answer is between 0 and 1, and the model id starts with `jev-`.
Files: `evidence/AT-1/rebuild.log`, `evidence/AT-1/verify.json`, `evidence/AT-1/attempts.txt`, `evidence/scripts/attempts.py`
Observation: The rebuild with the key exited 0 and made real `POST https://api.typesafe.ai/v1/systemone` calls. `attempts.txt` lists 19 attempts, 14 with no code failure. Each of the 14 has as many Jev answers as sentences, with indexes 0 to n-1, every answer between 0 and 1, and the model `jev-1.14.0`. The 5 attempts with a code failure have no answers and the model None.

## AT-2: The Jev check never skips the Claude check

App: pipeline
Then: every attempt with no code failure has one Claude verdict per sentence. `passed` equals "every Claude verdict is supported", for every attempt, whatever the Jev answers are.
Files: `evidence/AT-2/attempts.txt`, `evidence/AT-1/verify.json`, `evidence/scripts/attempts.py`
Observation: For each of the 14 checked attempts, the count of Claude verdicts equals the count of sentences. `passed_equals_rule=True` on all 19 lines. `awards` attempt 1 has `passed=False` with a lowest Jev answer of 0.63, and `rankings` attempt 1 has `passed=True` with a lowest Jev answer of 0.24.

## AT-3: A missing key leaves the build whole

App: pipeline
Then: the build exits 0 and writes `clients/cpc/build/2026/week-08/page.json`. In `verify.json`, every attempt with no code failure has a `jev` with an error text and no answers. The log shows one warning per checked attempt that names the Jev error.
Files: `evidence/AT-3/rebuild.log`, `evidence/AT-3/verify.json`, `evidence/AT-3/jev-field.txt`, `evidence/scripts/attempts.py`
Observation: The command line of the log has `env -u TYPESAFE_API_KEY`, and the log ends with the path of the written `page.json` and `exit 0`. `jev-field.txt` lists 17 attempts. Each of the 13 checked attempts has `"answers": []` and the error `TypeSafeError: No API key was provided...`, and the 4 code-failed attempts have `jev=null`. The log has 13 lines `WARNING facts.verifier: Jev check failed for <chapter>: TypeSafeError: No API key was provided...`, one per checked attempt.

## AT-4: A code-failed attempt has no Jev check

App: pipeline
Then: the attempt with the code failure has `jev` None in `verify.json`, and `FakeJev` recorded no request for it. The second attempt, which passes the code check, has a `jev`.
Files: `evidence/AT-4/pytest.txt`, `evidence/AT-4/source.py.txt`
Observation: `test_an_attempt_with_a_code_failure_has_no_jev_check` passed. Its source asserts `first.code_failures and first.jev is None`, `not second.code_failures and second.jev is not None`, and that no recorded request has the blurb of the first attempt.

## AT-5: One request per blurb, with one question per sentence

App: pipeline
Then: `FakeJev` recorded exactly one request for each attempt that passed the code check. Each request has one question key per sentence of that attempt, and no other key.
Files: `evidence/AT-5/pytest.txt`, `evidence/AT-5/source.py.txt`
Observation: `test_each_checked_attempt_saves_its_sentences_and_one_jev_answer_per_sentence` passed. Its source asserts `len(jev.requests) == len(checked)` and, per request, `len(request.questions) == len(result.sentences)`.

## AT-6: The state holds all chapter facts and the vocabulary

App: pipeline
Then: the state of each recorded request holds every fact id of its chapter and the vocabulary text of the client.
Files: `evidence/AT-6/pytest.txt`, `evidence/AT-6/source.py.txt`
Observation: `test_the_state_holds_every_chapter_fact_and_the_vocabulary_of_the_client` passed. Its source asserts that the fact ids of the chapter are a subset of `request.state["facts"]`, and that `request.state["vocabulary"]` equals the terms parsed from the client's `vocabulary.md` with the median terms.

## AT-7: The build log shows the Jev line

App: pipeline
Then: the log has one Jev line for the build. It gives the count of Jev checks, the count of errors, and the token use. The count of checks equals the count of attempts with a `jev` in `verify.json`.
Files: `evidence/AT-7/jev-line.txt`, `evidence/AT-1/rebuild.log`
Observation: `grep "Jev:"` finds one line: `Jev: 14 checks, 0 errors, 74573 input tokens`. The count from `verify.json` is 14 attempts with a `jev`, and their `input_tokens` sum to 74573.

## AT-8: An old verify.json still loads

App: pipeline
Then: the command exits 0, and `clients/cpc/build/2026/week-08/page.json` is the same as on `main`.
Files: `evidence/AT-8/output.txt`
Observation: `verify.json` has no diff against `main`, and its attempts have only the keys `chapter`, `code_failures`, `passed`, and `verdicts`. `page-json` printed the path of `page.json` and exited 0. `git diff --stat main -- clients/cpc/build/2026/week-08/page.json` printed nothing.

## AT-9: No test calls TypeSafe

App: pipeline
Then: every check passes. `FakeJev` is annotated as the `Jev` port, and no test patches the port.
Files: `evidence/AT-9/output.txt`, `evidence/AT-9/fakejev.txt`, `evidence/AT-9/grep.txt`
Observation: `env -u TYPESAFE_API_KEY make -C apps/pipeline check` ends with `exit 0`. `fakejev.txt` shows `class FakeJev` and `FAKE_JEV: Jev = FakeJev()`. The grep for a `monkeypatch.setattr`, `mock.patch`, or `patch(` of a Jev name exits 1 with no match. The only `monkeypatch` in the Jev test file is a `delenv` of the key.

## AT-10: Only the league package imports the SDK

App: pipeline
Then: the only match outside the tests is the one adapter module in the league package, and the layer rule maps the port module to the provider layer. `make -C apps/pipeline rules` passes.
Files: `evidence/AT-10/grep.txt`, `evidence/AT-10/layer-map.txt`, `evidence/AT-10/rules.txt`
Observation: The grep finds `packages/league/python/src/league/jev.py:5` and one line in `apps/pipeline/tests/test_jev_check.py`. The layer map has `"league.jev_port": "provider"` and `"league.jev": "provider"`. `make -C apps/pipeline rules` gives `49 passed` and `exit 0`.

## AT-11: All question text sits in one module

App: pipeline
Then: the text appears in one module of the facts package, outside the tests.
Files: `evidence/AT-11/grep.txt`
Observation: The full question, the yes text, and the no text each match only in `packages/facts/python/src/facts/jev_check.py`. The first grep also matches a shorter question of an older design in the research notes under `.scratch/jev/decisions/`, which is not code.

## AT-12: The ADR records the vendor, the data sent, and the pass rule

App: pipeline
Then: it states that TypeSafe Jev is the second model vendor, that blurbs and fact sheets with names go to TypeSafe and that TypeSafe does not train on them, and that a Jev answer passes no check alone and a failed call never counts as a pass. It names the Jev port as the third port with one fake.
Files: `evidence/AT-12/adr.txt`
Observation: `docs/adr/0029-typesafe-jev-is-the-second-model-vendor.md` lists the three choices in those words, and its section "The third port" names the Jev port after `Provider` and `Writer`, with `FakeJev` as its one fake.

## AT-13: The glossary and the README match the code

App: pipeline
Then: **Jev check** says that it runs beside the Claude check in the weekly build and logs only. The README lists the Jev port beside the `Writer` port and names `TYPESAFE_API_KEY` beside `ANTHROPIC_API_KEY`.
Files: `evidence/AT-13/lines.txt`
Observation: `GLOSSARY.md:232` reads "In the weekly build, it runs beside the Claude check and logs only." `apps/pipeline/src/cornerstone/README.md` lines 16 and 17 list `Writer` with `ANTHROPIC_API_KEY` and `Jev` with `TYPESAFE_API_KEY`.

## AT-14: Out of scope: no other app or command changes

App: pipeline
Then: no file changes under `apps/site/`, `apps/api/`, `packages/analyzer/`, or `packages/midseason/`. The `publish` command does not change. No change adds a cascade, a tone question, or a cause question.
Files: `evidence/AT-14/diff-stat.txt`, `evidence/AT-14/cli.diff`, `evidence/AT-14/grep.txt`
Observation: The diff stat of those four paths is empty. `cli.diff` changes only the import of `Jev`, the `jev` seam of `main`, and its pass to `run_build`. The publish code does not change. A whole-word grep of the Python diff finds no `cascade`, `tone`, or `publish`. The word "cause" occurs only in the yes and no text of the one fact question.
