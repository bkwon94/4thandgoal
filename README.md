# Cornerstone Weekly

This repo builds the weekly report site for the Cornerstone fantasy football league. The
data comes from Sleeper. The public site is at https://cpcfantasy.com/

## Commands

- `cornerstone build` builds the data of a week: `page.json` and the images.
- `cornerstone publish` copies the week folder to the site repo and pushes it.
- `cornerstone rewrite --chapter <key>` rewrites one chapter.
- `cornerstone page-json` writes `page.json` for a saved week.

## Tuesday runbook

1. At 8:00 the launchd job builds the week and shows a notification. The job is `com.briankwon.cornerstone-weekly`. Its log is `~/Library/Logs/cornerstone-weekly/build.log`.
2. Read the week data, or the page after the site repo deploys.
3. Run `cornerstone rewrite --chapter <key>` for each chapter that needs a fix.
4. Run `cornerstone publish`.
5. Share the home page link: https://cpcfantasy.com/

## Page data for the site

The build writes JSON and images only. It writes no HTML. The site repo renders the pages from
the JSON, including the home page.

The build writes `site/<season>/week-NN/page.json` with the images beside it. The file holds the
render context and a `schema_version` key. The image paths in it are relative to the week folder.
The default avatar and headshot paths point to `static/` at the site root, and the site repo serves
those files.

`cornerstone publish` copies the whole week folder to `public/<season>/week-NN/` in the site
repo. It copies no `static/` folder and writes no `index.html`. The site repo reads `summary` from
each `page.json` to list the weeks on the home page.

To write the file for a saved week, run `cornerstone page-json --season <S> --week <W>`. The
command reads the saved facts and blurbs. It makes no writer call and no network call.

Bump `PAGE_SCHEMA_VERSION` in `src/cornerstone/render.py` when a key changes meaning or leaves.
A new key does not need a bump.

Schema version 2 removed the `asset_version` and `root` keys. Only the retired templates read them.
