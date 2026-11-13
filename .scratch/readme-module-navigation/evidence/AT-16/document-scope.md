Implementation revision: `dad744db4f3b49732adc1586e08c34be2f381f73`.
Base revision: `17f45a15d1c324e36beefd0da29b77fe56b7ef91`.
All source excerpts below come from Git objects at the stated revision.
No behavior test or cold task runs during this static capture.

## Approved product inventory

| ID | Path | Route |
| --- | --- | --- |
| D1 | `CLAUDE.md` | root entry, all tasks |
| D2 | `apps/site/CLAUDE.md` | site entry, T1 and T2 |
| D3 | `apps/pipeline/CLAUDE.md` | pipeline entry, T3 and T4 |
| D4 | `apps/site/README.md` | site map, T1 and T2 |
| D5 | `apps/pipeline/README.md` | pipeline map, T3 and T4 |
| D6 | `apps/api/README.md` | API map, T5 and T6 |
| D7 | `apps/site/src/lib/data/README.md` | archive, T1 |
| D8 | `apps/pipeline/src/cornerstone/README.md` | publish, T4 |
| D9 | `apps/api/src/cornerstone_api/README.md` | answer caps, T5; grade boundary, T6 |
| D10 | `packages/analyzer/README.md` | form, T2; grade limits, T6 |
| D11 | `packages/analyzer/site/form/README.md` | picker, T2 |
| D12 | `packages/week/README.md` | sheet and odds boundary, T3 |
| D13 | `packages/week/python/src/week/sheet/README.md` | current roster, T3 |

## Complete changed-file list at fixed revision

```text
A	.scratch/readme-module-navigation/ACCEPTANCE.md
A	.scratch/readme-module-navigation/MAP.md
A	.scratch/readme-module-navigation/PRD.md
A	.scratch/readme-module-navigation/decisions/01-grill-representative-task-set.md
A	.scratch/readme-module-navigation/decisions/02-grill-readme-coverage-and-structure.md
A	.scratch/readme-module-navigation/decisions/03-grill-cold-agent-test-procedure.md
A	.scratch/readme-module-navigation/issues/01-connect-all-six-navigation-routes.md
A	.scratch/readme-module-navigation/issues/02-prove-all-six-routes-with-cold-agents.md
M	CLAUDE.md
A	apps/api/README.md
M	apps/api/src/cornerstone_api/README.md
M	apps/pipeline/CLAUDE.md
M	apps/pipeline/README.md
M	apps/pipeline/src/cornerstone/README.md
M	apps/site/CLAUDE.md
M	apps/site/README.md
M	apps/site/src/lib/data/README.md
M	docs/agents/state.md
M	packages/analyzer/README.md
M	packages/analyzer/site/form/README.md
M	packages/week/README.md
M	packages/week/python/src/week/sheet/README.md
```

## Classification

Product documents are exactly D1 through D13.
Feature tracker records are .scratch/readme-module-navigation/* and docs/agents/state.md.
Evidence records do not exist in the fixed implementation commit.
This capture adds only EVIDENCE.md and evidence/ beneath the feature tracker.
The full product diff is product.diff. The full feature diff is ../AT-17/feature.diff.
