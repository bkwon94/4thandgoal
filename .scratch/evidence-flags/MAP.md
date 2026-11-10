# Evidence flags: map

App: pipeline.
Spec branch: `evidence-flags`.

## DESTINATION

After the evidence agent records each acceptance test, Jev reads the test and its evidence and gives each Evidence flag with a reason. The agent closes each gap while its server still runs, so the Judge passes the work in fewer rounds. A replay against past Judge rounds sets the bar before Jev enters the flow.

## DECISIONS SO FAR

- The destination is one spec for the evidence stage. Jev gives Evidence flags only, and the Judge stays all Claude and gives each Test verdict. Brian chose it on 2026-11-10, after the count of FAIL and BLOCKED results in 16 Judge rounds of six specs.
- The Jev call is a `cornerstone evidence-flags` subcommand in the pipeline CLI. It reuses `JEV`, `FakeJev`, and the shape of `advisor_eval`. The root `scripts/` stay standard-library only. Brian left the choice to Claude on 2026-11-10.
- The term is Evidence flag, in `GLOSSARY.md`. "Check", "screen", and "verdict" already have other meanings.
- The text questions are in scope: each fact that the test names, and a test of motion with only still shots as evidence.
- Jev takes PNG and JPEG images, 280 to 1568 px per side, with SDK 0.7.5. So the question about cut-off text in a screenshot is in scope, and the `Jev` port gets an image type. `decisions/01-research-jev-image-input.md`.

- The replay found 7 evidence gaps in 12 past FAIL and BLOCKED results. Questions (a) and (b) catch 3 of the 4 gaps of their kinds. Question (c) asks only about the text that the Then line names. `decisions/02-research-replay-past-rounds.md`.
- Question (d) checks each Observation sentence against the files. It catches 2 of 4 such gaps. Jev catches 5 of the 7 past gaps in all, and misses AT-50 and AT-47. `decisions/06-research-observation-question.md`.
- On a flag, the agent records again, hands a defect to a fix group, or writes a disagreement line. It never stops, and it has one loop per test. The flags go into `FLAGS.md`, which the Judge never reads. `decisions/04-grill-agent-on-flag.md`.

## NOT YET SPECIFIED

- What hit rate and what false-flag rate let Jev into the flow? `decisions/03-grill-replay-bar.md`, after ticket 06.
- What does Jev read, what happens when Jev is down or the key is missing, and what does the cost log line show? How does the caller cut a tall full-page shot into parts of 1568 px or less? `decisions/05-spec-state-failure-log.md`.

## OUT OF SCOPE

- Jev triage of the review findings and of the model tier of each fix group. It gets its own spec, after this one shows the Jev bar works in the flow.
- Jev routes each ticket to a model tier and predicts merge conflicts. It gets its own spec, for the same reason.
- Any Jev use by the Judge. The Judge stays fresh and all Claude, so no check gets weaker.
