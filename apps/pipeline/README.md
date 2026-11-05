# Cornerstone Weekly

This repo builds the weekly report site for the Cornerstone fantasy football league. The
data comes from Sleeper. The public site of CPC is at https://cpc.4thandgoal.app/

## Commands

Each command that reads a league names its client with `--client <slug>`, such as `--client cpc`. A command with no
slug stops with a plain message. The client folder `clients/<slug>/` at the repo root holds `client.toml` and `data/`.

- `cornerstone build` builds the data of a week: `page.json` and the images.
- `cornerstone publish` copies the week folder to `clients/<slug>/published/` of this repo and pushes it.
- `cornerstone rewrite --chapter <key>` rewrites one chapter.
- `cornerstone page-json` writes `page.json` for a saved week.
- `cornerstone settings` prints the League settings of a season and each size that derives from them.
- `cornerstone check-client <folder>` checks the `client.toml` of a client folder and the exported schema.

## Setup

Run `prek install` one time per clone. The hook then runs `make check-fast` before each commit.
Each worktree reads its own branch's `.pre-commit-config.yaml`.

## Makefile

The `Makefile` holds the common tasks. Run `make help` to list them. A weekly run uses three targets:

1. `make build CLIENT=cpc WEEK=<W>` builds the week.
2. `make publish CLIENT=cpc WEEK=<W>` copies the week to `clients/cpc/published/` and pushes it.
3. `make push` pushes `main`. It stops if the branch is not `main` or the tree is not clean.

## Tuesday runbook

1. At 8:00 the launchd job builds the week and shows a notification. The job is `com.briankwon.cornerstone-weekly`. Its log is `~/Library/Logs/cornerstone-weekly/build.log`.
2. Read the week data, or the page after the site deploys.
3. Run `cornerstone rewrite --client cpc --chapter <key>` for each chapter that needs a fix.
4. Run `cornerstone publish --client cpc`.
5. Share the home page link: https://cpc.4thandgoal.app/

## Page data for the site

The build writes JSON and images only. It writes no HTML. The site repo renders the pages from
the JSON, including the home page.

The build writes `site/<season>/week-NN/page.json` with the images beside it. The file holds the
render context and a `schema_version` key. The image paths in it are relative to the week folder.
The default avatar and headshot paths point to `images/` under `apps/site/public/`, and the site repo serves
those files.

`cornerstone publish` copies the whole week folder to `clients/<slug>/published/<season>/week-NN/` in the
repo. It copies no `images/` folder and writes no `index.html`. The site repo reads `summary` from
each `page.json` to list the weeks on the home page.

To write the file for a saved week, run `cornerstone page-json --client <slug> --season <S> --week <W>`. The
command reads the saved facts and blurbs. It makes no writer call and no network call.

Bump `PAGE_SCHEMA_VERSION` in `src/cornerstone/render.py` when a key changes meaning or leaves.
A new key does not need a bump.

Schema version 2 removed the `asset_version` and `root` keys. Only the retired templates read them.
