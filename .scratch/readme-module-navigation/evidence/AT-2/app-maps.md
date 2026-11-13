Implementation revision: `dad744db4f3b49732adc1586e08c34be2f381f73`.
Base revision: `17f45a15d1c324e36beefd0da29b77fe56b7ef91`.
All source excerpts below come from Git objects at the stated revision.
No behavior test or cold task runs during this static capture.

## `apps/site/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–95

```text
1: # Cornerstone League Weekly
2: 
3: The Cornerstone League Weekly site. Each client serves at `<slug>.4thandgoal.app`, so CPC is at `cpc.4thandgoal.app`.
4: This repo holds the Next.js source. The Python pipeline in `apps/pipeline` publishes each week's `page.json` and images into `clients/<slug>/published/`. The build
5: copies the published data of one client into `public/`. The site renders every page, the home page included, from that JSON.
6: 
7: ## Module map
8: 
9: - File loaders: the [data owner](src/lib/data/README.md) reads published files and builds the week archive.
10: - App routes: [src/app](src/app/) composes pages from loaders and package parts. Generated routes follow the client package list.
11: - Package parts: the [analyzer owner](../../packages/analyzer/README.md) owns the trade UI and API client. Its [form owner](../../packages/analyzer/site/form/README.md) owns team choice and focus. Parts take data and return markup.
12: 
13: ## Install
14: 
15: Use Node 22 or newer. The `.nvmrc` pins 22.
16: 
17: ```
18: pnpm install
19: ```
20: 
21: Install the commit hook one time per clone with `prek install`, or `pnpm hook:install`. Each worktree then reads its own branch's `.pre-commit-config.yaml`.
22: 
23: ## Run
24: 
25: ```
26: CLIENT=cpc pnpm dev
27: ```
28: 
29: ## Build and export
30: 
31: `pnpm build` writes the static export of one client to `out/`. The export has trailing slashes and no server.
32: The env value `CLIENT` names the client folder under `clients/`. A build with no `CLIENT` fails.
33: 
34: ```
35: CLIENT=cpc pnpm build
36: CLIENT=cpc pnpm check:export
37: ```
38: 
39: The `prebuild` step runs `scripts/client-build.mjs`. It checks `clients/$CLIENT/client.toml` against the JSON Schema
40: that the pipeline exports, with `ajv`. Then it writes the route file of each package of the client, the registry,
41: and the client values, and copies the client's `published/` into `public/`. Git ignores each generated file.
42: The registry lists the menu link and the home section of each package of the client only, so an omitted package ships no code.
43: 
44: `pnpm check:export` runs after the build. It checks that every file under `public/` exists in
45: `out/` with the same bytes, and that the export holds no route and no code of a package that the client omits.
46: It exits 1 and names the first mismatch. `pnpm check` builds and checks each client under `clients/`.
47: 
48: To look at the export, serve `out/`:
49: 
50: ```
51: python3 -m http.server --directory out
52: ```
53: 
54: ## Test
55: 
56: ```
57: pnpm test
58: pnpm typecheck
59: ```
60: 
61: `pnpm check` runs typecheck, test, build, and `check:export`. CI runs it on every push. `pnpm check:fast` runs typecheck and test. The commit hook runs it. The hook does not run `pnpm install`. If the hook fails in a worktree with no `node_modules`, run `pnpm install`.
62: 
63: ## Schema version
64: 
65: The week pages read `page.json` at schema version 2. The build fails loud on any other version.
66: Ship the reader of the site for a new version before the pipeline bumps the version.
67: 
68: ## Config
69: 
70: All values are build-time. Only `src/lib/config.ts` reads them.
71: 
72: | Variable | Default | Meaning |
73: | --- | --- | --- |
74: | `NEXT_PUBLIC_API_URL` | `https://api.4thandgoal.app` | Base URL of the site API. |
75: | `CLIENT` | none | The slug of the client folder under `clients/`. The build fails with no value. |
76: | `CLIENT_ROOT` | the repo root | The folder that holds `clients/` and the exported schemas. Set it to build a test client from a temp folder. |
77: 
78: A value that changes with the league comes from `client.toml`: the package list, the finder, the usage code, and the
79: season, which is the latest season of the client.
80: 
81: ## Deploy
82: 
83: Each client is one Cloudflare Worker with static assets. The Worker name is the client slug. The site has no base
84: path, because each client serves at the root of its own host.
85: 
86: A push to `main` runs the check, then deploys each client. The workflow is `.github/workflows/deploy-sites.yml`.
87: It has one job per folder under `clients/`. Each job builds the export with `CLIENT=<slug>`, runs `check:export`,
88: and deploys `out/` with `cloudflare/wrangler-action`. A failed step stops the deploy of that client.
89: 
90: The prebuild step writes `wrangler.jsonc` for `CLIENT`. Git ignores the file. It declares no route, because Brian adds
91: the Custom Domain in the Cloudflare dashboard. `docs/runbook-site-host.md` holds the deploy, the dry run, the
92: dashboard steps, and the Redirect Rule of `cpcfantasy.com`.
93: 
94: The Python publish in `apps/pipeline` writes the week folder, with `page.json` and the images, into `clients/cpc/published/` and pushes to
95: `main`. That push starts the deploy.
```

## `apps/pipeline/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–65

```text
1: # Cornerstone Weekly
2: 
3: This repo builds the weekly report site for the Cornerstone fantasy football league. The
4: data comes from Sleeper. The public site of CPC is at https://cpc.4thandgoal.app/
5: 
6: ## Module map
7: 
8: - Build and publish orchestration: the [cornerstone owner](src/cornerstone/README.md) joins the weekly stages and controls publish commits.
9: - Domain packages: the [week owner](../../packages/week/README.md) owns weekly facts and page data. Its [sheet owner](../../packages/week/python/src/week/sheet/README.md) owns roster projections. Packages hold domain rules; the app joins their outputs.
10: 
11: ## Commands
12: 
13: Each command that reads a league names its client with `--client <slug>`, such as `--client cpc`. A command with no
14: slug stops with a plain message. The client folder `clients/<slug>/` at the repo root holds `client.toml` and `data/`.
15: 
16: - `cornerstone build` builds the data of a week: `page.json` and the images.
17: - `cornerstone publish` copies the week folder to `clients/<slug>/published/` of this repo and pushes it.
18: - `cornerstone rewrite --chapter <key>` rewrites one chapter.
19: - `cornerstone page-json` writes `page.json` for a saved week.
20: - `cornerstone settings` prints the League settings of a season and each size that derives from them.
21: - `cornerstone check-client <folder>` checks the `client.toml` of a client folder and the exported schema.
22: 
23: ## Setup
24: 
25: Run `prek install` one time per clone. The hook then runs `make check-fast` before each commit.
26: Each worktree reads its own branch's `.pre-commit-config.yaml`.
27: 
28: ## Makefile
29: 
30: The `Makefile` holds the common tasks. Run `make help` to list them. A weekly run uses three targets:
31: 
32: 1. `make build CLIENT=cpc WEEK=<W>` builds the week.
33: 2. `make publish CLIENT=cpc WEEK=<W>` copies the week to `clients/cpc/published/` and pushes it.
34: 3. `make push` pushes `main`. It stops if the branch is not `main` or the tree is not clean.
35: 
36: ## Tuesday runbook
37: 
38: 1. At 8:00 the launchd job builds the week and shows a notification. The job is `com.briankwon.cornerstone-weekly`. Its log is `~/Library/Logs/cornerstone-weekly/build.log`.
39: 2. Read the week data, or the page after the site deploys.
40: 3. Run `cornerstone rewrite --client cpc --chapter <key>` for each chapter that needs a fix.
41: 4. Run `cornerstone publish --client cpc`.
42: 5. Share the home page link: https://cpc.4thandgoal.app/
43: 
44: ## Page data for the site
45: 
46: The build writes JSON and images only. It writes no HTML. The site repo renders the pages from
47: the JSON, including the home page.
48: 
49: The build writes `clients/<slug>/build/<season>/week-NN/page.json` with the images beside it.
50: Each client has its own build folder, so the build of one client never overwrites the files of another. The file holds the
51: render context and a `schema_version` key. The image paths in it are relative to the week folder.
52: The default avatar and headshot paths point to `images/` under `apps/site/public/`, and the site repo serves
53: those files.
54: 
55: `cornerstone publish` copies the whole week folder to `clients/<slug>/published/<season>/week-NN/` in the
56: repo. It copies no `images/` folder and writes no `index.html`. The site repo reads `summary` from
57: each `page.json` to list the weeks on the home page.
58: 
59: To write the file for a saved week, run `cornerstone page-json --client <slug> --season <S> --week <W>`. The
60: command reads the saved facts and blurbs. It makes no writer call and no network call.
61: 
62: Bump `PAGE_SCHEMA_VERSION` in `src/cornerstone/render.py` when a key changes meaning or leaves.
63: A new key does not need a bump.
64: 
65: Schema version 2 removed the `asset_version` and `root` keys. Only the retired templates read them.
```

## `apps/api/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–17

```text
1: # Cornerstone API
2: 
3: The FastAPI app serves each client through domain packages and deploys to Fly.
4: Its product code imports no pipeline code.
5: API tests reuse pipeline fixtures and README-rule helpers; these test dependencies do not define product ownership.
6: 
7: ## Module map
8: 
9: - HTTP composition: the [API owner](src/cornerstone_api/README.md) creates the app and mounts client routes in [app.py](src/cornerstone_api/app.py).
10: - App state and limits: the [API owner](src/cornerstone_api/README.md) owns client state, access checks, and daily answer allowances.
11: - Analyzer routes: the [analyzer owner](../../packages/analyzer/README.md) owns trade grades, caches, and persistent grade limits. The API mounts those routes.
12: 
13: ## Commands
14: 
15: Run `make help` in `apps/api/` for the app commands.
16: Run `make check-fast` for lint, types, and rules.
17: Run `make check` for lint, types, and all tests.
```

| Source | Line | Relative target | Resolved repository target | Exists at revision |
| --- | --- | --- | --- | --- |
| `apps/site/README.md` | 9 | `src/lib/data/README.md` | `apps/site/src/lib/data/README.md` | true |
| `apps/site/README.md` | 10 | `src/app/` | `apps/site/src/app` | true |
| `apps/site/README.md` | 11 | `../../packages/analyzer/README.md` | `packages/analyzer/README.md` | true |
| `apps/site/README.md` | 11 | `../../packages/analyzer/site/form/README.md` | `packages/analyzer/site/form/README.md` | true |
| `apps/pipeline/README.md` | 8 | `src/cornerstone/README.md` | `apps/pipeline/src/cornerstone/README.md` | true |
| `apps/pipeline/README.md` | 9 | `../../packages/week/README.md` | `packages/week/README.md` | true |
| `apps/pipeline/README.md` | 9 | `../../packages/week/python/src/week/sheet/README.md` | `packages/week/python/src/week/sheet/README.md` | true |
| `apps/api/README.md` | 9 | `src/cornerstone_api/README.md` | `apps/api/src/cornerstone_api/README.md` | true |
| `apps/api/README.md` | 9 | `src/cornerstone_api/app.py` | `apps/api/src/cornerstone_api/app.py` | true |
| `apps/api/README.md` | 10 | `src/cornerstone_api/README.md` | `apps/api/src/cornerstone_api/README.md` | true |
| `apps/api/README.md` | 11 | `../../packages/analyzer/README.md` | `packages/analyzer/README.md` | true |
