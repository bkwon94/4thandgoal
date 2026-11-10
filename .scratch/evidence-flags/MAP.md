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

## NOT YET SPECIFIED

- Does TypeSafe Jev take images, and with what limits? `decisions/01-research-jev-image-input.md`.
- Which past labels count as a real evidence gap, and how well does Jev flag them in a replay? `decisions/02-research-replay-past-rounds.md`.
- What hit rate and what false-flag rate let Jev into the flow? `decisions/03-grill-replay-bar.md`.
- What does the evidence agent do on a flag, and what is the loop limit? `decisions/04-grill-agent-on-flag.md`.
- What does Jev read, what happens when Jev is down or the key is missing, and what does the cost log line show? `decisions/05-spec-state-failure-log.md`.

## OUT OF SCOPE

- Jev triage of the review findings and of the model tier of each fix group. It gets its own spec, after this one shows the Jev bar works in the flow.
- Jev routes each ticket to a model tier and predicts merge conflicts. It gets its own spec, for the same reason.
- Any Jev use by the Judge. The Judge stays fresh and all Claude, so no check gets weaker.
