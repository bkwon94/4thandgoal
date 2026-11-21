# Deadline week: approved rebuild diffs

The spec changes no value of the rebuild output on purpose.

Ticket 02 adds the keys `accepted` and `faab` to each trade in `facts.json` (AT-13, AT-14). The rebuild cannot diff `facts.json` today, because no week of cpc or norcal holds the saved inputs `verify.json`, `raw/nflverse.json`, `raw/slow_sources.json`, and `raw/news.json`. The rebuild diffs `page.json`, `topics.json`, and `waiver.json` only, and the new keys do not change them. The golden file `apps/pipeline/tests/fixtures/golden/facts.json` holds the new keys.

A list line here would fail the check with "listed but not changed". So the list is empty until a week holds the saved inputs.
