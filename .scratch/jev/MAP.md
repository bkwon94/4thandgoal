# Jev: map

App: pipeline.
Spec branch: `jev`.

Outcome: the app has one Jev port, and the weekly build runs a Jev check beside the Claude verifier.
Goal: Jev complements Claude and replaces it where Jev is better, such as checks. The app costs less, gives more reliable results, and gets better.

## DESTINATION

One spec, the bare minimum. It adds the Jev port beside the `Writer` port, with the `typesafe-sdk` client and one fake.
The weekly build runs one Jev check per blurb on the facts, log only, and writes the Jev answers beside `verify.json`.
The build also saves the text of each failed attempt, so real labels build up for a later cascade. An ADR records the vendor and the data sent.

## DECISIONS SO FAR

- Brian narrowed the spec to the bare minimum on 2026-11-09: the port, the local key, one log-only Jev check on the facts, the saved failed attempts, and the ADR.
- A failed Jev call never counts as a pass. In this spec the Jev check changes nothing on the page.
- The terms are Jev check, Jev answer, and Cascade. "Verdict" stays with the analyzer and the Judge. Brian, 2026-11-09.
- One Noul per sentence, one request per blurb, with all chapter facts and the vocabulary in the state, works best on past labels. The labels are weak. `decisions/01-research-jev-on-past-labels.md`.
- The weekly build uses the local key from `~/.secrets`. `decisions/05-grill-build-key.md`.
- A Jev fact card is a fourth option for your-league ticket 04. It does not replace the Claude sentence. `decisions/09-research-finder-fact-rank.md`.
- The spec `PRD.md` records the log in `verify.json`, the port shape, and the ADR. Brian approved it on 2026-11-09. `decisions/06-spec-jev-log.md`, `decisions/07-spec-port-shape.md`, `decisions/08-spec-adr.md`.

## NOT YET SPECIFIED

None.

## OUT OF SCOPE

- The live cascade and its bar. A later spec sets the bar on the real labels this spec saves. `decisions/02-grill-cascade-bar.md`.
- The tone and cause questions and the flags at `publish`. Decided for a later spec. `decisions/03-grill-tone-and-cause-questions.md`.
- The midseason build and its re-check. `decisions/04-grill-midseason-scope.md`.
- The Finder facts and the fallback bullets of your-league. The your-league spec owns them, after this spec merges.
- The analyzer faithfulness check, the free-text trade request, and a Jev check on whether a manager would accept a trade. They need the API, the Fly deploy, and the app key.
- The fixes to the grade adjusters: Superstar, Upside, and Trend. Research 09 found trades that pass the Finder because of them. They belong to an analyzer spec, not to Jev.
- The workflow checks in `.claude/plugin/`, such as the evidence check and the STE check. They change the dev tools, not the app.
- Box questions on images. Image input needs an opt-in header, and no blurb check needs it.
