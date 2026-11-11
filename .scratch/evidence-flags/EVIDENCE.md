# Evidence flags: evidence

Spec: `.scratch/evidence-flags/PRD.md`. Acceptance tests: `.scratch/evidence-flags/ACCEPTANCE.md`.
Built from: `ce7257c6`, on 2026-11-10. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.

## AT-1: Motion with only still shots gets a flag

App: pipeline
Then: `"$T"/.scratch/easter-eggs/FLAGS.md` has an entry for AT-32 and question (b), with a probability of 0.7 or more, a reason, and `Action: open`.
Files: `evidence/AT-1/output.txt`, `evidence/AT-1/FLAGS.md`
Observation: `FLAGS.md` has one entry, `## AT-32, question (b)`, with `Probability: 0.98`, a reason that starts "The Then line may ask for motion (at 0.99)", and `Action: open`. The output ends with `Evidence flags: 1 tests, 1 flags, 0 errors, 26958 input tokens` and `exit: 0`.

## AT-2: An Observation that misstates a file gets a flag

App: pipeline
Then: `FLAGS.md` has an entry for AT-54 and question (d), with a probability of 0.7 or more and a reason.
Files: `evidence/AT-2/output.txt`, `evidence/AT-2/FLAGS.md`
Observation: `FLAGS.md` has one entry, `## AT-54, question (d)`, with `Probability: 0.87` and a reason that quotes the Observation sentence "...took 17 s and read "Not as is"..." at "shown at 0.04". The output ends with `Evidence flags: 1 tests, 1 flags, 0 errors, 9076 input tokens` and `exit: 0`.

## AT-3: A fact that no file shows gets a flag

App: pipeline
Then: `FLAGS.md` has an entry for AT-3 and question (a), with a probability of 0.7 or more and a reason.
Files: `evidence/AT-3/output.txt`, `evidence/AT-3/FLAGS.md`
Observation: `FLAGS.md` has one entry, `## AT-3, question (a)`, with `Probability: 0.70` and the reason "No file may show this fact of the Then line: "The same check inside the window matches." (shown at 0.30).". The output ends with `Evidence flags: 1 tests, 1 flags, 0 errors, 3058 input tokens` and `exit: 0`.

## AT-4: Only the questions in the flow are asked

App: pipeline
Then: the question keys that the command prints as asked equal the keys that the questions module marks as in the flow.
Files: `evidence/AT-4/output.txt`, `evidence/AT-4/module-lines.txt`
Observation: The output prints `AT-41: asked a, b, d`, then `Evidence flags: 1 tests, 0 flags, 0 errors, 28513 input tokens, 1 cut` and `exit: 0`. `module-lines.txt` shows `in_flow=True` for keys "a", "b", and "d", and `in_flow=False` for key "c". The run wrote no `FLAGS.md`.

## AT-5: A whole round gives one log line

App: pipeline
Then: the command exits 0 and logs one line `Evidence flags: <tests> tests, <flags> flags, <errors> errors, <tokens> input tokens`. The test count equals the count of entries in `EVIDENCE.md` that do not say `Files: none`. The flag count equals the count of entries in `FLAGS.md`.
Files: `evidence/AT-5/output.txt`, `evidence/AT-5/FLAGS.md`, `evidence/AT-5/counts.txt`
Observation: The output ends with `Evidence flags: 41 tests, 2 flags, 0 errors, 311611 input tokens` and `exit: 0`. `counts.txt` shows 45 entries in `EVIDENCE.md`, 4 with `Files: none` (AT-19 to AT-22), 41 that do not say `Files: none`, and 2 entries in `FLAGS.md` (AT-23 and AT-27, both question (b)).

## AT-6: A missing key leaves the evidence stage whole

App: pipeline
Then: the command exits 0, writes no entry to `FLAGS.md`, and logs `Evidence flags: 2 tests, 0 flags, 2 errors, 0 input tokens`.
Files: `evidence/AT-6/output.txt`, `evidence/AT-6/flags-state.txt`
Observation: The output shows `Jev error, no flags: TypeSafeError: No API key was provided...` for AT-32 and AT-34, then `Evidence flags: 2 tests, 0 flags, 2 errors, 0 input tokens` and `exit: 0`. `flags-state.txt` shows `FLAGS.md` as `absent` after the run.

## AT-7: The eval gives the rates of the final questions

App: pipeline
Then: for each of the four questions (a), (b), (c), and (d), it prints the hits, the misses, and the false flags at its cut, and `meets the bar: yes` or `meets the bar: no`. The in-flow mark of each question in the module equals its bar result.
Files: `evidence/AT-7/output.txt`, `evidence/AT-7/module-lines.txt`
Observation: The output prints one line for each question: (a) 1 hits, 1 misses of 2 gaps, 2 false flags of 44, `meets the bar: yes`; (b) 2 hits, 0 misses of 2 gaps, 0 false flags, `yes`; (c) 0 hits, 0 misses of 0 gaps, 0 false flags, `no`; (d) 2 hits, 1 misses of 3 gaps, 3 false flags, `yes`. It ends with `Evidence flags eval: 56 tests, 0 errors, 664904 input tokens, 9 cut` and `exit: 0`, and `module-lines.txt` shows `in_flow=True` for a, b, and d and `in_flow=False` for c.

## AT-8: The label file holds the past labels and no manager

App: pipeline
Then: the file has 56 tests: 7 `gap`, 5 `defect`, and 44 `pass`. No manager name is in it.
Files: `evidence/AT-8/output.txt`
Observation: The script output shows `tests: 56`, `defect: 5`, `gap: 7`, and `pass: 44`. It searched 24 manager names, the team name and the owner of each of 12 managers, and shows `manager names found: 0 []`.

## AT-9: A Jev error is never a "no flag" in the eval

App: pipeline
Then: the eval counts each test as an error. It counts no test as a hit, a miss, a false flag, or a pass.
Files: `evidence/AT-9/output.txt`, `evidence/AT-9/test-source.txt`
Observation: The test `test_a_jev_error_counts_each_test_as_an_error_never_as_a_miss_or_a_pass` of `apps/pipeline/tests/test_evidence_flags_eval.py` shows `1 passed, 3 deselected in 0.28s` and `exit: 0`.

## AT-10: Every shot goes to Jev as tiles that fit

App: pipeline
Then: the request of `FakeJev` holds a tile of every shot that `Files:` lists, and each tile is 280 to 1568 px on each side.
Files: `evidence/AT-10/output.txt`, `evidence/AT-10/test-source.txt`
Observation: The test `test_every_real_shot_of_a_test_goes_to_jev_as_tiles_that_fit` prints 12 shots of AT-32, each with 1 tile: four at `(1280, 900)`, four at `(768, 900)`, and four at `(375, 900)`. It shows `1 passed, 17 deselected in 0.44s` and `exit: 0`.

## AT-11: A state over 32 MiB is cut and logged

App: pipeline
Then: the request holds the text and the shots that fit, in the order of `Files:`, and the log line ends with `, 1 cut`.
Files: `evidence/AT-11/output.txt`, `evidence/AT-11/test-source.txt`
Observation: The test `test_a_state_over_32_mib_sends_the_shots_that_fit_in_the_order_of_files_and_logs_the_cut` shows `1 passed, 17 deselected in 2.15s` and `exit: 0`.

## AT-12: A test with no files gets no request

App: pipeline
Then: `FakeJev` records one request, for the test with files, and none for the test at `Files: none`.
Files: `evidence/AT-12/output.txt`, `evidence/AT-12/test-source.txt`
Observation: The test `test_a_fact_that_no_file_shows_gets_an_open_flag_and_a_test_with_no_files_gets_no_request` shows `1 passed, 17 deselected in 0.14s` and `exit: 0`.

## AT-13: Only the adapter imports the SDK

App: pipeline
Then: the only file outside tests is `packages/league/python/src/league/jev.py`.
Files: `evidence/AT-13/output.txt`
Observation: The search lists three files: `apps/pipeline/tests/test_jev_check.py`, `apps/pipeline/tests/test_jev_image.py`, and `packages/league/python/src/league/jev.py`. The one file outside `tests/` is `packages/league/python/src/league/jev.py`.

## AT-14: The questions, the cuts, the marks, and the bar sit in one module

App: pipeline
Then: each one is in one module only, outside tests.
Files: `evidence/AT-14/output.txt`
Observation: Each search for the six Noul texts of the four questions, for `cut=0.7`, `cut=0.9`, `in_flow=True`, and `in_flow=False` finds lines only in `apps/pipeline/src/cornerstone/evidence_questions.py`. The definitions `BAR_HIT_RATE = 0.5` and `BAR_FALSE_FLAG_RATE = 0.10` are only in that module, and `apps/pipeline/src/cornerstone/evidence_eval.py` imports both names at line 15 and uses them at lines 92 and 93.

## AT-15: The evidence stage runs the command at the right time

App: pipeline
Then: it runs `evidence-flags` on every site test after the runner round, and on each pipeline test after its output is saved. It commits `FLAGS.md` with `EVIDENCE.md` in the evidence commit.
Files: `evidence/AT-15/output.txt`
Observation: The diff adds the step "Run it on every site test after the runner round, once each test has its entry in `EVIDENCE.md`. Run it on each pipeline test after its `output.txt` is saved." The stop rule changes to "Commit `EVIDENCE.md`, `FLAGS.md`, and `evidence/` on the Spec branch".

## AT-16: The evidence stage gives one action for each kind of flag

App: pipeline
Then: an evidence gap gets a new recording, a product defect goes to the orchestrator as a fix group, and a false flag gets one disagreement line. No entry stays `open` at the evidence commit.
Files: `evidence/AT-16/output.txt`
Observation: The diff adds three items: "An evidence gap" with "record that test again, and set `Action: recorded again`", "A product defect" with "Hand it to the orchestrator as a fix group" and `Action: fix group`, and "A false flag" with `Action: disagree: <one line of why>`. It adds "Set the action of each entry before the evidence commit. No entry stays `open`."

## AT-17: The evidence stage has no stop on a flag and one loop per test

App: pipeline
Then: it says never to ask Brian about a flag. It gives one loop per test, and a flag that stays gets a disagreement line. A product defect is outside the limit, and the limit starts again after its fix merges.
Files: `evidence/AT-17/output.txt`
Observation: The diff adds "Never stop to ask Brian about a flag." and "Each test gets one loop." It adds "If the flag stays, set `Action: disagree: <one line of why>` and go on. A product defect is outside the limit. The limit starts again after its fix merges."

## AT-18: The PR body counts the flags

App: pipeline
Then: the PR body gets one line of counts from `FLAGS.md`, in the shape "9 flags: 5 new recordings, 1 fix group, 3 disagreements".
Files: `evidence/AT-18/output.txt`
Observation: The diff of `pr.md` adds a section `## The Evidence flags` to the body, with "one line of counts of the `evidence-flags` run, from `.scratch/<slug>/FLAGS.md`, such as "9 flags: 5 new recordings, 1 fix group, 3 disagreements"". It adds "Write "0 flags." if the file has no entry or does not exist."

## AT-19: The Judge does not change

App: pipeline
Then: the output is empty.
Files: `evidence/AT-19/output.txt`
Observation: The file holds the command line and `exit: 0`, with no line of diff between them.

## AT-20: The ADR records the new data that goes to TypeSafe

App: pipeline
Then: it says that the evidence of the acceptance tests and its screenshots go to TypeSafe, and that the shots show the names of managers. It says that an Evidence flag is never a Test verdict and never reaches the Judge.
Files: `evidence/AT-20/adr.txt`
Observation: The ADR is `docs/adr/0031-the-evidence-goes-to-typesafe-and-a-flag-is-not-a-verdict.md`. It lists the test text, the evidence files, and "each shot of `evidence/AT-<n>/`" as data that goes to TypeSafe, and says "they show the names of managers and players". It says "A flag never reaches the Judge", and its item 3 says "Only the Judge gives a Test verdict (ADR 0026)."

## AT-21: Out of scope: no Jev in the review, the routing, or the Judge

App: pipeline
Then: the only files are `implement/evidence.md` and `implement/pr.md`.
Files: `evidence/AT-21/output.txt`
Observation: The search lists two files, `.claude/plugin/skills/implement/evidence.md` and `.claude/plugin/skills/implement/pr.md`, with `exit: 0`.

## AT-22: The checks pass with no TypeSafe call

App: pipeline
Then: the check passes.
Files: `evidence/AT-22/output.txt`
Observation: The run with `TYPESAFE_API_KEY` unset shows ruff `All checks passed!`, pyright `0 errors, 0 warnings, 0 informations`, `1628 passed in 80.59s (0:01:20)`, and `2 passed, 1637 deselected in 1.48s` for the serial tests. It ends with `exit: 0`.
