# Cornerstone Weekly

This repo builds the weekly report site for the Cornerstone fantasy football league. The
data comes from Sleeper. The public site is at https://cpcfantasy.com/

## Commands

- `cornerstone build` builds the report for a week.
- `cornerstone publish` publishes the built site.
- `cornerstone rewrite --chapter <key>` rewrites one chapter.
- `cornerstone page-json` writes `page.json` for a saved week.

## Tuesday runbook

1. At 8:00 the launchd job builds the report and opens the page. The job is `com.briankwon.cornerstone-weekly`. Its log is `~/Library/Logs/cornerstone-weekly/build.log`.
2. Read the page.
3. Run `cornerstone rewrite --chapter <key>` for each chapter that needs a fix.
4. Run `cornerstone publish`.
5. Share the home page link: https://cpcfantasy.com/

## Page data for the site

The build writes `site/<season>/week-NN/page.json` next to `index.html`. The file holds the
render context that `week.html` reads, plus a `schema_version` key. The image paths in it are
relative to the week folder. `cornerstone publish` copies the whole week folder, so the file goes to
`public/<season>/week-NN/page.json` in the site repo, with the images beside it.

To write the file for a saved week, run `cornerstone page-json --season <S> --week <W>`. The
command reads the saved facts and blurbs. It makes no writer call and no network call.

Bump `PAGE_SCHEMA_VERSION` in `src/cornerstone/render.py` when a key changes meaning or leaves.
A new key does not need a bump.
