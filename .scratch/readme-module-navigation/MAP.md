# README module navigation: map

App: site, pipeline, and API, with relevant packages.
Spec branch: `readme-module-navigation`.

## DESTINATION

READMEs name the module an agent needs, so the agent finds it without a read of most of the repo.
One spec defines the README and agent instruction edits, plus the test that proves this outcome.

## DECISIONS SO FAR

Brian confirms these bounds for Stage 1:

- The scope covers all three apps and relevant packages. Decision 02 records the approved coverage.
- Edits affect READMEs and agent instructions only. No module moves or code changes belong to this feature.
- Cold agents start at the repo root with representative tasks from each app.
- Each agent reads at most 10 files, including instructions and READMEs, and records every file read.
- Each agent names the correct target module and relevant test file, with reasons for both choices.

Brian approves the six tasks and expected module and test paths in `decisions/01-grill-representative-task-set.md`.
Each app has one app-owned task and one package-owned task.
This set gives representative coverage; it does not cover every package.
The pipeline projection task covers a historical gap from ticket 07 at its current package path.
Brian approves the 13-document coverage and navigation structure in `decisions/02-grill-readme-coverage-and-structure.md`.
The route follows root instructions, app README, owner README, then the module and its test.
Owner READMEs keep `Knows`, `Ports`, and `Does not do`, with module responsibilities and test pointers together.
Each owner or module README in scope has at most 24 physical lines, with blank lines included.
App READMEs have concise navigation sections and no whole-file cap.
The scope includes an API app README and the root correction that the API imports no pipeline code.
Brian approves the cold-agent test procedure in `decisions/03-grill-cold-agent-test-procedure.md`.
One fresh agent runs each of the six approved tasks, with the same model and repository revision.
Agents receive their task prompt and common procedure, with no inherited history or expected answers.
A test-only exception suspends state and ticket reads. Cold agents cannot read `.scratch/` or `docs/agents/state.md`.
Each distinct file counts once, including partial reads, automatic instruction loads, external instructions, and files exposed by content search.
Filename listings cost no file reads. An eleventh distinct file fails the run.
All six agents must find the correct module and test within the limit, with reasons and ordered, complete read logs.
An auditor checks the logs against tool traces and the automatic context inventory. Failed runs remain evidence.
The Judge supplies the acceptance tests' Test verdicts.

Source: `.scratch/week-8-fixes/issues/07-the-readmes-name-the-module-an-agent-needs.md`.
That ticket supplies prior evidence and candidate gaps; its paths and details need a current check.

## NOT YET SPECIFIED

None.

## OUT OF SCOPE

- Module moves, code changes, and test code changes exceed the confirmed scope.
- Product behavior changes do not serve the navigation outcome.
- The remaining historical ticket 07 gaps exceed the six approved routes and need separate scope decisions.
  They cover provider refresh, saved data, prompt tests, fact selection, and build behavior. Brian keeps ticket 07 open.
- Work beyond the map and open decision tickets belongs to later skill stages.
