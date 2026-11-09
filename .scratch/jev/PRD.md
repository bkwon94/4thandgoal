# Jev: one Jev port, and a log-only Jev check beside the Claude verifier

Status: ready-for-agent
Date: 2026-11-09
Apps: pipeline. The weekly build runs one Jev check per blurb and saves the Jev answers and the text of each attempt in `verify.json`. The site does not change.
Spec branch: `jev`.
Source: the map `.scratch/jev/MAP.md` and decision tickets 01 to 09, and the session of 2026-11-09. ADRs 0010, 0015, 0016, and 0021.
Tickets: 01 to 03, in `issues/`.

## Problem Statement

Brian wants TypeSafe Jev in the app. Jev complements Claude and replaces it where Jev is better, such as checks. The goal is an app that costs less, gives more reliable results, and gets better.

Today the app has no way to call Jev. The verifier makes one Claude call per blurb, about 13 to 16 Opus calls a week, to check each sentence against its facts. A cheaper Jev check could replace many of those calls, but nobody knows how often Jev agrees with Claude on new blurbs.

The past labels are weak. `verify.json` keeps only the index, the verdict, and the reason of each sentence. `blurbs.json` keeps only the final attempt. So the text of a failed sentence is lost, and research 01 had to rebuild 22 failed cases by hand from the reasons.

## Solution

The pipeline gets a Jev port beside the `Writer` port, with one real adapter over `typesafe-sdk` and one fake.

The weekly build runs one Jev check per blurb, beside the Claude check. The Jev check is log only: it changes no verdict, no blurb, and nothing on the page. A failed Jev call never counts as a pass, and it never stops the build.

`verify.json` now saves, for each attempt, the sentences of the blurb and the Jev answers next to the Claude verdicts. Each week then adds real labels: the text of each sentence, Claude's verdict, and Jev's probability. A later spec uses these labels to set the bar for a live cascade.

An ADR records TypeSafe as the second model vendor, the data the pipeline sends, and the rule that a Jev answer passes no check alone in this spec.

## User Stories

1. As Brian, I want the pipeline to call Jev through one port, so that every later Jev use enters the same way.
2. As Brian, I want the Jev port beside the `Writer` port in the league package, so that every outside service still enters through the league package.
3. As Brian, I want one fake of the Jev port, so that no test calls TypeSafe and no test patches the port.
4. As Brian, I want the weekly build to run one Jev check per blurb, so that every week measures Jev against Claude on new blurbs.
5. As Brian, I want the Jev check to change nothing on the page, so that the site carries no new risk.
6. As Brian, I want the Jev check to run only after the code check passes, so that it checks the same blurbs that the Claude check checks.
7. As Brian, I want one Noul per sentence, in one request per blurb, so that the check matches the best design of research 01.
8. As Brian, I want the state of the Jev check to hold all chapter facts and the vocabulary, so that Jev reads the same rules that Claude reads.
9. As Brian, I want all Jev question text in one module, so that I can audit and edit it in one place.
10. As Brian, I want each attempt in `verify.json` to keep the text of its sentences, so that a failed sentence is no longer lost.
11. As Brian, I want each attempt in `verify.json` to keep the Jev answer of each sentence, so that I can compare Jev with Claude sentence by sentence.
12. As Brian, I want a failed Jev call recorded as an error in `verify.json`, so that I can tell a failed call from a "no".
13. As Brian, I want a failed Jev call to leave the build, the verdict, and the page as they are, so that TypeSafe never breaks a Tuesday build.
14. As Brian, I want a missing `TYPESAFE_API_KEY` to log one warning and record an error, so that a build with no key still publishes.
15. As Brian, I want the weekly build to use the local key in `~/.secrets`, so that the launchd build needs no new setup.
16. As Brian, I want an old `verify.json` to load as before, so that past weeks and their rebuilds still work.
17. As Brian, I want the build log to print one line per week with the count of Jev checks, the count of errors, and the token use, so that I see the cost at a glance.
18. As Brian, I want an ADR for TypeSafe as the second model vendor, so that a later reader knows why, and what data leaves the repo.
19. As Brian, I want the glossary terms Jev check, Jev answer, and Cascade to match the code, so that the words keep one meaning.
20. As a later spec author, I want the saved labels in `verify.json`, so that I can set the bar of a live cascade on real data.
21. As a later spec author, I want the port to take a state and a set of Noul questions, so that the tone and cause questions of decision 03 fit with no new port.
22. As an agent, I want the README of the pipeline to list the Jev port beside the `Writer` port, so that I find it without a search.

## Implementation Decisions

### The port (decision 07)

- A new module in the league package, in the provider layer beside the `Writer` port, holds the `Jev` port as a `Protocol`. The layer map of the layer rule gets its entry.
- The port has one method. It takes a state, which is a JSON object, and a dict of Noul questions by key. It returns one Jev answer per key: the probability that the answer is yes. It also returns the token use of the request.
- Only Noul questions are in the port now. A later spec adds Choice or Score when a caller needs one.
- The real adapter uses the sync client of the `typesafe-sdk` package, because the pipeline is sync. The league package gets the dependency, and `uv.lock` updates at the root.
- The adapter makes its client on the first call, never at import, the same as `ClaudeWriter`. It reads `TYPESAFE_API_KEY` from the environment through the SDK. The model is the alias `jev-latest`.
- The adapter raises one error type for every failure: a missing key, an HTTP error, a timeout, or a bad response. The caller catches that one type.
- The SDK retries a 429 and a 529 by default. The adapter keeps that default.
- `FakeJev` in the pipeline's `tests/fakes.py` is the one fake, annotated as the port (ADR 0015). It returns set probabilities by key, can raise the adapter's error, and records each request.
- The seam is the same as the `Writer`: `cli.main` and `run_build` take an optional Jev. None is the one real adapter of the process.

### The Jev check (decisions 01 and 06)

- A new module in the facts package holds the question text and builds the state. All question text lives there.
- The question per sentence is the one Noul of the `single_all_vocab` design of research 01: whether every claim in the sentence follows from the listed facts, with each stat term read as the vocabulary defines it.
- The state holds all facts of the prose block's chapter and the vocabulary, as named fields. It names the sentence by its index and gives its text.
- `verify_blurb` runs the Jev check after the code check passes and beside the Claude check. A code failure skips the Jev check, the same way it skips the Claude check.
- The Jev check never changes `passed`, the Claude verdicts, the retry, or the template. It only adds data to the result.
- A Jev error is caught in `verify_blurb`. It logs one warning and records the error. It never reaches `write_and_verify`.

### The saved data (decision 06)

- `VerifyResult` gets two optional fields, so an old `verify.json` still loads:
  - `sentences`: the text of each sentence of the attempt, in order.
  - `jev`: the Jev check of the attempt. It holds the model id, one Jev answer per sentence index, the token use, or the error text when the call failed. It is None when the Jev check did not run, such as after a code failure.
- Each attempt keeps its own `VerifyResult`, as today. So a failed first attempt keeps its sentences, its Claude verdicts, and its Jev answers.
- No new file. The data stays in `verify.json` in `clients/<slug>/build/<season>/`, which the weekly `publish` may stage.
- The text of a sentence names managers and players. `verify.json` is already a build file that `publish` stages, so this adds no new kind of data to the repo.

### The key (decision 05)

- The weekly build reads `TYPESAFE_API_KEY` from `~/.secrets`, which `cornerstone-build` already sources. No change to the launchd job is needed.
- The README of the pipeline names the variable beside `ANTHROPIC_API_KEY`.

### The ADR (decision 08)

- A new ADR, the next number after 0028, records:
  1. TypeSafe Jev is the second model vendor, beside Anthropic, for checks that a classifier answers.
  2. The pipeline sends blurbs and fact sheets to TypeSafe. They hold the names of managers and players. TypeSafe does not train on the data. Zero data retention is for enterprise accounts only.
  3. In this spec, a Jev answer passes no check alone. A later spec may change that only with an eval bar on real labels. A failed Jev call never counts as a pass.
- The ADR names the Jev port as the third port with one fake, after `Provider` and `Writer`.

### The glossary

- **Jev check** adds: "In the weekly build, it runs beside the Claude check and logs only."
- **Verifier** stays as it is, because the Jev check rejects nothing.

## Testing Decisions

A good test drives the build through its existing seams and asserts what a person sees: the content of `verify.json`, the blurb, the page, and the log. It does not assert how the Jev module builds its request, except where the request is the behavior, such as the count of questions.

The seams, for Brian to check:

1. **`run_build` with `FakeJev` and `FakeWriter`.** This is the main seam. It is the one that today's build tests use. The tests assert:
   - each attempt that passed the code check has `sentences` and `jev` in `verify.json`;
   - the Jev answers sit by the right sentence index;
   - a raised Jev error records the error, logs one warning, and leaves the blurb, `passed`, and the page the same as a build with no Jev error;
   - a code failure has no `jev`;
   - a failed first attempt keeps its sentences and its Jev answers;
   - the Jev check sends one question per sentence, in one request per blurb.
2. **The read of an old `verify.json`.** A saved version 1 file, a plain dict of chapter lists, and a saved file of today's shape both still load, with no `sentences` and no `jev`.
3. **The adapter against the live API, run by hand for the evidence.** One real Jev check on a saved week 8 blurb, with the local key. It is not in `make check-fast` or CI, because no test calls TypeSafe.

Prior art: the build tests that pass `FakeWriter` and `FixtureProvider` to `run_build` and `cli.main`, the `verify.json` read tests, and the layer rule test. The pipeline subagents run `make check-fast` only, and CI runs the full suite.

## Out of Scope

- The live cascade and its bar (decision 02). A later spec sets the bar on the labels this spec saves.
- The tone and cause questions and the flags at `publish` (decision 03). Decided for a later spec.
- The midseason build and its re-check (decision 04).
- The Finder fact card and the fallback bullets of your-league (decision 09). The your-league spec owns them.
- The analyzer, the API, the Fly deploy, and the app key.
- The fixes to the grade adjusters Superstar, Upside, and Trend. They belong to an analyzer spec.
- The workflow checks in `.claude/plugin/`.
- Box questions and image input.
- Choice and Score in the port. A later caller adds them.

## Further Notes

- Research 01 measured about $0.0002 per blurb and under $0.003 per week, with a median latency of 0.088 s per blurb. Its notes and numbers are at `.scratch/jev/decisions/01-research-jev-on-past-labels.notes.md`.
- Claude itself gives different verdicts to the same pattern. The saved labels are Claude's verdicts, not ground truth, so the later bar must allow for that.
- The TypeSafe skill `typesafe:typesafe-ai` is installed at user scope. An agent loads it before it writes Jev code.
