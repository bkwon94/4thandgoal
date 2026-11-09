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
| `card-polish` | site | 01 Open card and GameCard | none | |
| `clients` | both | 01 the root workspaces and the API app | none | |
| `easter-eggs` | both | 01 one egg from the drop to the board | none | |
| `egg-polish` | site | 01 The crack starts at the tap point | none | must merge before the first egg drop on Tuesday, 2026-11-10 |
| `fast-cycle` | both | 07 the midseason tests share one build | PR #13 | `fast-cycle` merges after PR #13 |
| `faster-evidence` | both | 01 the rate limit setting and make api-evidence | none | |
| `jev` | pipeline | 01 the weekly build saves one Jev check per blurb | none | |
| `known-games` | pipeline | 08 the-site-renders-the-known-games-line | | |
| `matchup-impact` | pipeline | 01 the impact fact, without the odds | none | |
| `manager-brain` | both | 01 The chart cache trusts the PNG hash | none | |
| `manager-pages` | site | 01 the past week keeps every rostered player | none | |
| `manager-pages` | pipeline | 12 drop-awards-from-managers-entry | | |
| `midseason-report` | both | 15 the roast voice: one prose block per chapter | none | |
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
| `site-redesign` | site | 01 dark default and a light set for each client | none | |
| `site-speed` | site | 01 the teams prefetch and the skeleton | none | |
| `tone` | pipeline | 09 leftovers-after-the-second-rewrite | | |
| `transaction-history` | pipeline | 01 each build writes the full week before into the history | none | |
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

- `verdict` is not yet a required check on `main`, so nothing blocks the merge of a spec PR with a FAIL. Brian adds it in Settings, Rules: a ruleset for `main` with `verdict` required, and the Repository admin role on the bypass list, so `publish` can still push to `main`.
- Brian runs one `make publish` by hand under the hook before the week 9 publish.
