# Where the work sits

One row for each feature under `.scratch/` with an open ticket. The next ticket is the lowest open
number. The close comment of a ticket updates this file in the same commit. `src/tracker-rule.test.ts`
keeps it true.

| Feature | Next ticket | Blocked by | Hold |
| --- | --- | --- | --- |
| `agent-habits` | 03 close the site tickets whose merge main proves | none | |
| `analyzer-multi-team` | 10 the headshot strip gap | none | |
| `manager-pages` | 01 the past week keeps every rostered player | none | |
| `modular` | 12 the fixtures carry every as-of key | none | |
| `one` | 04 one root check, one hook, and one CI file | none | 05 runs beside 04 |
| `next-week-byes` | 01 byes on the next-week games | the pipeline tracker | |
| `rankings` | 01 the reader and the route | none | |
| `site-foundation` | 01 the tiers and the page column | none | |
| `site-pages` | 01 the page shell | none | |
| `site-report` | 01 the type scale, the measure, and the cards | none | |
| `site-speed` | 01 the teams prefetch and the skeleton | none | |
| `waiver` | 01 the route behind the flag | pipeline 01 the week file | |
| `win-win` | 06 the shared API call hook | none | |

## Holds

- No one has installed the prek hook yet. After the week 8 page is live, run `pnpm hook:install` in the main checkout.
- Nothing uncommitted may sit on `main` at publish time, because the publish stages every file.
