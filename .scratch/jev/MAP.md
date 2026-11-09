# Jev: map

App: pipeline.
Spec branch: `jev`.

Outcome: the app has one Jev port, and the weekly build runs a Jev check beside the Claude verifier.
Goal: Jev complements Claude and replaces it where Jev is better, such as checks. The app costs less, gives more reliable results, and gets better.

## DESTINATION

One spec. It adds the Jev port beside the `Writer` port, and the weekly build runs one Jev check per blurb.
The facts check becomes a live cascade behind an eval bar. The tone and cause questions only log their flags.

## DECISIONS SO FAR

- The spec covers the setup and every blurb check: the facts check, the tone questions, and the cause questions, in one Jev request per blurb. Brian, 2026-11-09.
- The facts check goes live as a cascade, but only if the eval on past `verify.json` labels clears the bar of ticket 02. Otherwise it stays log only. Brian, 2026-11-09.
- The tone and cause questions log only. A later spec makes them gate the build. They have no past labels. Brian, 2026-11-09.
- A failed Jev call never counts as a pass. The blurb goes to the Claude check.
- The terms are Jev check, Jev answer, and Cascade. "Verdict" stays with the analyzer and the Judge. Brian, 2026-11-09.

## NOT YET SPECIFIED

- How well do Jev answers agree with the past Claude verdicts, and which question text and state work best? `decisions/01-research-jev-on-past-labels.md`.
- Which eval bar and which probability threshold make the cascade live? `decisions/02-grill-cascade-bar.md`.
- Which tone and cause questions does the Jev check ask, and where do the flags show? `decisions/03-grill-tone-and-cause-questions.md`.
- Does the cascade also cover the midseason blurbs and the `midseason-publish` re-check? `decisions/04-grill-midseason-scope.md`.
- Which key does the weekly build use: the local key or the app key? `decisions/05-grill-build-key.md`.
- Where does the Jev log live, and in what format? `decisions/06-spec-jev-log.md`.
- What shape does the port take: the SDK or plain HTTP, sync or async, and the fake? `decisions/07-spec-port-shape.md`.
- Which ADR records the vendor, the data sent to TypeSafe, and the pass rule? `decisions/08-spec-adr.md`.

## OUT OF SCOPE

- The Finder facts and the fallback bullets of your-league. The your-league spec owns them, after this spec merges.
- The analyzer faithfulness check and the free-text trade request. They need the API, the Fly deploy, and the app key.
- The workflow checks in `.claude/plugin/`, such as the evidence check and the STE check. They change the dev tools, not the app.
- Box questions on images. Image input needs an opt-in header, and no blurb check needs it.
