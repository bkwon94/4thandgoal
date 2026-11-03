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
| `agent-habits` | site | 03 close the site tickets whose merge main proves | none | |
| `analyzer-multi-team` | site | 10 the headshot strip gap | none | |
| `known-games` | pipeline | 08 the-site-renders-the-known-games-line | | |
| `manager-pages` | site | 01 the past week keeps every rostered player | none | |
| `manager-pages` | pipeline | 12 drop-awards-from-managers-entry | | |
| `modular` | site | 12 the fixtures carry every as-of key | none | |
| `modular` | pipeline | 20 remove-the-chart-parameter-of-context | | |
| `one` | both | 09 the build skills and the verdict rule | none | 09 is in-review until the first real spec PR runs `tdd`, `code-review`, and `cpc:review` |
| `next-week-byes` | site | 01 byes on the next-week games | the pipeline tracker | |
| `next-week-byes` | pipeline | 06 two-chapters-fell-to-templates-in-the-week-7-rebuild | | |
| `rankings` | site | 01 the reader and the route | none | |
| `rankings` | pipeline | 01 the-formula | | |
| `site-api` | pipeline | 10 prompt-caching | | |
| `site-foundation` | site | 01 the tiers and the page column | none | |
| `site-pages` | site | 01 the page shell | none | |
| `site-report` | site | 01 the type scale, the measure, and the cards | none | |
| `site-speed` | site | 01 the teams prefetch and the skeleton | none | |
| `tone` | pipeline | 09 leftovers-after-the-second-rewrite | | |
| `trade-grade-v3` | pipeline | 05 rebuild-week-6 | | Brian's review and the publish of week 6 |
| `waiver` | site | 01 the route behind the flag | pipeline 01 the week file | |
| `waiver` | pipeline | 09 usage-floor-for-ranked-buckets | | |
| `week-8-fixes` | pipeline | 07 the-readmes-name-the-module-an-agent-needs | | |
| `win-win` | site | 06 the shared API call hook | none | |

## Notes

- No merge on `main` proves known-games 08, so its Status stays open until Brian decides.
- `main` holds the merge of branch `tone-09`, but tone 09 reads ready-for-human, so Brian decides its Status.
- trade-grade-v3 05 may be done, because `main` holds the week 6 report, so Brian decides its Status.

## Holds

- Brian installs the prek hook after the week 8 page is live, with `prek install` in each main checkout.
- Brian runs one `make publish` by hand under the hook before the week 9 publish.
