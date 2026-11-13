# Where the work sits

One row for each feature under `.scratch/` with an open ticket. The next ticket is the lowest open
number. The close comment of a ticket updates this file in the same commit. Two rule tests keep it true:
`apps/site/src/tracker-rule.test.ts` and `apps/pipeline/tests/test_rule_tracker.py`.

The App column is `site`, `pipeline`, or `both`. A shared feature has a `site/` and a `pipeline/` subfolder.
It gets one row for each subfolder with an open ticket. The App of that row names the subfolder, and the
number in Next ticket is a ticket in `.scratch/<feature>/<app>/issues/`. So the row `waiver`, `pipeline`, 09
names `.scratch/waiver/pipeline/issues/09-*.md`. A feature with no subfolder has one row.

| Feature | App | Next ticket | Blocked by | Hold |
| --- | --- | --- | --- | --- |
| `manager-pages` | site | 11 the bench sentence and the odds change words | none | |
| `manager-pages` | pipeline | 12 drop-awards-from-managers-entry | | |
| `modular` | pipeline | 20 remove-the-chart-parameter-of-context | | |
| `quick-runs` | both | 01 the queue keeps Bugs and Quick Wins | none | |
| `site-pages` | site | 09 the home page test reads a class name | none | |
| `tone` | pipeline | 10 remove-names-is-case-sensitive | | |
| `week-8-fixes` | pipeline | 08 the-scoring-component-fact-names-the-component | | |

## Holds

- Brian runs one `make publish` by hand under the hook before the week 9 publish.
