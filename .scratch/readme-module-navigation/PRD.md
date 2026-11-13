# README module navigation

Status: ready-for-agent
Date: 2026-11-12
Apps: site renders published pages. Pipeline builds and publishes weekly data. API serves answers and trade grades through domain packages.
Spec branch: `readme-module-navigation`.
Source: the map `.scratch/readme-module-navigation/MAP.md` and decision tickets 01 to 03. ADRs 0018, 0019, 0021, and 0026.
Tickets: 01 to 02, in `issues/`.

## Problem Statement

An agent needs to find the module that owns a behavior and the test that checks it.
The repo spans three apps and domain packages, but its README links do not give a complete path to each owner.
An agent can read many files before it finds both destinations.
The root instructions also claim that the API imports pipeline code, which misstates its dependency boundary.

Existing README rules check document shape and size.
They do not prove that a fresh agent can find the correct module and test within a small read budget.
Historical ticket 07 identifies pipeline gaps, but it does not define representative tasks across all three apps.

## Solution

Connect root instructions, app READMEs, owner READMEs, and their modules and tests through relative Markdown links.
Group the maps by responsibility, so an agent can choose the owner from the behavior it must change.
Keep each owner README short, with the module, its responsibility, and its relevant test together.

Use the 13 documents from decision 02 to support the six tasks from decision 01.
Each app has one task with an app-owned module and one task with a package-owned module.
Run the cold-agent procedure from decision 03 against those paths.
All six agents must find the correct module and test within ten distinct file reads, with reasons and complete read logs.

## User Stories

1. As an agent, I want app links at the repo root, so that I can choose the relevant app.
2. As an agent, I want app maps by responsibility, so that I can find the owner of a behavior.
3. As an agent, I want direct owner links, so that I can skip unrelated folders.
4. As an agent, I want module responsibilities beside test pointers, so that I can find both destinations together.
5. As an agent, I want relative Markdown links, so that I can follow the maps within my checkout.
6. As an agent, I want short owner READMEs, so that I can read the necessary context quickly.
7. As an agent, I want clear responsibility boundaries, so that I can choose between nearby owners.
8. As a site agent, I want the archive owner and test, so that I can check season and week order.
9. As a site agent, I want the picker owner and test, so that I can check selected-team focus.
10. As a pipeline agent, I want the projection owner and test, so that I can check current roster use.
11. As a pipeline agent, I want the publish owner and test, so that I can check commit scope.
12. As an API agent, I want the answer-cap owner and test, so that I can check daily team isolation.
13. As an API agent, I want the grade-limit owner and test, so that I can check persistence across restarts.
14. As an agent, I want accurate API dependencies, so that I do not search the pipeline for API ownership.
15. As Brian, I want the approved document scope, so that this feature does not expand into unrelated gaps.
16. As Brian, I want existing responsibilities preserved, so that short READMEs do not lose useful context.
17. As Brian, I want six fresh agents, so that prior answers do not affect the trials.
18. As Brian, I want one model and revision, so that all six trials use the same conditions.
19. As Brian, I want all file exposure counted, so that the read budget reflects each agent's actual context.
20. As an auditor, I want complete traces and context inventories, so that I can check every read log.
21. As Brian, I want failed runs preserved, so that the evidence shows unsuccessful trials too.
22. As the Judge, I want path choices and reasons, so that I can assess each acceptance test independently.
23. As an agent, I want normal instructions preserved, so that the trial exception does not change ordinary work.

## Implementation Decisions

### Coverage and ownership

- Limit product-document edits to the 13 documents in decision 02 and the six task paths in decision 01.
- Add the API app README. Add no root README or separate API instruction file.
- Root instructions link all three app READMEs and state the navigation rule.
- Correct the root claim about API dependencies: the API imports no pipeline code.
- Site and pipeline instructions point to their app README for module ownership. Their commands and rules keep their current role.

The site map distinguishes file loaders, app routes, and package parts.
It links the data and analyzer owners.
The pipeline map distinguishes build and publish orchestration from domain packages.
It links the cornerstone and week owners.
The API map distinguishes HTTP composition, app state and limits, and analyzer routes.
It links their owner READMEs.

Owner maps name the archive module, picker focus, publish boundary, current-roster projections, answer caps, and persistent grade limits.
The analyzer map links its form owner and names the Python rate-limit owner with its API integration test.
The week map links its sheet owner and distinguishes roster projections from the rankings odds engine.
The API owner distinguishes daily answer caps from analyzer grade limits.
Preserve unrelated responsibilities in each document.

### Navigation and document shape

- Follow root instructions, app README, owner README, then the module and its test.
- Group app maps by responsibility. Do not repeat the six task answers as a lookup table.
- Link directly to relevant owner READMEs, so an agent need not read each intermediate folder.
- Place each module, its responsibility, and its test together, with relative Markdown links.
- Name the other owner under `Does not do` when a responsibility belongs elsewhere.

Each owner README has a one-line title, then `Knows`, `Ports`, and `Does not do`, in that order.
Test pointers sit within these sections and add no extra heading.
Each owner or module README in scope has at most 24 physical lines, including blank lines.
This bound includes the week sheet README, although existing automated rules do not scan it.
App READMEs have concise navigation sections and no whole-file line cap.

### Instruction boundary

Normal work keeps the state and ticket read requirements.
The cold-agent trials alone suspend those reads, because the tracker holds expected answers.
All other repository and external instructions still apply during the trials.
The test procedure must account for automatic instruction loads within the read budget.
No module move, code edit, test-code edit, schema change, or API contract change belongs to this feature.

## Testing Decisions

### Seams and prior art

The primary seam is an agent's visible behavior from the repository root.
The test asks whether the documentation leads that agent to the correct module and relevant test within the read budget.
A good trial checks path choices, reasons, and actual file exposure.
It does not infer success from the presence of links alone.

Existing README rule tests supply the document-shape seam.
The site rule checks package roots, direct package site folders, and selected site source folders.
It also permits app-root instruction files and rejects deeper instruction files.
The Python rules check package roots and app source folders with an initializer.
The API reuses those Python rules for its source folders.
These checks enforce the existing title, section order, and 24-line limit where they apply.
They do not scan nested package Python folders or impose a whole-file cap on app READMEs.

Use those existing rules without test-code changes.
Check relative links, stated responsibilities, and the 24-line bound across every owner README in scope.
Include the week sheet README in that check.
The exact existing rule files appear under Further Notes.
The six behavior tests remain reference destinations; this feature does not change their assertions or implementations.
No mock implementation or mock mode belongs to these checks.

### Approved tasks

Use each behavior prompt from decision 01 exactly as written.
The expected paths and reasons stay with the auditor, outside the cold agent's context.

| App | Cold-agent behavior prompt |
| --- | --- |
| Site | The week archive must put the newest season first, then order its weeks by number. |
| Site | After I select Change my team, keyboard focus must return to my selected team. |
| Pipeline | The roster projection behind playoff odds must use current players, including additions after the scored week. |
| Pipeline | Publish one week without a commit of stray files or data from another season. |
| API | A team's daily answer allowance must reset tomorrow without a reset of another team's allowance today. |
| API | The daily trade-grade limit must survive an API restart. |

### Cold start and read budget

Run one fresh agent per approved task, for six runs total.
All six runs use the same model and repository revision.
Each agent starts at the repository root, with no inherited history or expected answers.
Each agent receives only its approved task prompt and the common procedure.
The trial exception forbids reads of `.scratch/` and `docs/agents/state.md`.
The exception applies only to these trials; normal work keeps the state and ticket rules.

Count each distinct file once, including partial reads, READMEs, and automatically loaded instruction files.
Count external files too, including external instructions.
Count every file exposed by a content search.
Repeated reads of one file add no further count.
Filename listings expose names only and cost no file reads.
The eleventh distinct file fails the run.

### Evidence and Test verdicts

Each agent names the correct target module and relevant test file within ten distinct file reads.
It gives reasons for both choices and an ordered, complete read log.
All six runs must meet those conditions against the expected answers in decision 01.
Preserve failed runs as evidence.

The auditor compares each read log with the complete tool trace and the automatic context inventory.
The inventory accounts for instruction files that load without a tool call.
Each run's evidence contains its path choices, reasons, complete read log, and audit record.
The procedure records evidence and gives no Test verdict.
The fresh Judge gives each acceptance test its Test verdict under ADR 0026.
Brian's FAIL overrides the Judge.

These sections define future checks; they report no completed trial, evidence record, or Test verdict.

## Out of Scope

- Module moves, code edits, test-code changes, and product behavior changes.
- Documentation beyond the 13 approved documents or task paths beyond the six approved tasks.
- Exhaustive package coverage or task-specific answer tables in product documentation.
- Historical ticket 07 gaps for provider refresh, saved data, prompt tests, fact selection, and build behavior.
- Completion of historical ticket 07, which stays open.

## Further Notes

The approved source records fix the exact scope and expected answers:

- [Decision 01](decisions/01-grill-representative-task-set.md) records all six target modules, test files, and reasons.
- [Decision 02](decisions/02-grill-readme-coverage-and-structure.md) records the exact 13-document list and each document's role.
- [Decision 03](decisions/03-grill-cold-agent-test-procedure.md) records the common procedure and the test-only tracker exception.
- [The map](MAP.md) records the destination, approved decisions, and deferred scope.

The existing rule files are `apps/site/src/readme-rule.test.ts`, `apps/pipeline/tests/test_rule_readmes.py`, and `apps/api/tests/test_rule_api.py`.
The API rule imports the pipeline's README rule helpers; that test reuse does not make the API import pipeline product code.

Historical source: `.scratch/week-8-fixes/issues/07-the-readmes-name-the-module-an-agent-needs.md`.
The approved projection task covers one historical gap at its current week package path.
The old app-local projection path no longer names its owner.
The remaining historical gaps need separate scope decisions.

The local tracker follows ADR 0021.
The spec branch and ticket branches follow ADR 0019.
This spec creates no acceptance tests, ticket list, state row, evidence record, or Test verdict.
After Brian approves this spec, `4ag:to-acceptance readme-module-navigation` is next.
