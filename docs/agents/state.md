# Where the work sits

One row for each feature under `.scratch/` with an open ticket. The close comment of a ticket updates its row.

| Feature | Next ticket | Blocked by | Hold |
| --- | --- | --- | --- |
| week-8-fixes | 01 the-odds-replace-an-injured-starter | | page unpublished until 01 to 05 land |
| agent-habits | 03 a-deploy-step-for-the-fly-api-behind-the-check-and-an-approval | | Brian decides: approve each deploy by hand, or deploy on each green push |
| known-games | 08 the-site-renders-the-known-games-line | | |
| manager-pages | 12 drop-awards-from-managers-entry | | |
| modular | 20 remove-the-chart-parameter-of-context | | |
| next-week-byes | 06 two-chapters-fell-to-templates-in-the-week-7-rebuild | | |
| tone | 09 leftovers-after-the-second-rewrite | | |
| trade-grade-v3 | 05 rebuild-week-6 | | Brian's review and the publish of week 6 |
| waiver | 09 usage-floor-for-ranked-buckets | | |

## Notes

- No merge on `main` proves known-games 08, so its Status stays open until Brian decides.
- `main` holds the merge of branch `tone-09`, but tone 09 reads ready-for-human, so Brian decides its Status.
- trade-grade-v3 05 may be done, because `main` holds the week 6 report, so Brian decides its Status.

## Holds

- Brian installs the prek hook after the week 8 page is live, with `prek install` in each main checkout.
- Brian runs one `make publish` by hand under the hook before the week 9 publish.
