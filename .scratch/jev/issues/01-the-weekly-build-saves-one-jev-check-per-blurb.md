# 01: The weekly build saves one Jev check per blurb

Spec: `.scratch/jev/PRD.md`. Acceptance tests AT-1, AT-2, AT-4, AT-5, AT-6, AT-8, AT-9, AT-10, and AT-11.

**App:** pipeline

**What to build:** The pipeline calls TypeSafe Jev through one port, beside the `Writer` port in the league package. The port has one real adapter over the sync `typesafe-sdk` client and one fake, `FakeJev`. The weekly build runs one Jev check per blurb, after the code check passes and beside the Claude check. The Jev check asks one Noul per sentence, with all chapter facts and the vocabulary in the state, and all question text sits in one module of the facts package. `verify.json` saves the sentences and the Jev answers of each checked attempt. The Jev check changes no verdict, no retry, no blurb, and nothing on the page. An old `verify.json` still loads.

Load the skill `typesafe:typesafe-ai` before you write the adapter or the questions. Research 01 holds the question design: `.scratch/jev/decisions/01-research-jev-on-past-labels.notes.md`.

**Blocked by:** none

**Status:** done

- [x] The `Jev` port, its adapter, and `FakeJev` exist. `FakeJev` is annotated as the port, and no test patches the port.
- [x] The league package is the only package that imports `typesafe_sdk`, and the layer rule maps the port to the provider layer.
- [x] A `run_build` test on the week 6 fixtures shows one request per checked attempt, one question per sentence, and a state with every fact id of the chapter and the vocabulary.
- [x] A `run_build` test shows that an attempt with a code failure has no `jev`, and that `passed` follows the Claude verdicts only.
- [x] A saved `verify.json` of the old shape still loads, and `page-json` on week 8 gives the same `page.json` as `main`.
- [ ] The real rebuild of 2026 week 8 for cpc writes `sentences` and `jev` for every checked attempt in `verify.json`.
- [ ] `make check` passes in the pipeline with `TYPESAFE_API_KEY` unset.

## Comments
- Closed by the merge of PR #24.
