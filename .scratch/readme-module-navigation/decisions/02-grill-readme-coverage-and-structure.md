# 02: Which README structure and coverage guide an agent?

Map: `.scratch/readme-module-navigation/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

Which READMEs and agent instructions must connect the repo root to the modules and tests in the task set?
Brian chooses the precise coverage and the navigation structure across all three apps and relevant packages.
The choice includes the links, module responsibilities, test pointers, and README size limits that the spec requires.
Check the existing README rules and the source ticket before Brian decides which constraints apply.
Keep module moves and code changes outside this choice.

## Decision

Brian approves this route: root instructions, app README, owner README, then the module and its test.
The maps group responsibilities and name each owner. They do not repeat the six task answers as a lookup table.
Each owner README names the module, its responsibility, and its relevant test together, with relative Markdown links.

### Coverage

The scope covers these 13 documents and the six approved task routes from decision 01.

| Level | Document | Role |
| --- | --- | --- |
| Root | `CLAUDE.md` | Link all three app READMEs. State the navigation rule. Correct the claim that the API imports the pipeline. |
| App instructions | `apps/site/CLAUDE.md` | Point to the app README for module ownership. Keep commands and rules here. |
| App instructions | `apps/pipeline/CLAUDE.md` | Point to the app README for module ownership. Keep commands and rules here. |
| App | `apps/site/README.md` | Map file loaders, app routes, and package components. Link the data and analyzer READMEs. |
| App | `apps/pipeline/README.md` | Map build and publish orchestration versus domain packages. Link the cornerstone and week READMEs. |
| App | `apps/api/README.md` | Add this README. Map HTTP composition, app state and limits, and analyzer routes. Link their owner READMEs. |
| App module | `apps/site/src/lib/data/README.md` | Name `week-data.ts`, its archive responsibility, and its test. |
| App module | `apps/pipeline/src/cornerstone/README.md` | Name `publish.py`, its commit boundary, and its rule test. |
| App module | `apps/api/src/cornerstone_api/README.md` | Distinguish daily answer caps from analyzer grade limits. Name `caps.py` and its test. |
| Package | `packages/analyzer/README.md` | Link the form folder. Name the Python rate-limit module and its API integration test. |
| Package module | `packages/analyzer/site/form/README.md` | Name the team picker, its focus responsibility, and its test. |
| Package | `packages/week/README.md` | Link the sheet folder. Distinguish roster projections from the rankings odds engine. |
| Package module | `packages/week/python/src/week/sheet/README.md` | Name `projected_totals` in `base.py` and the pipeline sheet test. |

The root needs no README. The API needs no separate instruction file for these routes.
The app maps link directly to the relevant owner README, so an agent need not read every intermediate folder.
The existing instructions to read the state and the ticket remain in force.
Decision 03 records Brian's approved test-only exception to these reads for cold-agent trials.
Decision 03 sets the test procedure and the file-count rules.

### Structure and size

Each owner README keeps a one-line title, then `Knows`, `Ports`, and `Does not do`, in that order.
Test pointers sit within these sections. They add no extra heading.
`Does not do` names the other owner when a responsibility lies elsewhere.
Each owner or module README that this feature touches has at most 24 physical lines, with blank lines included.
This bound also applies to the week sheet README, beyond the current automated check's scope.
App READMEs gain concise navigation sections. They have no whole-file line cap.
Agent instructions keep their current role and gain the navigation links.

The current site and Python rules enforce a 24-line maximum for the package READMEs they cover.
The site rule covers package roots, direct package `site/` folders, and selected site source folders.
The Python rules cover app source folders with `__init__.py` and package roots.
The API reuses the Python README rules. These checks do not scan nested package Python folders.
Root and app READMEs have no current size cap.
The site rule permits `CLAUDE.md` at each app root, but not in deeper folders.

The cornerstone, cornerstone_api, analyzer, and analyzer/site/form READMEs already have 24 lines.
Their edits must fit within that bound without removal of unrelated responsibilities.
The API README says the API imports no pipeline code. The root instruction correction brings these statements into agreement.

### Deferred historical gaps

Brian keeps the remaining gaps from `.scratch/week-8-fixes/issues/07-the-readmes-name-the-module-an-agent-needs.md` separate and open.
These gaps cover provider refresh, saved data, prompt tests, fact selection, and build behavior.
They exceed the six approved task routes and need separate scope decisions.
The projection route covers one historical gap at its current package path.
This feature does not complete ticket 07.

Brian approves this coverage, structure, size policy, and deferral.
This decision changes no README, agent instruction, code, or test procedure.
