# Clients: evidence

Spec: `.scratch/clients/PRD.md`. Acceptance tests: `.scratch/clients/ACCEPTANCE.md`.
Built from: `c5634be`, on 2026-11-04. The agent gives no Test verdict. Brian gives one for each test.

Notes on the method:

- Each site shot is a full-page shot from `agent-browser`, at a viewport of 375, 768, or 1280 by 900 px. Before each shot, a script scrolls the page to the end and back, so each chapter with a reveal shows.
- A `<w>-light.png` file has no stored theme. A `<w>-dark.png` file has `cpc.theme` set to `dark` in local storage, the key of `packages/design/site/lib/theme.ts`.
- NorCal has one dark set and no theme button, so it paints dark in both files of each width. Each NorCal `light` file shows the page with no stored theme.
- A `local` folder holds shots of the export of `CLIENT=<slug> pnpm --dir apps/site build`, served at `http://localhost:4173`. A `live` folder holds shots of `https://cpc.4thandgoal.app` or `https://norcal.4thandgoal.app`, taken on 2026-11-04 after the deploy of the `clients` code.
- A `local-api` folder holds shots of an export built with `NEXT_PUBLIC_API_URL=http://localhost:18080`, against the local API image of AT-27. The passphrase is `localtest`, and two teams are picked.
- The NFL cache `data/nfl/cache/` came from `apps/pipeline/data/cache/` of the main checkout. The CPC charts went under `charts/1QB0.5PPR4pt/`. The cache is git-ignored.
- No command called Claude. After each pipeline command, `git status --short` showed no change to a tracked file.

## AT-1: The CPC week 8 rebuild matches the published week

App: pipeline
Then: the diff of each rebuilt published file against the published file is empty, except the removed key `is_brian` in each team of `page.json`.
Files: `evidence/AT-1/full.diff`, `evidence/AT-1/output.txt`
Observation: `make -C apps/pipeline page-json CLIENT=cpc WEEK=8` exited 0 and wrote `clients/cpc/build/2026/week-08/page.json`. Against the week 8 files of `main` at `003c70c`, only `page.json` differs, and each of its 66 changed lines is an `is_brian` line. With `is_brian` removed from the old file, the diff is empty. `waiver.json` and each image are the same. The rebuild is byte-identical to the tracked build file, so `git status` stayed clean. The tracked `clients/cpc/published/2026/week-08/page.json` still holds `is_brian`, because no publish ran since the move.

## AT-2: The CPC sizes derive from the provider

App: pipeline
Then: each derived value equals the old League config value.
Files: `evidence/AT-2/old-config.txt`, `evidence/AT-2/output.txt`, `evidence/AT-2/table.md`
Observation: `make -C apps/pipeline settings CLIENT=cpc` printed the League settings of cpc for 2026. `table.md` lists 19 values. Each derived value equals the value in `config.py` at `003c70c`. The output also shows `reception_points: 0.5`, `points_key: pts_half_ppr`, and `median_game: True`.

## AT-3: The CPC week 8 page looks the same after the move

App: site
Then: each screenshot matches its screenshot from before the move in a side-by-side look check.
Files: `evidence/AT-3/compare.txt`, `evidence/AT-3/before/build-main.txt`, `evidence/AT-3/before/375-light.png`, `evidence/AT-3/before/375-dark.png`, `evidence/AT-3/before/768-light.png`, `evidence/AT-3/before/768-dark.png`, `evidence/AT-3/before/1280-light.png`, `evidence/AT-3/before/1280-dark.png`, `evidence/AT-3/live/375-light.png`, `evidence/AT-3/live/375-dark.png`, `evidence/AT-3/live/768-light.png`, `evidence/AT-3/live/768-dark.png`, `evidence/AT-3/live/1280-light.png`, `evidence/AT-3/live/1280-dark.png`, `evidence/AT-3/local/375-light.png`, `evidence/AT-3/local/375-dark.png`, `evidence/AT-3/local/768-light.png`, `evidence/AT-3/local/768-dark.png`, `evidence/AT-3/local/1280-light.png`, `evidence/AT-3/local/1280-dark.png`
Observation: The `before` shots are not of `https://cpcfantasy.com`, because that host now answers 301 to the new host. They are of the export of `main` at `003c70c`, built in the main checkout with `pnpm --dir apps/site build` (see `before/build-main.txt`) and served locally. Each `local` shot has 0 changed pixels against its `before` shot, at the same height, in all six pairs (`compare.txt`). Each `live` shot of `https://cpc.4thandgoal.app/2026/week-08/` has the same height as its pair, and about 7,510 pixels differ. The changed pixels sit only inside the small round team avatars of the matchups, the median game, and the standings. Each avatar file on the live host is byte-identical to the local file, and to the eye the avatars look the same.

## AT-4: An old CPC link redirects to the new host

App: site
Then: the answer is a 301 with `location: https://cpc.4thandgoal.app/2026/week-08/`.
Files: `evidence/AT-4/output.txt`
Observation: The Redirect Rule is a manual step of Brian, and it is live now. `curl -sI https://cpcfantasy.com/2026/week-08/` answered `HTTP/2 301` with `location: https://cpc.4thandgoal.app/2026/week-08/`. `curl -sI 'https://cpcfantasy.com/analyze/?x=1'` answered `HTTP/2 301` with `location: https://cpc.4thandgoal.app/analyze/?x=1`, so the query string stays.

## AT-5: CPC keeps the theme button and paints light first

App: site
Then: the page paints light and shows the theme button.
Files: `evidence/AT-5/live/theme-state.txt`, `evidence/AT-5/live/375-light.png`, `evidence/AT-5/live/375-dark.png`, `evidence/AT-5/live/768-light.png`, `evidence/AT-5/live/768-dark.png`, `evidence/AT-5/live/1280-light.png`, `evidence/AT-5/live/1280-dark.png`, `evidence/AT-5/local/theme-state.txt`, `evidence/AT-5/local/375-light.png`, `evidence/AT-5/local/375-dark.png`, `evidence/AT-5/local/768-light.png`, `evidence/AT-5/local/768-dark.png`, `evidence/AT-5/local/1280-light.png`, `evidence/AT-5/local/1280-dark.png`
Observation: With no stored theme, the root has no `dark` class, `cpc.theme` is null, and the page shows one "Switch to dark theme" button at each width, in the local export and on the live host (`theme-state.txt`). The `light` shots show the light page. A press of the button sets the class `dark` and stores `dark`, and each `dark` shot shows the dark page. The local and live shots have the same height at each width.

## AT-6: The CPC export omits the waiver board

App: site
Then: the export has no `/waiver/` route, and no JS file in the export holds waiver code.
Files: `evidence/AT-6/build.txt`, `evidence/AT-6/output.txt`
Observation: `CLIENT=cpc pnpm --dir apps/site build` exited 0. The export holds 10 HTML pages under `/`, `/2026/week-06/` to `/2026/week-08/`, `/2026/managers/`, `/analyze/`, and `/rankings/`, and no `waiver` folder. A search of the export JS for "War chest", `WarChest`, `DriftField`, `TeamPick`, `drift-field`, and `waiver.json` found no match. `check:export` passed and says the client cpc omits waiver.

## AT-7: The CPC Trade Analyzer has no finder

App: site
Then: the page shows no finder.
Files: `evidence/AT-7/build-with-local-api.txt`, `evidence/AT-7/local-api-state.txt`, `evidence/AT-7/live/375-light.png`, `evidence/AT-7/live/375-dark.png`, `evidence/AT-7/live/768-light.png`, `evidence/AT-7/live/768-dark.png`, `evidence/AT-7/live/1280-light.png`, `evidence/AT-7/live/1280-dark.png`, `evidence/AT-7/local/375-light.png`, `evidence/AT-7/local/375-dark.png`, `evidence/AT-7/local/768-light.png`, `evidence/AT-7/local/768-dark.png`, `evidence/AT-7/local/1280-light.png`, `evidence/AT-7/local/1280-dark.png`, `evidence/AT-7/local-api/375-light.png`, `evidence/AT-7/local-api/375-dark.png`, `evidence/AT-7/local-api/768-light.png`, `evidence/AT-7/local-api/768-dark.png`, `evidence/AT-7/local-api/1280-light.png`, `evidence/AT-7/local-api/1280-dark.png`
Observation: The static `/analyze/` page of cpc holds `finderOn: false`, locally and on the live host. The `local-api` shots show the form with two teams picked, "The Blue Tent" and "Lil Fridge", and no "Find a Trade" region at any width. The `local` shots show the form with "Pick a Team" and no finder, because the browser kept the passphrase of the earlier run. The `live` shots show the "League passphrase" box over a blurred page. The live analyzer fails until the merge, because the live API runs the old code, so the live pick of two teams is pending.

## AT-8: No old color name remains in the source

App: site
Then: the search finds no match.
Files: `evidence/AT-8/output.txt`
Observation: `grep -rnE '[a-z]-(red|blk|gry|wht)\b|--color-(red|blk|gry|wht)\b'` over `apps/site` and `packages/*/site`, with no `node_modules`, `.next`, `out`, or `public`, printed nothing and exited 1.

## AT-9: NorCal has its own brand and site name

App: site
Then: the masthead shows "NorCal Apex 6" as text, on the dark NorCal brand.
Files: `evidence/AT-9/build.txt`, `evidence/AT-9/compare.txt`, `evidence/AT-9/live/375-light.png`, `evidence/AT-9/live/375-dark.png`, `evidence/AT-9/live/768-light.png`, `evidence/AT-9/live/768-dark.png`, `evidence/AT-9/live/1280-light.png`, `evidence/AT-9/live/1280-dark.png`, `evidence/AT-9/local/375-light.png`, `evidence/AT-9/local/375-dark.png`, `evidence/AT-9/local/768-light.png`, `evidence/AT-9/local/768-dark.png`, `evidence/AT-9/local/1280-light.png`, `evidence/AT-9/local/1280-dark.png`
Observation: `CLIENT=norcal pnpm --dir apps/site build` exited 0, and `check:export` passed with "the pages show "NorCal Apex 6"". Each shot shows the masthead text "NORCAL APEX 6" over "LEAGUE WEEKLY", with no logo image, on a near-black page with gold and orange accents. The page paints dark with and without a stored theme. Each live shot has 0 changed pixels against its local shot (`compare.txt`).

## AT-10: NorCal has no theme button

App: site
Then: no theme button shows at any width.
Files: `evidence/AT-10/compare.txt`, `evidence/AT-10/live/375-light.png`, `evidence/AT-10/live/375-dark.png`, `evidence/AT-10/live/768-light.png`, `evidence/AT-10/live/768-dark.png`, `evidence/AT-10/live/1280-light.png`, `evidence/AT-10/live/1280-dark.png`, `evidence/AT-10/local/375-light.png`, `evidence/AT-10/local/375-dark.png`, `evidence/AT-10/local/768-light.png`, `evidence/AT-10/local/768-dark.png`, `evidence/AT-10/local/1280-light.png`, `evidence/AT-10/local/1280-dark.png`
Observation: The masthead shows no theme button and no menu button at 375, 768, or 1280 px. At 375 and 1280 px the root has the class `dark`, and the page holds 0 buttons with "theme" in the label. Each live shot has 0 changed pixels against its local shot.

## AT-11: The NorCal week has no Median Game chapter

App: both
Then: `page.json` has no Median Game chapter, and the page shows none.
Files: `evidence/AT-11/chapters.txt`, `evidence/AT-11/output.txt`, `evidence/AT-11/local/375-light.png`, `evidence/AT-11/local/375-dark.png`, `evidence/AT-11/local/768-light.png`, `evidence/AT-11/local/768-dark.png`, `evidence/AT-11/local/1280-light.png`, `evidence/AT-11/local/1280-dark.png`
Observation: `make -C apps/pipeline page-json CLIENT=norcal WEEK=8` exited 0. In the rebuilt and the published `page.json`, `median` is `null`. The two files differ only in the image paths, because the rebuild had no image folder. The chapter rail shows Matchup of the Week, Game Changer, Awards, Position Leaders, Trades, All Matchups, Standings, and Next Week, with no Median Game. The rebuild output went away after the run.

## AT-12: The NorCal standings count one game a week

App: both
Then: the wins and the losses of each team add up to 8.
Files: `evidence/AT-12/fields.txt`, `evidence/AT-12/local/375-light.png`, `evidence/AT-12/local/375-dark.png`, `evidence/AT-12/local/768-light.png`, `evidence/AT-12/local/768-dark.png`, `evidence/AT-12/local/1280-light.png`, `evidence/AT-12/local/1280-dark.png`
Observation: In the rebuilt and the published `page.json`, each of the 12 teams has wins plus losses of 8, from Mitseeker5000 at 6-2 to The Dart Side at 2-6. The last week of `rankings.json` gives the same sums. The standings shots show the same 12 records. Under the table, each shot shows the note "Records include the weekly median game: every team plays its opponent and the league median each week."

## AT-13: NorCal has no DEF

App: both
Then: the pool and the leaders in `page.json` and on the page hold no DEF.
Files: `evidence/AT-13/fields.txt`, `evidence/AT-13/local/375-light.png`, `evidence/AT-13/local/375-dark.png`, `evidence/AT-13/local/768-light.png`, `evidence/AT-13/local/768-dark.png`, `evidence/AT-13/local/1280-light.png`, `evidence/AT-13/local/1280-dark.png`
Observation: The leaders of the rebuilt and the published `page.json` are QB, RB, WR, and TE. Each `position` value in `page.json` and `waiver.json` is QB, RB, TE, or WR. `"DEF"` is in none of `page.json`, `waiver.json`, `rankings.json`, or `managers.json`. The raw league has no DEF slot. The Position Leaders shots show four boxes: QB, RB, WR, and TE.

## AT-14: The NorCal projections use full PPR

App: pipeline
Then: the projection of one named WR on a NorCal roster equals his Sleeper `pts_ppr` value for week 8.
Files: `evidence/AT-14/committed.txt`, `evidence/AT-14/rebuild.txt`
Observation: Tee Higgins, WR, player `6801`, is on roster 4, The Mean Machine. His projection is 15.97 in the published and the rebuilt `page.json`. His raw Sleeper week 8 projection has `pts_ppr` 15.97 and `pts_half_ppr` 13.67. The raw league has `rec` 1.0.

## AT-15: The NorCal Trade Analyzer has the finder

App: site
Then: the page shows the finder.
Files: `evidence/AT-15/build-with-local-api.txt`, `evidence/AT-15/compare.txt`, `evidence/AT-15/local-api-state.txt`, `evidence/AT-15/live/375-light.png`, `evidence/AT-15/live/375-dark.png`, `evidence/AT-15/live/768-light.png`, `evidence/AT-15/live/768-dark.png`, `evidence/AT-15/live/1280-light.png`, `evidence/AT-15/live/1280-dark.png`, `evidence/AT-15/local/375-light.png`, `evidence/AT-15/local/375-dark.png`, `evidence/AT-15/local/768-light.png`, `evidence/AT-15/local/768-dark.png`, `evidence/AT-15/local/1280-light.png`, `evidence/AT-15/local/1280-dark.png`, `evidence/AT-15/local-api/375-light.png`, `evidence/AT-15/local-api/375-dark.png`, `evidence/AT-15/local-api/768-light.png`, `evidence/AT-15/local-api/768-dark.png`, `evidence/AT-15/local-api/1280-light.png`, `evidence/AT-15/local-api/1280-dark.png`
Observation: The static `/analyze/` page of norcal holds `finderOn: true`, locally and on the live host. The `local-api` shots show "puurdygood" and a second team picked, then a "Find a Trade" region with a list of trade partners and a "Find a Trade" button, at each width. The `local` and `live` shots show the "League passphrase" box, and each live shot has 0 changed pixels against its local shot. The live analyzer fails until the merge, because the live API runs the old code, so the live finder is pending.

## AT-16: The NorCal menu is a bar

App: site
Then: the menu shows as a bar, with Home first and then the items in the order of the package list.
Files: `evidence/AT-16/compare.txt`, `evidence/AT-16/live/375-light.png`, `evidence/AT-16/live/375-dark.png`, `evidence/AT-16/live/768-light.png`, `evidence/AT-16/live/768-dark.png`, `evidence/AT-16/live/1280-light.png`, `evidence/AT-16/live/1280-dark.png`, `evidence/AT-16/local/375-light.png`, `evidence/AT-16/local/375-dark.png`, `evidence/AT-16/local/768-light.png`, `evidence/AT-16/local/768-dark.png`, `evidence/AT-16/local/1280-light.png`, `evidence/AT-16/local/1280-dark.png`
Observation: The masthead holds a row of links: Home, Week 8, Power Rankings, Managers, and Trade Analyzer, with no menu button. At 375 px the row wraps, and Trade Analyzer goes to a second line. Each live shot has 0 changed pixels against its local shot.

## AT-17: Each text pair of each brand passes WCAG AA

App: site
Then: the output lists each text pair of each set of `cpc` and `norcal` with a ratio of 4.5 or more.
Files: `evidence/AT-17/output.txt`
Observation: The contrast test passed 4 tests and printed 66 lines: 22 pairs for each of cpc light, cpc dark, and norcal dark. The lowest ratio is 4.56, `norcal dark: on_dark on accent`. The next is 4.57, `cpc dark: on_dark_muted on chip_dark`.

## AT-18: A site build with no `CLIENT` fails

App: site
Then: the build exits non-zero with a message that names `CLIENT`.
Files: `evidence/AT-18/output.txt`
Observation: `env -u CLIENT pnpm build` in `apps/site/` exited 1 with "client build failed: Set CLIENT to the slug of one folder under clients/. Example: CLIENT=cpc pnpm build".

## AT-19: A pipeline build with no client fails

App: pipeline
Then: the command exits non-zero with a message that names the client slug.
Files: `evidence/AT-19/output.txt`
Observation: `env -u CLIENT make -C apps/pipeline build WEEK=8` exited 2 with "Set CLIENT, the client slug. Example: make build CLIENT=cpc WEEK=8".

## AT-20: An unknown key in `client.toml` fails the check

App: both
Then: each check fails with a message that names `finderr` and the file.
Files: `evidence/AT-20/output.txt`
Observation: A temp copy of `clients/cpc/` has `finderr = true` under `[values.analyzer]`. The site build with `CLIENT_ROOT` set to the copy exited 1. The pipeline `check-client` exited 2. Each printed the full path of the copied `client.toml` and "- values.analyzer.finderr: is not a known key".

## AT-21: A menu item for an omitted package fails the check

App: both
Then: each check fails with a message that names the menu item and `waiver`.
Files: `evidence/AT-21/output.txt`
Observation: A temp copy of `clients/cpc/` has the menu item `{ package = "waiver" }`. The site build exited 1 with "menu.items: The menu item for waiver names a package that is not in the package list." The pipeline `check-client` exited 2 with the same sentence. Each message names the copied file.

## AT-22: A stale exported schema fails the check

App: both
Then: the check fails with a message that names the stale schema file of `analyzer`.
Files: `evidence/AT-22/output.txt`
Observation: The edit added `finder_limit: int = 5` to `AnalyzerValues`, with no new export. `make -C apps/pipeline rules`, the rule tests that the pipeline part of `make check` runs, failed 1 of 47 tests with "The schema file .../packages/analyzer/python/src/analyzer/values.schema.json of analyzer is stale." `check-client` on `clients/cpc` exited 2 with the same message. `git restore` put the file back. The full `make check BASE=main` of AT-24 ran on the clean tree and exited 0.

## AT-23: A client with only `week` builds a week with no rankings

App: site
Then: the export has a week page with no rankings chapter, and no rankings route.
Files: `evidence/AT-23/output.txt`
Observation: A test client `solo` in a temp root has `packages = ["week"]`, the NorCal brand and copy, and the NorCal week 8 data. Its build exited 0 with the routes `/`, `/_not-found`, `/2026/week-08`, and `/404`. The export has no `rankings` folder. The week page has the sections motw, game-changer, awards, leaders, trades, matchups, standings, and next-week. The home page shows only "Weekly Reports", and no page holds "Power Rankings".

## AT-24: The full check builds each client

App: both
Then: the output shows a site build of `cpc` and a site build of `norcal`, each with success.
Files: `evidence/AT-24/build-lines.txt`, `evidence/AT-24/output.txt`
Observation: `make check BASE=main` ran in 7 min 59 s and exited 0. Its output has "==> site build: cpc" with "Compiled successfully", then a passed `check:export` of cpc. It has "==> site build: norcal" with "Compiled successfully", then a passed `check:export` of norcal. Then the pipeline, the API, and each package passed.

## AT-25: The generated site files stay out of git

App: site
Then: `git status --short` prints nothing.
Files: `evidence/AT-25/output.txt`
Observation: After `CLIENT=cpc pnpm --dir apps/site build`, `git status --short` printed only `?? .scratch/clients/evidence/`, the folder of this pass. The same command with that folder left out printed nothing. `git check-ignore` shows the rules for `apps/site/out`, `apps/site/public/2026`, and `data/nfl/cache`.

## AT-26: The publish stages only the data of the client

App: pipeline
Then: `git diff --cached --name-only` lists only paths under `clients/cpc/published/2026/`, `clients/cpc/data/2026/`, and `clients/cpc/build/2026/`.
Files: `evidence/AT-26/output.txt`
Observation: The run used a temp clone of `clients` at `c5634be`. A script ran `run_publish` with `push=False`, and it replaced each commit with a print of the stage. At the "Week 8 report" point the stage was empty, because the build and the data folders had no change. At the "Week 8" point the stage held only `clients/cpc/published/2026/week-08/page.json`. The clone kept `c5634be` as its last commit, and the Spec branch got no commit.

## AT-27: The API serves each client by its path

App: pipeline
Then: the first answer lists each NorCal team, 12 by assumption, and the second lists each CPC team.
Files: `evidence/AT-27/container.txt`, `evidence/AT-27/cpc-teams.txt`, `evidence/AT-27/image.txt`, `evidence/AT-27/norcal-teams.txt`, `evidence/AT-27/run.txt`
Observation: This ran on a local image, `make -C apps/api image`, on port 18080, and the live call comes after the merge. The run also set `CORNERSTONE_ALLOWED_ORIGINS=http://localhost:4173` for the analyzer shots. `/clients/norcal/teams?season=2026` answered 200 with 12 teams, from puurdygood to The Dart Side. `/clients/cpc/teams?season=2026` answered 200 with 12 teams, from The Blue Tent to Teehee. The real NorCal team count is 12. A first cpc call hit 429 from the limit of 10 calls a minute, and a call after the wait answered 200.

## AT-28: The old API path answers as CPC

App: pipeline
Then: the answer lists each CPC team.
Files: `evidence/AT-28/live-old.txt`, `evidence/AT-28/local-new.txt`
Observation: Live, `https://api.cpcfantasy.com/teams` answered `HTTP/2 401` with no body, with and without `season=2026`, because the call had no passphrase and the agent has no live passphrase. On the local image, `/teams?season=2026` with the passphrase answered 200 with the same 12 CPC teams as `/clients/cpc/teams`, and with no passphrase it answered 401. The live call with a passphrase is pending.

## AT-29: The rate limit of the grades counts per client

App: pipeline
Then: the `cpc` grade past the limit answers 429, and the `norcal` grade answers 200.
Files: `evidence/AT-29/output.txt`
Observation: The API tests ran with `GRADES_PER_MINUTE = 5`. `test_the_grade_limit_counts_per_client_and_per_address` passed: five cpc grades get 200, the sixth gets 429, the old path `/analyze` gets 429, and a grade of the second client gets 200. Two more grade limit tests passed. No real start sent grades, because a grade calls Claude.

## AT-30: A bad `client.toml` stops the API at start

App: pipeline
Then: the start exits non-zero with a message that names the file and `timezone`.
Files: `evidence/AT-30/output.txt`
Observation: A temp copy of `clients/` has no `timezone` line in `norcal/client.toml`. `uvicorn --factory cornerstone_api.app:app_from_env` over that copy exited 1 with `league.client.ClientError`, the full path of the copied `client.toml`, and "- timezone: is required".

## AT-31: An undeclared import between packages fails the check

App: pipeline
Then: the check fails with `ModuleNotFoundError` for `waiver`.
Files: `evidence/AT-31/output.txt`
Observation: A temp test `apps/api/tests/test_import_waiver.py` imports `waiver`. `uv run --exact --package cpc-api pytest` on it exited 2 with "ModuleNotFoundError: No module named 'waiver'". The temp test went away after the run.

## AT-32: A change in one language checks both languages of the package

App: both
Then: the check runs the Python of `waiver`, the site side `@cpc/waiver`, and each package and app that depends on `waiver`.
Files: `evidence/AT-32/diff.txt`, `evidence/AT-32/output.txt`
Observation: The diff adds one trailing space to line 3 of `packages/waiver/python/src/waiver/price.py`. `scripts/changed_apps.py HEAD` printed `site pipeline api waiver`. `make check-fast BASE=HEAD` exited 0 and ran the scripts, the site with 663 tests that hold the `@cpc/waiver` tests, the pipeline, the API, and `packages/waiver`. The API is in the list because its dev group lists the pipeline, which needs `waiver`. `git restore` put the file back.

## AT-33: A client folder holds no code

App: both
Then: the search finds no file.
Files: `evidence/AT-33/output.txt`
Observation: `find clients -type f` for `.py`, `.ts`, `.tsx`, `.js`, and `.mjs` printed nothing, and its count is 0.

## AT-34: Each client has its own passphrase

App: pipeline
Then: the call with the wrong passphrase gets 401, the call with the right one passes, and the start with a missing passphrase exits non-zero and names the env value.
Files: `evidence/AT-34/output.txt`, `evidence/AT-34/real-start.txt`
Observation: Six passphrase tests of the API passed, with `test_each_client_checks_its_own_passphrase` among them. A real local start with `CORNERSTONE_PASSPHRASE_CPC=cpc-local` and `CORNERSTONE_PASSPHRASE_NORCAL=norcal-local` answered 401 for each `teams` call with the passphrase of the other client, and 200 for each call with its own. A start with no `CORNERSTONE_PASSPHRASE_NORCAL` exited 1 with "RuntimeError: Set CORNERSTONE_PASSPHRASE_NORCAL before the API starts."
