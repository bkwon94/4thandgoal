# 01: Which tasks prove that agents find the right module?

Map: `.scratch/readme-module-navigation/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Which representative tasks, correct target modules, and relevant test files define success for site, pipeline, and API?
Brian chooses the task set and its breadth across relevant packages.
The spec needs expected answers with reasons, so the test measures the correct destination for each task.
Check candidate paths against the current repo before Brian decides.
The source ticket supplies candidate pipeline gaps, but it does not define the task set for all three apps.

## Decision

Brian approves these six tasks and their expected module and test paths.
The prompts contain no module paths, so each cold agent must find the owner.

| App | Cold-agent behavior prompt | Expected target module | Relevant test file | Reason |
| --- | --- | --- | --- | --- |
| Site | The week archive must put the newest season first, then order its weeks by number. | `apps/site/src/lib/data/week-data.ts` | `apps/site/src/lib/data/week-data.test.ts` | `listWeekSummaries` sorts season and week numerically. The test crosses seasons and compares weeks 2 and 10. |
| Site | After I select Change my team, keyboard focus must return to my selected team. | `packages/analyzer/site/form/team-picker.tsx` | `packages/analyzer/site/form/team-picker.test.tsx` | The picker restores focus after its list opens. The test checks the selected radio after the Change button. |
| Pipeline | The roster projection behind playoff odds must use current players, including additions after the scored week. | `packages/week/python/src/week/sheet/base.py` | `apps/pipeline/tests/test_sheet.py` | `projected_totals` reads the current roster. The test adds one player and removes another after lineup lock. |
| Pipeline | Publish one week without a commit of stray files or data from another season. | `apps/pipeline/src/cornerstone/publish.py` | `apps/pipeline/tests/test_rule_publish.py` | `run_publish` constrains each commit to season paths. Tests cover stray files, other seasons, and files outside season folders. |
| API | A team's daily answer allowance must reset tomorrow without a reset of another team's allowance today. | `apps/api/src/cornerstone_api/caps.py` | `apps/api/tests/test_caps.py` | `Caps` counts answers by roster and local calendar day. The test separates yesterday's count from another team's count. |
| API | The daily trade-grade limit must survive an API restart. | `packages/analyzer/python/src/analyzer/ratelimit.py` | `apps/api/tests/test_api.py` | `GradeLimiter` saves daily counts. The test creates another app and checks that the next grade returns 429. |

The task set has two tasks per app: one app-owned module and one package-owned module.
It covers data reads, interaction, publish boundaries, calculations, account limits, and saved state.
This set gives representative coverage; it does not cover every package.
Provider refresh rules, prompt rules, and saved-data layout fall outside this sample.

The projection task covers a historical gap from ticket 07.
Its current owner is the `week` package, at the path above.
The old app-local `sheet/base.py` path no longer exists.
Current source and tests confirm all six module and test pairs.

Brian approves the task set and its breadth.
Decision 02 still sets precise README coverage and structure.
Decision 03 still sets the cold-agent test procedure.
This decision adds no procedure choices.
