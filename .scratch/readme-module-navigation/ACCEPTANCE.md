# README module navigation: acceptance tests

Spec: `.scratch/readme-module-navigation/PRD.md`.

Status: approved by Brian on 2026-11-12.

The Judge gives each test its Test verdict in `VERDICTS.md`.
The fresh Judge reads only this file and the evidence.
The evidence agent gives no Test verdict.
Every test needs PASS, with no FAIL from Brian, before merge under ADR 0026.

## Evidence format

Brian approves terminal traces and file evidence for site-owned documentation tests on 2026-11-12.
This replaces the acceptance skill's screenshots at 375, 768, and 1280 px in both themes.
These tests inspect files and agent navigation, with no browser output.
Use document excerpts, diffs, command output, and complete agent traces.

Use real repository files and real agent trials.
These checks require no football week fixture.
Do not introduce mock implementations or mock modes.
This file defines tests; it records no completed trial, evidence, or Test verdict.

## Shared fixtures

Use the implementation revision for every document check and all six cold trials.
Record its full commit identifier.
Record the base revision for document preservation and scope comparisons.

The evidence and this acceptance file hold the expected answers.
Cold agents must not receive either.

### Approved document inventory

Only these 13 product documents belong to this feature.

| ID | Document | Approved role |
| --- | --- | --- |
| D1 | `CLAUDE.md` | Link all three app READMEs, state the navigation rule, and correct the API dependency claim. |
| D2 | `apps/site/CLAUDE.md` | Point to the site README for module ownership; retain commands and rules. |
| D3 | `apps/pipeline/CLAUDE.md` | Point to the pipeline README for module ownership; retain commands and rules. |
| D4 | `apps/site/README.md` | Map file loaders, app routes, and package parts; link the data and analyzer owners. |
| D5 | `apps/pipeline/README.md` | Separate build and publish orchestration from domain packages; link cornerstone and week owners. |
| D6 | `apps/api/README.md` | Add the app README; map HTTP composition, app state and limits, and analyzer routes. |
| D7 | `apps/site/src/lib/data/README.md` | Name the archive module, its responsibility, and its test. |
| D8 | `apps/pipeline/src/cornerstone/README.md` | Name the publish module, its commit boundary, and its rule test. |
| D9 | `apps/api/src/cornerstone_api/README.md` | Name answer caps and their test; distinguish analyzer grade limits. |
| D10 | `packages/analyzer/README.md` | Link the form owner; name the Python rate-limit owner and its API integration test. |
| D11 | `packages/analyzer/site/form/README.md` | Name the team picker, its focus responsibility, and its test. |
| D12 | `packages/week/README.md` | Link the sheet owner; distinguish roster projections from the rankings odds engine. |
| D13 | `packages/week/python/src/week/sheet/README.md` | Name `projected_totals` in `base.py` and its pipeline sheet test. |

D7 through D13 are the seven owner or module READMEs.
D4 through D6 are app READMEs.
App READMEs have no whole-file line cap.

### Approved tasks and expected answers

T1 — Site archive

Prompt: The week archive must put the newest season first, then order its weeks by number.
Module: `apps/site/src/lib/data/week-data.ts`
Test: `apps/site/src/lib/data/week-data.test.ts`
Module reason: `listWeekSummaries` sorts season and week numerically.
Test reason: The test crosses seasons and compares weeks 2 and 10.

T2 — Site picker

Prompt: After I select Change my team, keyboard focus must return to my selected team.
Module: `packages/analyzer/site/form/team-picker.tsx`
Test: `packages/analyzer/site/form/team-picker.test.tsx`
Module reason: The picker restores focus after its list opens.
Test reason: The test checks the selected radio after the Change button.

T3 — Pipeline roster projections

Prompt: The roster projection behind playoff odds must use current players, including additions after the scored week.
Module: `packages/week/python/src/week/sheet/base.py`
Test: `apps/pipeline/tests/test_sheet.py`
Module reason: `projected_totals` reads the current roster.
Test reason: The test adds one player and removes another after lineup lock.

T4 — Pipeline publish

Prompt: Publish one week without a commit of stray files or data from another season.
Module: `apps/pipeline/src/cornerstone/publish.py`
Test: `apps/pipeline/tests/test_rule_publish.py`
Module reason: `run_publish` constrains each commit to season paths.
Test reason: Tests cover stray files, other seasons, and files outside season folders.

T5 — API answer caps

Prompt: A team's daily answer allowance must reset tomorrow without a reset of another team's allowance today.
Module: `apps/api/src/cornerstone_api/caps.py`
Test: `apps/api/tests/test_caps.py`
Module reason: `Caps` counts answers by roster and local calendar day.
Test reason: The test separates yesterday's count from another team's count.

T6 — API grade limits

Prompt: The daily trade-grade limit must survive an API restart.
Module: `packages/analyzer/python/src/analyzer/ratelimit.py`
Test: `apps/api/tests/test_api.py`
Module reason: `GradeLimiter` saves daily counts.
Test reason: The test creates another app and checks that the next grade returns 429.

### Common procedure for cold agents

Give each agent this procedure and exactly one approved task prompt.

1. Start at the repository root.
2. Follow repository and external instructions, except for the trial exception below.
3. For this trial only, do not read `.scratch/` or `docs/agents/state.md`.
4. The trial exception suspends normal state and ticket reads.
5. Find the module that owns the requested behavior and its relevant test file.
6. Use at most ten distinct file reads.
7. Count partial reads, READMEs, and automatically loaded instruction files. Exclude automatic skill catalog metadata from this count; actual file reads and loaded instructions still count.
8. Count external files, including external instructions.
9. Count every file exposed by a content search.
10. Content-search results count even when they show only matching filenames.
11. Count each distinct file once.
12. Repeated reads add no further count.
13. Filename listings that enumerate pathnames without a content search cost no file reads.
14. The eleventh distinct file fails the run.
15. Return the chosen module path and test path.
16. Give a reason for each choice.
17. Return an ordered, complete file-read log.
18. Record evidence without a Test verdict.

### Auditor procedure

Run one fresh agent per task, for six runs total.
Use the same model and repository revision for all six.
Start every agent at the repository root.
Give no inherited history or expected answers.
Give only the approved task prompt and common procedure.
Other applicable instructions still apply and count toward file exposure.

Record the model, revision, start directory, task prompt, and common procedure for each run.
Record the full launch context and automatic context inventory.
Record all tool calls and returned content.
Preserve the agent's chosen paths, both reasons, and ordered read log.
Compare each log with the full tool trace and automatic context inventory.
Include instruction files that load without a tool call.
Count every file exposed by a content search, even when results show only matching filenames.
Only pathname enumeration without a content search counts as a free filename listing.
Preserve failed runs.

The auditor supplies evidence.
The Judge supplies Test verdicts.

## Tests

AT-1: Instruction entry links
App: site, pipeline, API
Stories: 1, 3, 5
Given: D1 through D3 at the implementation revision.
When: The reader follows their module-navigation instructions.
Then: Instructions provide the approved root-to-app entry links.
Evidence: Exact excerpts and resolved relative links from D1 to D4, D5, and D6, and D2/D3 to their app READMEs.
Evidence: Include D1's root instructions → app README → owner README → module and test navigation rule.

AT-2: App responsibility maps
App: site, pipeline, API
Stories: 2, 3, 7
Given: D4 through D6 and their roles in the approved document inventory.
When: The reader follows each app's responsibility map.
Then: Each app map separates its approved responsibilities and links their owners directly.
Evidence: Map excerpts, relative link targets, and target existence checks.
Evidence: Show site file loaders, app routes, and package parts, with data and analyzer owner links.
Evidence: Show pipeline build/publish orchestration versus domain packages, with cornerstone and week owner links.
Evidence: Show API HTTP composition, app state/limits, and analyzer routes, with their owner links.

AT-3: Owner destinations and boundaries
App: site, pipeline, API
Stories: 4, 5, 7
Given: D7 through D13 and the six approved module/test pairs.
When: The reader follows the owner maps for those six responsibilities.
Then: Each owner map places its module, responsibility, and relevant test together.
Evidence: Owner-map excerpts with resolved relative Markdown links to the real module and test files.
Evidence: Include analyzer's form-owner link and Python rate-limit owner with its API integration test.
Evidence: Include week's sheet-owner link and its boundary with the rankings odds engine.
Evidence: Include the API owner's distinction between answer caps and analyzer grade limits.
Evidence: Show the other owner under `Does not do` for responsibilities that belong elsewhere.

AT-4: Owner README shape
App: site, pipeline, API
Stories: 6
Given: The seven owner or module READMEs D7 through D13.
When: The reader checks their document shape.
Then: Every owner README meets the existing shape and 24-line rules.
Evidence: Numbered full contents and physical line totals for all seven documents, with blank lines included.
Evidence: Show a one-line title, then `Knows`, `Ports`, and `Does not do`, in that order.
Evidence: Show test pointers within those sections, without an extra test heading.
Evidence: Include D13 explicitly, because existing automated rules do not scan it.
Evidence: Include commands and output for the existing README rules, without test-code changes.
Evidence: Rule files are `apps/site/src/readme-rule.test.ts`, `apps/pipeline/tests/test_rule_readmes.py`, and `apps/api/tests/test_rule_api.py`.

AT-5: Existing document duties
App: site, pipeline, API
Stories: 16, 23
Given: The base and implementation versions of the approved documents.
When: The reader compares their existing responsibilities and instruction duties.
Then: Existing responsibilities and normal instruction duties remain intact.
Evidence: Before/after excerpts for revised responsibilities and instruction sections.
Evidence: Show that site and pipeline instructions retain their commands and rules.
Evidence: Show that normal work still requires state and ticket reads.
Evidence: Show that the trial exception applies only to cold-agent trials.

AT-6: API dependency statement
App: API
Stories: 14
Given: D1 and the API app README at the implementation revision.
When: The reader reads the API dependency statement in root instructions.
Then: Root instructions state that API product code imports no pipeline code.
Evidence: Exact root and API README excerpts, with the root diff.
Evidence: Distinguish shared README-rule test helpers from API product dependencies.

AT-7: Archive destination
App: site
Stories: 8, 22
Given: One fresh agent receives T1 under the common procedure.
When: The agent performs the archive navigation task.
Then: The agent identifies the approved archive module and test within ten distinct file reads.
Evidence: T1's actual prompt, both chosen paths, both reasons, ordered read log, full trace, automatic context inventory, and audit.
Evidence: Compare both choices and reasons with T1's expected answers above.

AT-8: Picker focus destination
App: site
Stories: 9, 22
Given: One fresh agent receives T2 under the common procedure.
When: The agent performs the picker navigation task.
Then: The agent identifies the approved picker module and test within ten distinct file reads.
Evidence: T2's actual prompt, both chosen paths, both reasons, ordered read log, full trace, automatic context inventory, and audit.
Evidence: Compare both choices and reasons with T2's expected answers above.

AT-9: Current-roster projection destination
App: pipeline
Stories: 10, 22
Given: One fresh agent receives T3 under the common procedure.
When: The agent performs the roster-projection navigation task.
Then: The agent identifies the approved projection module and test within ten distinct file reads.
Evidence: T3's actual prompt, both chosen paths, both reasons, ordered read log, full trace, automatic context inventory, and audit.
Evidence: Compare both choices and reasons with T3's expected answers above.

AT-10: Publish boundary destination
App: pipeline
Stories: 11, 22
Given: One fresh agent receives T4 under the common procedure.
When: The agent performs the publish navigation task.
Then: The agent identifies the approved publish module and test within ten distinct file reads.
Evidence: T4's actual prompt, both chosen paths, both reasons, ordered read log, full trace, automatic context inventory, and audit.
Evidence: Compare both choices and reasons with T4's expected answers above.

AT-11: Answer-cap destination
App: API
Stories: 12, 22
Given: One fresh agent receives T5 under the common procedure.
When: The agent performs the answer-cap navigation task.
Then: The agent identifies the approved answer-cap module and test within ten distinct file reads.
Evidence: T5's actual prompt, both chosen paths, both reasons, ordered read log, full trace, automatic context inventory, and audit.
Evidence: Compare both choices and reasons with T5's expected answers above.

AT-12: Persistent grade-limit destination
App: API
Stories: 13, 22
Given: One fresh agent receives T6 under the common procedure.
When: The agent performs the grade-limit navigation task.
Then: The agent identifies the approved grade-limit module and test within ten distinct file reads.
Evidence: T6's actual prompt, both chosen paths, both reasons, ordered read log, full trace, automatic context inventory, and audit.
Evidence: Compare both choices and reasons with T6's expected answers above.

AT-13: Cold trial conditions
App: site, pipeline, API
Stories: 17, 18
Given: The launch and context records for T1 through T6.
When: The auditor compares those records with the approved cold-start procedure.
Then: The six trials meet every approved cold-start condition.
Evidence: A six-run manifest with one fresh agent per task, one model, one revision, and repository-root start directories.
Evidence: Preserve each exact task prompt and the common procedure.
Evidence: Show no inherited history, expected answers, `.scratch/` content, or `docs/agents/state.md` content.
Evidence: Account for all other applicable repository and external instructions in each context inventory.

AT-14: Complete file exposure audit
App: site, pipeline, API
Stories: 19, 20
Given: All six ordered read logs, complete tool traces, and automatic context inventories.
When: The auditor reconciles each log with its trace and inventory.
Then: Each audited read log accounts for every exposed file under the approved count rules.
Evidence: Per-run ordered file inventories, trace references, automatic-load references, and final distinct-file totals.
Evidence: Count partial, README, instruction, external, and automatic file exposure.
Evidence: Count every file exposed by a content search, even when results show only matching filenames.
Evidence: Count repeated file reads once and pathname enumeration without a content search zero times.
Evidence: Identify any eleventh distinct file as a failed run, without a Test verdict.
Evidence: Explain every difference between an agent's log and the audited inventory.

AT-15: Failed evidence remains
App: site, pipeline, API
Stories: 21
Given: The complete trial manifest and recorded trial outputs.
When: The auditor checks the evidence archive against the manifest.
Then: Every failed run remains in the evidence record.
Evidence: Link every run to its full retained output, read log, trace, context inventory, and audit.
Evidence: Identify unsuccessful runs without their removal or replacement in the record.
Evidence: If no run fails, record that fact against the complete six-run manifest.
Evidence: This test requires no artificial failure or additional trial.

AT-16: Approved document scope
App: site, pipeline, API
Stories: 15
Given: The base-to-implementation product-document diff and approved inventory D1 through D13.
When: The reader reviews the scope of the documentation changes.
Then: Product-document changes stay within the 13 approved documents and six approved task routes.
Evidence: The full changed-file list and product-document diff, mapped to D1 through D13 and T1 through T6.
Evidence: Separate feature tracker and evidence records from product-document changes.

AT-17: No product or deferred-scope change
App: site, pipeline, API
Stories: none
Given: The full feature diff and historical ticket 07's state.
When: The reader checks the feature against the excluded scope.
Then: The feature introduces none of the listed out-of-scope changes.
Evidence: Full changed-file list and diff show no module move, code edit, test-code edit, schema change, or API contract change.
Evidence: Product documents contain no task-specific answer table or exhaustive package expansion.
Evidence: No root README or separate API instruction file appears.
Evidence: Deferred provider-refresh, saved-data, prompt-test, fact-selection, and build-behavior gaps remain outside the feature.
Evidence: Historical ticket 07 remains open.

## Trace

Story 1: AT-1
Story 2: AT-2
Story 3: AT-1, AT-2
Story 4: AT-3
Story 5: AT-1, AT-3
Story 6: AT-4
Story 7: AT-2, AT-3
Story 8: AT-7
Story 9: AT-8
Story 10: AT-9
Story 11: AT-10
Story 12: AT-11
Story 13: AT-12
Story 14: AT-6
Story 15: AT-16
Story 16: AT-5
Story 17: AT-13
Story 18: AT-13
Story 19: AT-14
Story 20: AT-14
Story 21: AT-15
Story 22: AT-7, AT-8, AT-9, AT-10, AT-11, AT-12
Story 23: AT-5, AT-13

No story lacks a test.

Out of scope "Module moves, code edits, test-code changes, and product behavior changes": AT-17
Out of scope "Documentation beyond the 13 approved documents or task paths beyond the six approved tasks": AT-16, AT-17
Out of scope "Exhaustive package coverage or task-specific answer tables in product documentation": AT-17
Out of scope "Historical ticket 07 gaps for provider refresh, saved data, prompt tests, fact selection, and build behavior": AT-17
Out of scope "Completion of historical ticket 07, which stays open": AT-17

## Revisions

None yet.
