Implementation revision: `dad744db4f3b49732adc1586e08c34be2f381f73`.
Base revision: `17f45a15d1c324e36beefd0da29b77fe56b7ef91`.
All source excerpts below come from Git objects at the stated revision.
No behavior test or cold task runs during this static capture.

The app instruction diffs add only each app README pointer. Existing command and rule sections remain byte-for-byte.
The root Where the work sits section still requires state, then one ticket.
The cold-trial exception appears in the approved procedure only.

# Before and after: `CLAUDE.md`

## `CLAUDE.md` at `17f45a15d1c324e36beefd0da29b77fe56b7ef91`; lines 1–60

```text
1: # 4thandgoal
2: 
3: This repo holds three apps. The site and the pipeline each have a CLAUDE.md with its own commands and rules. Read the one for the app you change.
4: 
5: - `apps/site/` is the Next.js site. Its build copies `clients/<slug>/published/` of one client into `public/` and renders each `page.json` and its images.
6: - `apps/pipeline/` is the Python pipeline. It builds each week and publishes it into `clients/<slug>/published/`.
7: - `apps/api/` is the API of the trade analyzer. It imports the pipeline and deploys to Fly. Run `make help` in it.
8: 
9: The root holds one uv workspace and one pnpm workspace, each with one lock file: `uv.lock` and `pnpm-lock.yaml`.
10: Run `uv sync --all-packages` and `pnpm install` at the root. A member runs with `uv run --exact --package <name>`.
11: 
12: ## Style
13: 
14: Write all output in Simplified Technical English. Rules: `~/.claude/rules/communication/simplified-technical-english.md`. Active voice, present tense, one instruction per sentence, 20 words or fewer, no `-ing` as a verb, plain words. Code, technical names, and quoted output are exempt.
15: 
16: ## Records
17: 
18: - `GLOSSARY.md` holds the terms of both apps, one section per app, and the workflow terms. Each term has one meaning.
19: - `docs/adr/` holds one ADR series for both apps. `docs/adr/README.md` maps each old app number to its new number.
20: 
21: ## The flow
22: 
23: ADRs 0018 to 0021 and ADR 0026 set the flow. ADR 0026 supersedes ADR 0020. The spec `.scratch/one/` builds it, so its own tickets still merge to `main` as before.
24: 
25: 1. `main` is the record branch. No agent commits on `main` or pushes to `main` (ADR 0019).
26: 2. A spec branch is named `<slug>` and starts from `main`.
27: 3. A ticket branch is named `<slug>-<NN>`. It is local, starts from the spec branch, and has its own worktree.
28: 4. A ticket merges into its spec branch with `git merge --no-edit`, after the check passes.
29: 5. One pull request goes from the spec branch to `main`, as a squash merge.
30: 6. An agent records the evidence of each acceptance test `AT-<n>`. The agent gives no test verdict.
31: 7. A fresh subagent, the Judge, gives PASS, FAIL, or BLOCKED for each test in `VERDICTS.md`. A check blocks the merge until each test has PASS. A FAIL from Brian in a PR comment overrides the Judge (ADR 0026).
32: 
33: The weekly `publish` is the one exception. It may push to `main`, and it may stage only `clients/<slug>/published/<season>/`, `clients/<slug>/data/<season>/`, and `clients/<slug>/build/<season>/`.
34: 
35: The repo plugin `4ag` takes an idea to a merged spec. Run its skills in this order. Brian approves the output of each of steps 2 to 4.
36: 
37: 1. `4ag:plan <outcome statement>` writes the map and the decision tickets. `4ag:plan <feature>` clears one decision ticket per session.
38: 2. `4ag:to-spec <feature>` writes `PRD.md`.
39: 3. `4ag:to-acceptance <feature>` writes `ACCEPTANCE.md`.
40: 4. `4ag:to-tickets <feature>` writes the tickets and the `state.md` row.
41: 5. `4ag:implement <feature>` builds each ticket on its ticket branch, merges it into the spec branch, records the evidence in `EVIDENCE.md`, has the Judge write `VERDICTS.md`, and opens one PR to `main`.
42: 6. Brian posts no comment unless he gives a FAIL. `4ag:review <PR number>` does one round of feedback per run. The check `verdict` passes when each test has PASS from the Judge and no FAIL from Brian, and Brian merges.
43: 
44: ## Tracker
45: 
46: The tracker is local markdown, because the notes name league managers and the repo is public (ADR 0021).
47: 
48: - The tracker is `.scratch/<feature>/` at the root, for both apps. See `docs/agents/issue-tracker.md`.
49: - A feature that both old trackers held keeps a `site/` and a `pipeline/` subfolder, each with its own PRD and `issues/`.
50: - A new feature has an optional `MAP.md`, `decisions/`, `PRD.md`, `ACCEPTANCE.md`, and `issues/`. Old features keep their shape.
51: 
52: ## Where the work sits
53: 
54: `docs/agents/state.md` lists each open feature, its next ticket, and its blocker. An agent new to the repo reads it
55: after this file, then reads one ticket in the tracker.
56: 
57: ## Commits
58: 
59: The prek hook runs `pnpm check:fast` of the site, then `make check-fast` of the pipeline and of the API, before each commit.
60: Never commit with `--no-verify`.
```

## `CLAUDE.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–63

```text
1: # 4thandgoal
2: 
3: This repo holds three apps. The site and the pipeline each have a CLAUDE.md with its own commands and rules. Read the one for the app you change.
4: 
5: - [Site](apps/site/README.md) in `apps/site/` is the Next.js site. Its build copies `clients/<slug>/published/` of one client into `public/` and renders each `page.json` and its images.
6: - [Pipeline](apps/pipeline/README.md) in `apps/pipeline/` is the Python pipeline. It builds each week and publishes it into `clients/<slug>/published/`.
7: - [API](apps/api/README.md) in `apps/api/` serves the trade analyzer and deploys to Fly. Its product code imports no pipeline code. Run `make help` in it.
8: 
9: For module ownership, follow root instructions → app README → owner README → module and test.
10: Choose the responsibility in the app map, then follow its owner links.
11: 
12: The root holds one uv workspace and one pnpm workspace, each with one lock file: `uv.lock` and `pnpm-lock.yaml`.
13: Run `uv sync --all-packages` and `pnpm install` at the root. A member runs with `uv run --exact --package <name>`.
14: 
15: ## Style
16: 
17: Write all output in Simplified Technical English. Rules: `~/.claude/rules/communication/simplified-technical-english.md`. Active voice, present tense, one instruction per sentence, 20 words or fewer, no `-ing` as a verb, plain words. Code, technical names, and quoted output are exempt.
18: 
19: ## Records
20: 
21: - `GLOSSARY.md` holds the terms of both apps, one section per app, and the workflow terms. Each term has one meaning.
22: - `docs/adr/` holds one ADR series for both apps. `docs/adr/README.md` maps each old app number to its new number.
23: 
24: ## The flow
25: 
26: ADRs 0018 to 0021 and ADR 0026 set the flow. ADR 0026 supersedes ADR 0020. The spec `.scratch/one/` builds it, so its own tickets still merge to `main` as before.
27: 
28: 1. `main` is the record branch. No agent commits on `main` or pushes to `main` (ADR 0019).
29: 2. A spec branch is named `<slug>` and starts from `main`.
30: 3. A ticket branch is named `<slug>-<NN>`. It is local, starts from the spec branch, and has its own worktree.
31: 4. A ticket merges into its spec branch with `git merge --no-edit`, after the check passes.
32: 5. One pull request goes from the spec branch to `main`, as a squash merge.
33: 6. An agent records the evidence of each acceptance test `AT-<n>`. The agent gives no test verdict.
34: 7. A fresh subagent, the Judge, gives PASS, FAIL, or BLOCKED for each test in `VERDICTS.md`. A check blocks the merge until each test has PASS. A FAIL from Brian in a PR comment overrides the Judge (ADR 0026).
35: 
36: The weekly `publish` is the one exception. It may push to `main`, and it may stage only `clients/<slug>/published/<season>/`, `clients/<slug>/data/<season>/`, and `clients/<slug>/build/<season>/`.
37: 
38: The repo plugin `4ag` takes an idea to a merged spec. Run its skills in this order. Brian approves the output of each of steps 2 to 4.
39: 
40: 1. `4ag:plan <outcome statement>` writes the map and the decision tickets. `4ag:plan <feature>` clears one decision ticket per session.
41: 2. `4ag:to-spec <feature>` writes `PRD.md`.
42: 3. `4ag:to-acceptance <feature>` writes `ACCEPTANCE.md`.
43: 4. `4ag:to-tickets <feature>` writes the tickets and the `state.md` row.
44: 5. `4ag:implement <feature>` builds each ticket on its ticket branch, merges it into the spec branch, records the evidence in `EVIDENCE.md`, has the Judge write `VERDICTS.md`, and opens one PR to `main`.
45: 6. Brian posts no comment unless he gives a FAIL. `4ag:review <PR number>` does one round of feedback per run. The check `verdict` passes when each test has PASS from the Judge and no FAIL from Brian, and Brian merges.
46: 
47: ## Tracker
48: 
49: The tracker is local markdown, because the notes name league managers and the repo is public (ADR 0021).
50: 
51: - The tracker is `.scratch/<feature>/` at the root, for both apps. See `docs/agents/issue-tracker.md`.
52: - A feature that both old trackers held keeps a `site/` and a `pipeline/` subfolder, each with its own PRD and `issues/`.
53: - A new feature has an optional `MAP.md`, `decisions/`, `PRD.md`, `ACCEPTANCE.md`, and `issues/`. Old features keep their shape.
54: 
55: ## Where the work sits
56: 
57: `docs/agents/state.md` lists each open feature, its next ticket, and its blocker. An agent new to the repo reads it
58: after this file, then reads one ticket in the tracker.
59: 
60: ## Commits
61: 
62: The prek hook runs `pnpm check:fast` of the site, then `make check-fast` of the pipeline and of the API, before each commit.
63: Never commit with `--no-verify`.
```

# Before and after: `apps/site/CLAUDE.md`

## `apps/site/CLAUDE.md` at `17f45a15d1c324e36beefd0da29b77fe56b7ef91`; lines 1–27

```text
1: # Cornerstone site
2: 
3: The Next.js site. It builds one client, named by the env value `CLIENT`. The build copies `clients/$CLIENT/published/`
4: into `public/`, and the site renders each `public/<season>/week-NN/page.json` and its images.
5: The root CLAUDE.md holds the style, the flow, and the tracker.
6: 
7: ## Commands
8: 
9: Run these in `apps/site/`.
10: 
11: - Install: `pnpm install`
12: - Dev server: `CLIENT=cpc pnpm dev`
13: - Build the static export: `CLIENT=cpc pnpm build`. The `prebuild` step checks `client.toml` and writes the generated files.
14: - Test: `pnpm test`. The tests read the generated files, so run `pnpm check:fast` or a build first.
15: - Check the export: `CLIENT=cpc pnpm check:export`. Run it after `pnpm build`, with the same `CLIENT`.
16: - Check the readability floor: `CLIENT=cpc pnpm check:floor`. Run it after `pnpm build`, with the same `CLIENT`. Add `-g <route>` to check one page.
17: - Test the rules of the floor: `pnpm test:floor`. It needs Chromium once: `pnpm exec playwright install chromium`.
18: - Check all: `pnpm check`. It runs the fast check, the rules of the floor, then the build, `check:export`, and `check:floor` of each client under `clients/`. Then it builds the fixture client of the midseason report and runs the floor of the report on it. CI runs it on every push.
19: - Fast check: `pnpm check:fast`. It runs the client build of `cpc`, typecheck, and test. The hook runs it.
20: 
21: ## Rules
22: 
23: - The hook does not run `pnpm install`. In a new worktree with no `node_modules`, run `pnpm install` first.
24: - The pipeline owns the shape of each published file. Change the schema in `packages/<package>/site/schema/` and the pipeline writer together (ADR 0013).
25: - Never edit a file with a `GENERATED` first line. Change `client.toml` or `scripts/client-build.mjs`, and build again.
26: - A component takes data and returns markup. It reads no file, no env, and no config (ADR 0012).
27: - Each package folder holds a README with the headings Knows, Ports, and Does not do (ADR 0016).
```

## `apps/site/CLAUDE.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–29

```text
1: # Cornerstone site
2: 
3: The Next.js site. It builds one client, named by the env value `CLIENT`. The build copies `clients/$CLIENT/published/`
4: into `public/`, and the site renders each `public/<season>/week-NN/page.json` and its images.
5: The root CLAUDE.md holds the style, the flow, and the tracker.
6: 
7: For module ownership, start with the [app map](README.md). Follow its owner README links to the module and test.
8: 
9: ## Commands
10: 
11: Run these in `apps/site/`.
12: 
13: - Install: `pnpm install`
14: - Dev server: `CLIENT=cpc pnpm dev`
15: - Build the static export: `CLIENT=cpc pnpm build`. The `prebuild` step checks `client.toml` and writes the generated files.
16: - Test: `pnpm test`. The tests read the generated files, so run `pnpm check:fast` or a build first.
17: - Check the export: `CLIENT=cpc pnpm check:export`. Run it after `pnpm build`, with the same `CLIENT`.
18: - Check the readability floor: `CLIENT=cpc pnpm check:floor`. Run it after `pnpm build`, with the same `CLIENT`. Add `-g <route>` to check one page.
19: - Test the rules of the floor: `pnpm test:floor`. It needs Chromium once: `pnpm exec playwright install chromium`.
20: - Check all: `pnpm check`. It runs the fast check, the rules of the floor, then the build, `check:export`, and `check:floor` of each client under `clients/`. Then it builds the fixture client of the midseason report and runs the floor of the report on it. CI runs it on every push.
21: - Fast check: `pnpm check:fast`. It runs the client build of `cpc`, typecheck, and test. The hook runs it.
22: 
23: ## Rules
24: 
25: - The hook does not run `pnpm install`. In a new worktree with no `node_modules`, run `pnpm install` first.
26: - The pipeline owns the shape of each published file. Change the schema in `packages/<package>/site/schema/` and the pipeline writer together (ADR 0013).
27: - Never edit a file with a `GENERATED` first line. Change `client.toml` or `scripts/client-build.mjs`, and build again.
28: - A component takes data and returns markup. It reads no file, no env, and no config (ADR 0012).
29: - Each package folder holds a README with the headings Knows, Ports, and Does not do (ADR 0016).
```

# Before and after: `apps/pipeline/CLAUDE.md`

## `apps/pipeline/CLAUDE.md` at `17f45a15d1c324e36beefd0da29b77fe56b7ef91`; lines 1–61

```text
1: # Cornerstone Weekly
2: 
3: ## Purpose
4: 
5: This tool builds a weekly report page for the Cornerstone fantasy football league. It reads
6: league data from Sleeper. It writes the chapters of the report and writes the page data. The site in `apps/site` renders the pages.
7: The root CLAUDE.md holds the style, the flow, and the tracker. `GLOSSARY.md` names the chapter of prose a "Prose block".
8: 
9: ## Commands
10: 
11: Run these in `apps/pipeline/`. Run `make help` for the full list.
12: 
13: - Install: `make install`. The root `uv.lock` holds the locked versions of the whole uv workspace.
14: - Check: `make check`. The hook runs `make check-fast`.
15: - Build a week: `make build CLIENT=cpc WEEK=<W>`. Each league target needs the client slug.
16: - Publish a week: `make publish CLIENT=cpc WEEK=<W>`. It commits `clients/<slug>/build/<season>/`, `clients/<slug>/data/<season>/`, and `clients/<slug>/published/<season>/`, then pushes `main`.
17: - Local API on port 8080: `make -C ../api api`. The API is its own app in `apps/api/`.
18: 
19: ## Pipeline
20: 
21: 1. Fetch the raw league data from Sleeper.
22: 2. Save the raw data under `clients/<slug>/data/` and cache the shared NFL data under `data/nfl/cache/`, both at the repo root.
23: 3. Compute the stats for each chapter.
24: 4. Write the chapter text with the Anthropic API.
25: 5. Write `page.json` and the images into the build folder `clients/<slug>/build/`.
26: 6. Publish the week folder to `clients/<slug>/published/` of this repo.
27: 
28: ## Where the work sits
29: 
30: `docs/agents/state.md` at the repo root lists each open feature of both apps, its next ticket, and its hold. Read it, then the
31: ticket in the root tracker under `.scratch/`.
32: 
33: ## Publish rule
34: 
35: Nothing publishes without `cornerstone publish`. No other command or script pushes the site.
36: 
37: ## Tests
38: 
39: - Run `uv run pytest` for the default suite. It skips tests marked `live`.
40: - A test marked `live` calls a real external API. Run it on purpose with `uv run pytest -m live`.
41: - Run `make check` before a merge. The prek hook runs `make check-fast` on each commit.
42: - Name a rule test `tests/test_rule_<topic>.py`. `make rules` finds each one with no edit.
43: 
44: ## House style
45: 
46: Prose follows Simplified Technical English. The rules are in
47: `~/.claude/rules/communication/simplified-technical-english.md`.
48: 
49: ## Agent skills
50: 
51: ### Issue tracker
52: 
53: Local markdown under `.scratch/<feature>/` at the repo root. See `docs/agents/issue-tracker.md`.
54: 
55: ### Triage labels
56: 
57: The five default names, unchanged. See `docs/agents/triage-labels.md`.
58: 
59: ### Domain docs
60: 
61: Single-context: `GLOSSARY.md` and `docs/adr/` at the repo root, shared with the site. See `docs/agents/domain.md`.
```

## `apps/pipeline/CLAUDE.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–63

```text
1: # Cornerstone Weekly
2: 
3: ## Purpose
4: 
5: This tool builds a weekly report page for the Cornerstone fantasy football league. It reads
6: league data from Sleeper. It writes the chapters of the report and writes the page data. The site in `apps/site` renders the pages.
7: The root CLAUDE.md holds the style, the flow, and the tracker. `GLOSSARY.md` names the chapter of prose a "Prose block".
8: 
9: For module ownership, start with the [app map](README.md). Follow its owner README links to the module and test.
10: 
11: ## Commands
12: 
13: Run these in `apps/pipeline/`. Run `make help` for the full list.
14: 
15: - Install: `make install`. The root `uv.lock` holds the locked versions of the whole uv workspace.
16: - Check: `make check`. The hook runs `make check-fast`.
17: - Build a week: `make build CLIENT=cpc WEEK=<W>`. Each league target needs the client slug.
18: - Publish a week: `make publish CLIENT=cpc WEEK=<W>`. It commits `clients/<slug>/build/<season>/`, `clients/<slug>/data/<season>/`, and `clients/<slug>/published/<season>/`, then pushes `main`.
19: - Local API on port 8080: `make -C ../api api`. The API is its own app in `apps/api/`.
20: 
21: ## Pipeline
22: 
23: 1. Fetch the raw league data from Sleeper.
24: 2. Save the raw data under `clients/<slug>/data/` and cache the shared NFL data under `data/nfl/cache/`, both at the repo root.
25: 3. Compute the stats for each chapter.
26: 4. Write the chapter text with the Anthropic API.
27: 5. Write `page.json` and the images into the build folder `clients/<slug>/build/`.
28: 6. Publish the week folder to `clients/<slug>/published/` of this repo.
29: 
30: ## Where the work sits
31: 
32: `docs/agents/state.md` at the repo root lists each open feature of both apps, its next ticket, and its hold. Read it, then the
33: ticket in the root tracker under `.scratch/`.
34: 
35: ## Publish rule
36: 
37: Nothing publishes without `cornerstone publish`. No other command or script pushes the site.
38: 
39: ## Tests
40: 
41: - Run `uv run pytest` for the default suite. It skips tests marked `live`.
42: - A test marked `live` calls a real external API. Run it on purpose with `uv run pytest -m live`.
43: - Run `make check` before a merge. The prek hook runs `make check-fast` on each commit.
44: - Name a rule test `tests/test_rule_<topic>.py`. `make rules` finds each one with no edit.
45: 
46: ## House style
47: 
48: Prose follows Simplified Technical English. The rules are in
49: `~/.claude/rules/communication/simplified-technical-english.md`.
50: 
51: ## Agent skills
52: 
53: ### Issue tracker
54: 
55: Local markdown under `.scratch/<feature>/` at the repo root. See `docs/agents/issue-tracker.md`.
56: 
57: ### Triage labels
58: 
59: The five default names, unchanged. See `docs/agents/triage-labels.md`.
60: 
61: ### Domain docs
62: 
63: Single-context: `GLOSSARY.md` and `docs/adr/` at the repo root, shared with the site. See `docs/agents/domain.md`.
```

# Before and after: `apps/site/README.md`

## `apps/site/README.md` at `17f45a15d1c324e36beefd0da29b77fe56b7ef91`; lines 1–89

```text
1: # Cornerstone League Weekly
2: 
3: The Cornerstone League Weekly site. Each client serves at `<slug>.4thandgoal.app`, so CPC is at `cpc.4thandgoal.app`.
4: This repo holds the Next.js source. The Python pipeline in `apps/pipeline` publishes each week's `page.json` and images into `clients/<slug>/published/`. The build
5: copies the published data of one client into `public/`. The site renders every page, the home page included, from that JSON.
6: 
7: ## Install
8: 
9: Use Node 22 or newer. The `.nvmrc` pins 22.
10: 
11: ```
12: pnpm install
13: ```
14: 
15: Install the commit hook one time per clone with `prek install`, or `pnpm hook:install`. Each worktree then reads its own branch's `.pre-commit-config.yaml`.
16: 
17: ## Run
18: 
19: ```
20: CLIENT=cpc pnpm dev
21: ```
22: 
23: ## Build and export
24: 
25: `pnpm build` writes the static export of one client to `out/`. The export has trailing slashes and no server.
26: The env value `CLIENT` names the client folder under `clients/`. A build with no `CLIENT` fails.
27: 
28: ```
29: CLIENT=cpc pnpm build
30: CLIENT=cpc pnpm check:export
31: ```
32: 
33: The `prebuild` step runs `scripts/client-build.mjs`. It checks `clients/$CLIENT/client.toml` against the JSON Schema
34: that the pipeline exports, with `ajv`. Then it writes the route file of each package of the client, the registry,
35: and the client values, and copies the client's `published/` into `public/`. Git ignores each generated file.
36: The registry lists the menu link and the home section of each package of the client only, so an omitted package ships no code.
37: 
38: `pnpm check:export` runs after the build. It checks that every file under `public/` exists in
39: `out/` with the same bytes, and that the export holds no route and no code of a package that the client omits.
40: It exits 1 and names the first mismatch. `pnpm check` builds and checks each client under `clients/`.
41: 
42: To look at the export, serve `out/`:
43: 
44: ```
45: python3 -m http.server --directory out
46: ```
47: 
48: ## Test
49: 
50: ```
51: pnpm test
52: pnpm typecheck
53: ```
54: 
55: `pnpm check` runs typecheck, test, build, and `check:export`. CI runs it on every push. `pnpm check:fast` runs typecheck and test. The commit hook runs it. The hook does not run `pnpm install`. If the hook fails in a worktree with no `node_modules`, run `pnpm install`.
56: 
57: ## Schema version
58: 
59: The week pages read `page.json` at schema version 2. The build fails loud on any other version.
60: Ship the reader of the site for a new version before the pipeline bumps the version.
61: 
62: ## Config
63: 
64: All values are build-time. Only `src/lib/config.ts` reads them.
65: 
66: | Variable | Default | Meaning |
67: | --- | --- | --- |
68: | `NEXT_PUBLIC_API_URL` | `https://api.4thandgoal.app` | Base URL of the site API. |
69: | `CLIENT` | none | The slug of the client folder under `clients/`. The build fails with no value. |
70: | `CLIENT_ROOT` | the repo root | The folder that holds `clients/` and the exported schemas. Set it to build a test client from a temp folder. |
71: 
72: A value that changes with the league comes from `client.toml`: the package list, the finder, the usage code, and the
73: season, which is the latest season of the client.
74: 
75: ## Deploy
76: 
77: Each client is one Cloudflare Worker with static assets. The Worker name is the client slug. The site has no base
78: path, because each client serves at the root of its own host.
79: 
80: A push to `main` runs the check, then deploys each client. The workflow is `.github/workflows/deploy-sites.yml`.
81: It has one job per folder under `clients/`. Each job builds the export with `CLIENT=<slug>`, runs `check:export`,
82: and deploys `out/` with `cloudflare/wrangler-action`. A failed step stops the deploy of that client.
83: 
84: The prebuild step writes `wrangler.jsonc` for `CLIENT`. Git ignores the file. It declares no route, because Brian adds
85: the Custom Domain in the Cloudflare dashboard. `docs/runbook-site-host.md` holds the deploy, the dry run, the
86: dashboard steps, and the Redirect Rule of `cpcfantasy.com`.
87: 
88: The Python publish in `apps/pipeline` writes the week folder, with `page.json` and the images, into `clients/cpc/published/` and pushes to
89: `main`. That push starts the deploy.
```

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

# Before and after: `apps/pipeline/README.md`

## `apps/pipeline/README.md` at `17f45a15d1c324e36beefd0da29b77fe56b7ef91`; lines 1–60

```text
1: # Cornerstone Weekly
2: 
3: This repo builds the weekly report site for the Cornerstone fantasy football league. The
4: data comes from Sleeper. The public site of CPC is at https://cpc.4thandgoal.app/
5: 
6: ## Commands
7: 
8: Each command that reads a league names its client with `--client <slug>`, such as `--client cpc`. A command with no
9: slug stops with a plain message. The client folder `clients/<slug>/` at the repo root holds `client.toml` and `data/`.
10: 
11: - `cornerstone build` builds the data of a week: `page.json` and the images.
12: - `cornerstone publish` copies the week folder to `clients/<slug>/published/` of this repo and pushes it.
13: - `cornerstone rewrite --chapter <key>` rewrites one chapter.
14: - `cornerstone page-json` writes `page.json` for a saved week.
15: - `cornerstone settings` prints the League settings of a season and each size that derives from them.
16: - `cornerstone check-client <folder>` checks the `client.toml` of a client folder and the exported schema.
17: 
18: ## Setup
19: 
20: Run `prek install` one time per clone. The hook then runs `make check-fast` before each commit.
21: Each worktree reads its own branch's `.pre-commit-config.yaml`.
22: 
23: ## Makefile
24: 
25: The `Makefile` holds the common tasks. Run `make help` to list them. A weekly run uses three targets:
26: 
27: 1. `make build CLIENT=cpc WEEK=<W>` builds the week.
28: 2. `make publish CLIENT=cpc WEEK=<W>` copies the week to `clients/cpc/published/` and pushes it.
29: 3. `make push` pushes `main`. It stops if the branch is not `main` or the tree is not clean.
30: 
31: ## Tuesday runbook
32: 
33: 1. At 8:00 the launchd job builds the week and shows a notification. The job is `com.briankwon.cornerstone-weekly`. Its log is `~/Library/Logs/cornerstone-weekly/build.log`.
34: 2. Read the week data, or the page after the site deploys.
35: 3. Run `cornerstone rewrite --client cpc --chapter <key>` for each chapter that needs a fix.
36: 4. Run `cornerstone publish --client cpc`.
37: 5. Share the home page link: https://cpc.4thandgoal.app/
38: 
39: ## Page data for the site
40: 
41: The build writes JSON and images only. It writes no HTML. The site repo renders the pages from
42: the JSON, including the home page.
43: 
44: The build writes `clients/<slug>/build/<season>/week-NN/page.json` with the images beside it.
45: Each client has its own build folder, so the build of one client never overwrites the files of another. The file holds the
46: render context and a `schema_version` key. The image paths in it are relative to the week folder.
47: The default avatar and headshot paths point to `images/` under `apps/site/public/`, and the site repo serves
48: those files.
49: 
50: `cornerstone publish` copies the whole week folder to `clients/<slug>/published/<season>/week-NN/` in the
51: repo. It copies no `images/` folder and writes no `index.html`. The site repo reads `summary` from
52: each `page.json` to list the weeks on the home page.
53: 
54: To write the file for a saved week, run `cornerstone page-json --client <slug> --season <S> --week <W>`. The
55: command reads the saved facts and blurbs. It makes no writer call and no network call.
56: 
57: Bump `PAGE_SCHEMA_VERSION` in `src/cornerstone/render.py` when a key changes meaning or leaves.
58: A new key does not need a bump.
59: 
60: Schema version 2 removed the `asset_version` and `root` keys. Only the retired templates read them.
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

# Before and after: `apps/api/README.md`

The base has no such document.

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

# Before and after: `apps/site/src/lib/data/README.md`

## `apps/site/src/lib/data/README.md` at `17f45a15d1c324e36beefd0da29b77fe56b7ef91`; lines 1–22

```text
1: # src/lib/data: the loaders of the published files
2: 
3: ## Knows
4: 
5: - One loader per published file: the week page file, the rankings file, the managers file, `waiver.json`, `midseason.json`, and `sim.json`.
6: - Where each file sits under `public/`, and which week folders hold `waiver.json`.
7: - The join of the managers file with the last week of the rankings file.
8: - The teams of the latest week for the sheet of Your team on the front door, in `front-door-data.ts`.
9: - Whether the waiver route and the managers route are on. `next.config.ts` builds each one only when its file exists.
10: - The shared read of a published file in `published-file.ts`: the check of the schema version, then the parse.
11: - The test of every published file against its schema, in `src/lib/data/published-files.test.ts`.
12: 
13: ## Ports
14: 
15: - The reads of `public/` with `node:fs`, at build time only.
16: 
17: ## Does not do
18: 
19: - It owns no shape. The pipeline owns each shape, and each package holds the schema of its own file (ADR 0013).
20: - It runs in no browser. Only the app layer and `next.config.ts` call a loader (ADR 0012).
21: - It writes no file. The pipeline publishes every file under `public/`.
22: - It formats no number. Each package holds its own formats.
```

## `apps/site/src/lib/data/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–23

```text
1: # src/lib/data: the loaders of the published files
2: 
3: ## Knows
4: 
5: - [week-data.ts](week-data.ts) owns the archive. `listWeekSummaries` sorts seasons and weeks numerically, newest first. [week-data.test.ts](week-data.test.ts) checks cross-season order and weeks 2 and 10.
6: - One loader per published file: the week page file, the rankings file, the managers file, `waiver.json`, `midseason.json`, and `sim.json`.
7: - Where each file sits under `public/`, and which week folders hold `waiver.json`.
8: - The join of the managers file with the last week of the rankings file.
9: - The teams of the latest week for the sheet of Your team on the front door, in `front-door-data.ts`.
10: - Whether the waiver route and the managers route are on. `next.config.ts` builds each one only when its file exists.
11: - The shared read of a published file in `published-file.ts`: the check of the schema version, then the parse.
12: - The test of every published file against its schema, in `src/lib/data/published-files.test.ts`.
13: 
14: ## Ports
15: 
16: - The reads of `public/` with `node:fs`, at build time only.
17: 
18: ## Does not do
19: 
20: - It owns no shape. The [pipeline](../../../../pipeline/README.md) owns each shape, and each package holds the schema of its own file (ADR 0013).
21: - It runs in no browser. Only the app layer and `next.config.ts` call a loader (ADR 0012).
22: - It writes no file. The pipeline publishes every file under `public/`.
23: - It formats no number. Each package holds its own formats.
```

# Before and after: `apps/pipeline/src/cornerstone/README.md`

## `apps/pipeline/src/cornerstone/README.md` at `17f45a15d1c324e36beefd0da29b77fe56b7ef91`; lines 1–24

```text
1: # cornerstone
2: 
3: ## Knows
4: 
5: - The weekly build: fetch from the provider, parse, build the fact sheet, write, verify, render, and publish.
6: - The `advisor-eval` command of the CLI. The `analyzer` package holds the fact sheet, the Advisor, and the Finder.
7: - The build of each week and the season files. The `rankings`, `managers`, and `waiver` packages hold their own rules.
8: - The build and the publish of the midseason report: `midseason` runs the sim through `season_sim.py`, reads the pairs left through `season_schedule.py`, and writes the draft and the review file, and `midseason-publish` checks each blurb again and commits `midseason.json` and `sim.json`.
9: - The six layers: model, provider, load, facts, write, output. A module imports only from its own layer or a lower one.
10: - The shared kernel is the league package in `packages/league/`. Every outside service enters through it.
11: - The fact tokens, the writer, the verifier, and the default voice are the facts package in `packages/facts/`.
12: - `LAYER_OF` in `tests/test_layers.py` gives the layer of each module. `docs/adr/0010-six-layers-import-downward-only.md` gives the reason. The terms are in `GLOSSARY.md`.
13: 
14: ## Ports
15: 
16: - `Writer` in `league/claude_port.py`: the one Claude call. `ClaudeWriter` in `facts/writer.py` implements it. Its key is `ANTHROPIC_API_KEY`.
17: - `Jev` in `league/jev_port.py`: the one TypeSafe Jev request. `TypeSafeJev` in `league/jev.py` implements it. Its key is `TYPESAFE_API_KEY`.
18: - The `Provider` port is in `league/provider/`. `tests/fakes.py` holds the one fake of each port: `FixtureProvider`, `FakeWriter`, and `FakeJev`.
19: 
20: ## Does not do
21: 
22: - It never imports `cornerstone_api`. That package serves the trade analyzer over HTTP.
23: - It builds no HTML. The site repo builds the HTML from each published file.
24: - No module reads a global client. The CLI or the API entry builds the Client once with `load_client` and passes it down.
```

## `apps/pipeline/src/cornerstone/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–24

```text
1: # cornerstone
2: 
3: ## Knows
4: 
5: - The weekly build: fetch from the provider, parse, build the fact sheet, write, verify, render, and publish. [publish.py](publish.py) owns `run_publish` and limits commits to the client season paths. [test_rule_publish.py](../../tests/test_rule_publish.py) checks stray files and other seasons.
6: - The `advisor-eval` command of the CLI. The `analyzer` package holds the fact sheet, the Advisor, and the Finder.
7: - The build of each week and the season files. The `rankings`, `managers`, and `waiver` packages hold their own rules.
8: - The build and the publish of the midseason report: `midseason` runs the sim through `season_sim.py`, reads the pairs left through `season_schedule.py`, and writes the draft and the review file, and `midseason-publish` checks each blurb again and commits `midseason.json` and `sim.json`.
9: - The six layers: model, provider, load, facts, write, output. A module imports only from its own layer or a lower one.
10: - The shared kernel is the league package in `packages/league/`. Every outside service enters through it.
11: - The fact tokens, the writer, the verifier, and the default voice are the facts package in `packages/facts/`.
12: - `LAYER_OF` in `tests/test_layers.py` gives the layer of each module. `docs/adr/0010-six-layers-import-downward-only.md` gives the reason. The terms are in `GLOSSARY.md`.
13: 
14: ## Ports
15: 
16: - `Writer` in `league/claude_port.py`: the one Claude call. `ClaudeWriter` in `facts/writer.py` implements it. Its key is `ANTHROPIC_API_KEY`.
17: - `Jev` in `league/jev_port.py`: the one TypeSafe Jev request. `TypeSafeJev` in `league/jev.py` implements it. Its key is `TYPESAFE_API_KEY`.
18: - The `Provider` port is in `league/provider/`. `tests/fakes.py` holds the one fake of each port: `FixtureProvider`, `FakeWriter`, and `FakeJev`.
19: 
20: ## Does not do
21: 
22: - It never imports `cornerstone_api`. The [API owner](../../../api/src/cornerstone_api/README.md) serves the trade analyzer over HTTP.
23: - It builds no HTML. The site repo builds the HTML from each published file.
24: - No module reads a global client. The CLI or the API entry builds the Client once with `load_client` and passes it down.
```

# Before and after: `apps/api/src/cornerstone_api/README.md`

## `apps/api/src/cornerstone_api/README.md` at `17f45a15d1c324e36beefd0da29b77fe56b7ef91`; lines 1–24

```text
1: # cornerstone_api
2: 
3: ## Knows
4: 
5: - The FastAPI app that serves the trade analyzer to the site of each client.
6: - At start it reads each folder under `clients/`. A bad `client.toml` stops the start with the file and the key.
7: - It mounts the analyzer routes of the `analyzer` package at `/clients/<slug>/`. The old paths with no client answer as `cpc`.
8: - It mounts the eggs routes of the `eggs` package at `/clients/<slug>/eggs/` for each client of the package, with one SQLite file per client in `CORNERSTONE_EGGS_DIR`.
9: - The ask route of the front door at `/clients/<slug>/ask`, behind the passphrase. One Jev request routes each typed question, and the route table in `ask.py` reads the answers. `ask_wording.py` holds every word sent to Jev. An honest miss writes one entry in the miss log, one SQLite file per client in `CORNERSTONE_ASK_DIR`, kept 90 days (ADR 0031).
10: - The trade Topics of the front door at `/clients/<slug>/trade-check` and `/clients/<slug>/trade-ideas`, behind the passphrase, in `trade_topics.py`. A typed trade check has one Jev request that picks the player of each side from the real rosters, with its words in `trade_wording.py`. An unsure pick gives the form of the Trade page. Each route streams a plain step for each stage of the Advisor, then the whole Answer, in the event stream of the AI SDK. Trade ideas runs whatever the `finder` flag says. Sell high at `/clients/<slug>/sell-high` streams the same way, with the sell high press of the `analyzer` package.
11: - The free answer of the ask box at `/clients/<slug>/ask/free`, behind the passphrase. The route runs again first, so only a question that Jev routes to a free answer reaches Claude. Claude Sonnet 5.5 runs at `low` effort through Pydantic AI, with the tools of `free_tools.py` over the saved weeks of this season and at most 4 tool calls. The text streams through `VercelAIAdapter` to `useChat` of the site. After the last word, one Jev request checks each sentence against the tool results, with one rewrite and then the honest miss. `free_wording.py` holds every word sent to Claude and to Jev for it. Each typed question carries the earlier turns of its Thread, cut to about 8,000 tokens, as Jev state for the route and as earlier messages for Claude, with a cache mark. The check never reads them. `chat_turns.py` holds them and their words.
12: - The refresh route that a daily cron pings.
13: - The passphrase check of each client, from `CORNERSTONE_PASSPHRASE_<SLUG>`, the commissioner key check of each client of the eggs package, from `CORNERSTONE_COMMISSIONER_KEY_<SLUG>`, the rate limit of each address, the limit of the egg check of each address, the state of each client, and the settings from the environment.
14: - The terms are in `GLOSSARY.md`.
15: 
16: ## Ports
17: 
18: - It takes the `Jev` port of the `league` package for the ask route, the trade picks, and the check of the free answer. `create_app` takes a `jev`, so a test gives `FakeJev`. The free answer runs the model of its Pydantic AI agent, and a test sets `app.state.free_model` to a function model of Pydantic AI.
19: 
20: ## Does not do
21: 
22: - It holds no grade rule and no prompt of the trade analyzer. The `analyzer` package holds them, with the grade limit and the caches. The only prompt here is the free answer of `free_wording.py`.
23: - It imports no pipeline code. Only its tests read the fixtures of the pipeline tests.
24: - It imports nothing from the output layer of ADR 0010, so it writes no page.
```

## `apps/api/src/cornerstone_api/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–24

```text
1: # cornerstone_api
2: 
3: ## Knows
4: 
5: - The FastAPI app that serves the trade analyzer to the site of each client.
6: - At start it reads each folder under `clients/`. A bad `client.toml` stops the start with the file and the key.
7: - It mounts the analyzer routes of the `analyzer` package at `/clients/<slug>/`. The old paths with no client answer as `cpc`.
8: - It mounts the eggs routes of the `eggs` package at `/clients/<slug>/eggs/` for each client of the package, with one SQLite file per client in `CORNERSTONE_EGGS_DIR`.
9: - The ask route of the front door at `/clients/<slug>/ask`, behind the passphrase. One Jev request routes each typed question, and the route table in `ask.py` reads the answers. `ask_wording.py` holds every word sent to Jev. An honest miss writes one entry in the miss log, one SQLite file per client in `CORNERSTONE_ASK_DIR`, kept 90 days (ADR 0031).
10: - The trade Topics of the front door at `/clients/<slug>/trade-check` and `/clients/<slug>/trade-ideas`, behind the passphrase, in `trade_topics.py`. A typed trade check has one Jev request that picks the player of each side from the real rosters, with its words in `trade_wording.py`. An unsure pick gives the form of the Trade page. Each route streams a plain step for each stage of the Advisor, then the whole Answer, in the event stream of the AI SDK. Trade ideas runs whatever the `finder` flag says. Sell high at `/clients/<slug>/sell-high` streams the same way, with the sell high press of the `analyzer` package.
11: - The free answer of the ask box at `/clients/<slug>/ask/free`, behind the passphrase. The route runs again first, so only a question that Jev routes to a free answer reaches Claude. Claude Sonnet 5.5 runs at `low` effort through Pydantic AI, with the tools of `free_tools.py` over the saved weeks of this season and at most 4 tool calls. The text streams through `VercelAIAdapter` to `useChat` of the site. After the last word, one Jev request checks each sentence against the tool results, with one rewrite and then the honest miss. `free_wording.py` holds every word sent to Claude and to Jev for it. Each typed question carries the earlier turns of its Thread, cut to about 8,000 tokens, as Jev state for the route and as earlier messages for Claude, with a cache mark. The check never reads them. `chat_turns.py` holds them and their words.
12: - The refresh route that a daily cron pings.
13: - The passphrase check of each client, from `CORNERSTONE_PASSPHRASE_<SLUG>`, the commissioner key check of each client of the eggs package, from `CORNERSTONE_COMMISSIONER_KEY_<SLUG>`, the rate limit of each address, the limit of the egg check of each address, the state of each client, and the settings from the environment. [caps.py](caps.py) owns daily answer allowances per team and local calendar day. [test_caps.py](../../tests/test_caps.py) checks team isolation and the next-day reset.
14: - The terms are in `GLOSSARY.md`.
15: 
16: ## Ports
17: 
18: - It takes the `Jev` port of the `league` package for the ask route, the trade picks, and the check of the free answer. `create_app` takes a `jev`, so a test gives `FakeJev`. The free answer runs the model of its Pydantic AI agent, and a test sets `app.state.free_model` to a function model of Pydantic AI.
19: 
20: ## Does not do
21: 
22: - It holds no grade rule and no prompt of the trade analyzer. The [analyzer owner](../../../../packages/analyzer/README.md) holds them, with the grade limit and the caches. The only prompt here is the free answer of `free_wording.py`.
23: - It imports no pipeline code. Only its tests read the fixtures of the pipeline tests.
24: - It imports nothing from the output layer of ADR 0010, so it writes no page.
```

# Before and after: `packages/analyzer/README.md`

## `packages/analyzer/README.md` at `17f45a15d1c324e36beefd0da29b77fe56b7ef91`; lines 1–24

```text
1: # analyzer: the trade analyzer and the trade finder
2: 
3: ## Knows
4: 
5: - The proposed trade of `trade.py`, the Measures and `Side` of `measures.py`, and the trade facts (`cpc-analyzer`, imported as `analyzer`). The read of the Advisor in `advisor.py`, with the Jev answers of `trade_jev.py`, and the team facts of `team_facts.py`. The Finder search of `finder_search.py`: the partner filter, the targets, the offers, and the shortlist, with its Jev requests in waves by `jev_waves.py`. The Finder pick of `finder_pick.py`: one sheet per shortlist offer, the Advisor pick of up to 3 trades with a headline and Bullets, and the fallback to the shortlist with fact lines. The sell high pick of `sell_high.py`: the sheet of one roster in `sell_facts.py`, with the trade value, the lineup value, the trend of the last 4 weeks, and the schedule ahead of each player side by side, and the Advisor pick of up to 3 players to sell with the guards and the Jev checks of the read.
6: - The rule prompts `prompts/advisor.md`, `prompts/finder_pick.md`, `prompts/finder_pick_repair.md`, and `prompts/sell_high.md`, and the numbers of `tunables.py`.
7: - The analyzer routes of the API in `routes.py`: the teams, the analyze route, and the find route, with the result cache, the teams cache, and the grade limit. The sell high press of the front door is there too, with no route of its own.
8: - The grade limit counts per client and per address. Each client has its own result cache, so the roster ids of two leagues never share a grade.
9: - The cache key reads the points key of the League settings of the client, such as `pts_ppr` for a full PPR league.
10: - The trade form, the finder, the API client, the passphrase, the teams store, and the team picker of the site (`@cpc/analyzer`). The site calls `/clients/<slug>/...`.
11: - Package values, under `[values.analyzer]`: `finder`, the trade finder on the analyzer page. The default is false.
12: - The model of its package values in `values.py`, and its exported JSON Schema `values.schema.json`. `make schema` rewrites the file.
13: 
14: ## Ports
15: 
16: - `SnapshotSource` in `routes.py`: the live snapshots of one client. The API app gives its `Sources`, and a test gives fixture-backed ones.
17: - `Analyzer` and `FinderPicker` in `routes.py`: the Advisor calls of the grade and of the Finder pick. Each takes an optional `Stage` of `stage.py`, a plain line per stage for the front door. A test gives a stub call. The Advisor takes the Jev port of `league`, and a test gives `FakeJev`. `FinderSearch` in `routes.py` is the Finder search with the real Jev, and a test gives a search with `FakeJev`. `SellHighPicker` in `routes.py` is the sell high pick, and a test gives a stub call.
18: 
19: ## Does not do
20: 
21: - It imports no app and no other core package, only `league` and `facts`. `tests/test_layers.py` of the pipeline checks it.
22: - It mounts no route. The API app mounts the routes at `/clients/<slug>/` and loads each client.
23: - Of a client folder, it reads the voice folder `prompts/` with the Playbook `playbook.md`, and the playoff odds in `published/<season>/rankings.json`.
24: - It writes no published file.
```

## `packages/analyzer/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–24

```text
1: # analyzer: the trade analyzer and the trade finder
2: 
3: ## Knows
4: 
5: - The proposed trade of `trade.py`, the Measures and `Side` of `measures.py`, and the trade facts (`cpc-analyzer`, imported as `analyzer`). The read of the Advisor in `advisor.py`, with the Jev answers of `trade_jev.py`, and the team facts of `team_facts.py`. The Finder search of `finder_search.py`: the partner filter, the targets, the offers, and the shortlist, with its Jev requests in waves by `jev_waves.py`. The Finder pick of `finder_pick.py`: one sheet per shortlist offer, the Advisor pick of up to 3 trades with a headline and Bullets, and the fallback to the shortlist with fact lines. The sell high pick of `sell_high.py`: the sheet of one roster in `sell_facts.py`, with the trade value, the lineup value, the trend of the last 4 weeks, and the schedule ahead of each player side by side, and the Advisor pick of up to 3 players to sell with the guards and the Jev checks of the read.
6: - The rule prompts `prompts/advisor.md`, `prompts/finder_pick.md`, `prompts/finder_pick_repair.md`, and `prompts/sell_high.md`, and the numbers of `tunables.py`.
7: - The analyzer routes of the API in `routes.py`: the teams, the analyze route, and the find route, with the result cache, the teams cache, and the grade limit. The sell high press of the front door is there too, with no route of its own.
8: - [GradeLimiter in ratelimit.py](python/src/analyzer/ratelimit.py) counts grades per client and address and saves daily counts across restarts. [API integration tests](../../apps/api/tests/test_api.py) check the restart limit and HTTP 429. Each client has its own result cache, so the roster ids of two leagues never share a grade.
9: - The cache key reads the points key of the League settings of the client, such as `pts_ppr` for a full PPR league.
10: - The [form owner](site/form/README.md), the finder, the API client, the passphrase, the teams store, and the team picker of the site (`@cpc/analyzer`). The site calls `/clients/<slug>/...`.
11: - Package values, under `[values.analyzer]`: `finder`, the trade finder on the analyzer page. The default is false.
12: - The model of its package values in `values.py`, and its exported JSON Schema `values.schema.json`. `make schema` rewrites the file.
13: 
14: ## Ports
15: 
16: - `SnapshotSource` in `routes.py`: the live snapshots of one client. The API app gives its `Sources`, and a test gives fixture-backed ones.
17: - `Analyzer` and `FinderPicker` in `routes.py`: the Advisor calls of the grade and of the Finder pick. Each takes an optional `Stage` of `stage.py`, a plain line per stage for the front door. A test gives a stub call. The Advisor takes the Jev port of `league`, and a test gives `FakeJev`. `FinderSearch` in `routes.py` is the Finder search with the real Jev, and a test gives a search with `FakeJev`. `SellHighPicker` in `routes.py` is the sell high pick, and a test gives a stub call.
18: 
19: ## Does not do
20: 
21: - It imports no app and no other core package, only `league` and `facts`. `tests/test_layers.py` of the pipeline checks it.
22: - It mounts no route. The [API owner](../../apps/api/src/cornerstone_api/README.md) mounts the routes at `/clients/<slug>/` and loads each client. That owner also controls daily answer allowances through `caps.py`.
23: - Of a client folder, it reads the voice folder `prompts/` with the Playbook `playbook.md`, and the playoff odds in `published/<season>/rankings.json`.
24: - It writes no published file.
```

# Before and after: `packages/analyzer/site/form/README.md`

## `packages/analyzer/site/form/README.md` at `17f45a15d1c324e36beefd0da29b77fe56b7ef91`; lines 1–24

```text
1: # packages/analyzer/site/form: the trade analyzer and the trade finder
2: 
3: ## Knows
4: 
5: - The analyzer page body: the passphrase dialog, the trade form, and the result.
6: - The trade form, the Stack: the hero, the teams row, a card for each side, the sheets, the grade bar with its Ready halo, the fold line, the sweep, and the error box.
7: - The result of one analyze document: the read hero with the Lean on its 5-step scale, the Case, and the fairness line, the swap card, one tab per side, and the Bullet rows in `bullet-rows.tsx`, which the Finder card reuses.
8: - The trade finder, with an optional partner and up to three picks of the Advisor, each with a headline, the swap, and the Bullet rows. After a fallback, each trade of the shortlist shows its fact lines. The teams prefetch of the home page.
9: - `useRequest`, the guard of a call from a part to the API: the run id, the abort controller, and the unmounted flag.
10: 
11: ## Ports
12: 
13: - The site API, through the client in `../lib/api.ts`. The calls are teams, analyze, and find, at `/clients/<slug>/`.
14: - The passphrase in local storage, through `../lib/passphrase.ts`.
15: - The teams list in session storage, through `../lib/teams-store.ts`.
16: - GoatCounter events, through `packages/design/site/lib/usage.ts`.
17: - Player headshots from the Sleeper CDN. The URL comes in the teams answer of the site API.
18: 
19: ## Does not do
20: 
21: - It grades no trade. The site API grades it, and this folder shows the answer.
22: - It shows no roster grade. The roster grade lives in the managers part of the site.
23: - It defines no API shape. `../lib/schemas/api.ts` holds the response schemas.
24: - It reads no file, no env, and no config, and it imports no app. The page gives the API target and the finder flag.
```

## `packages/analyzer/site/form/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–24

```text
1: # packages/analyzer/site/form: the trade analyzer and the trade finder
2: 
3: ## Knows
4: 
5: - The analyzer page body: the passphrase dialog, the trade form, and the result. [team-picker.tsx](team-picker.tsx) restores selected-team focus after Change my team. [team-picker.test.tsx](team-picker.test.tsx) checks the selected radio.
6: - The trade form, the Stack: the hero, the teams row, a card for each side, the sheets, the grade bar with its Ready halo, the fold line, the sweep, and the error box.
7: - The result of one analyze document: the read hero with the Lean on its 5-step scale, the Case, and the fairness line, the swap card, one tab per side, and the Bullet rows in `bullet-rows.tsx`, which the Finder card reuses.
8: - The trade finder, with an optional partner and up to three picks of the Advisor, each with a headline, the swap, and the Bullet rows. After a fallback, each trade of the shortlist shows its fact lines. The teams prefetch of the home page.
9: - `useRequest`, the guard of a call from a part to the API: the run id, the abort controller, and the unmounted flag.
10: 
11: ## Ports
12: 
13: - The site API, through the client in `../lib/api.ts`. The calls are teams, analyze, and find, at `/clients/<slug>/`.
14: - The passphrase in local storage, through `../lib/passphrase.ts`.
15: - The teams list in session storage, through `../lib/teams-store.ts`.
16: - GoatCounter events, through `packages/design/site/lib/usage.ts`.
17: - Player headshots from the Sleeper CDN. The URL comes in the teams answer of the site API.
18: 
19: ## Does not do
20: 
21: - It grades no trade. The [analyzer Python owner](../../README.md) grades it through the site API, and this folder shows the answer.
22: - It shows no roster grade. The roster grade lives in the managers part of the site.
23: - It defines no API shape. `../lib/schemas/api.ts` holds the response schemas.
24: - It reads no file, no env, and no config, and it imports no app. The page gives the API target and the finder flag.
```

# Before and after: `packages/week/README.md`

## `packages/week/README.md` at `17f45a15d1c324e36beefd0da29b77fe56b7ef91`; lines 1–22

```text
1: # week: the weekly report of one league
2: 
3: ## Knows
4: 
5: - The sheet chapters except rankings, the league and matchup facts, and the page writer of `page.json` (`cpc-week`, imported as `week`).
6: - The week chapters, the schema and the types of `page.json`, and `who` (`@cpc/week`). The loader of `page.json` stays in the site app, because it reads files.
7: - The median text in `prompts/median.md`. The writer and the verifier get it only when the league scores a median game.
8: - A league with no median game has no MED facts, no median part in the impact fact, and no Median Game chapter.
9: - The tunables of the week in `tunables.py`: the shootout cut, the storyline weights, the key starter rule, and the award cap.
10: - Package values: it has no values.
11: 
12: ## Ports
13: 
14: - The chapter port `ChapterSource` in `sheet/port.py`: a chapter of another package, with its facts and the odds it computes. The app passes the source of each package that the client takes, so a client with no rankings has no rankings chapter and no odds.
15: - The registry of the site build lists the home chapter of each package that the client takes, and no other. Each one sits in `apps/site/src/app/_routes/<package>/home.tsx`.
16: 
17: ## Does not do
18: 
19: - It imports no app and no core package, only `league` and `facts`. `tests/test_layers.py` of the pipeline checks it.
20: - It holds no odds engine and no power rankings. The rankings source gives them through the chapter port.
21: - It writes no rankings, managers, or waiver file. Each package writes its own.
22: - It sends no Claude call of its own. The writer and the verifier of `facts` write and check each blurb.
```

## `packages/week/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–22

```text
1: # week: the weekly report of one league
2: 
3: ## Knows
4: 
5: - The [sheet owner](python/src/week/sheet/README.md) holds roster projections. The sheet chapters except rankings, the league and matchup facts, and the page writer of `page.json` (`cpc-week`, imported as `week`).
6: - The week chapters, the schema and the types of `page.json`, and `who` (`@cpc/week`). The loader of `page.json` stays in the site app, because it reads files.
7: - The median text in `prompts/median.md`. The writer and the verifier get it only when the league scores a median game.
8: - A league with no median game has no MED facts, no median part in the impact fact, and no Median Game chapter.
9: - The tunables of the week in `tunables.py`: the shootout cut, the storyline weights, the key starter rule, and the award cap.
10: - Package values: it has no values.
11: 
12: ## Ports
13: 
14: - The chapter port `ChapterSource` in `sheet/port.py`: a chapter of another package, with its facts and the odds it computes. The app passes the source of each package that the client takes, so a client with no rankings has no rankings chapter and no odds.
15: - The registry of the site build lists the home chapter of each package that the client takes, and no other. Each one sits in `apps/site/src/app/_routes/<package>/home.tsx`.
16: 
17: ## Does not do
18: 
19: - It imports no app and no core package, only `league` and `facts`. `tests/test_layers.py` of the pipeline checks it.
20: - It holds no odds engine and no power rankings. The [rankings owner](../rankings/README.md) gives them through the chapter port. Roster projections belong to the sheet, not that odds engine.
21: - It writes no rankings, managers, or waiver file. Each package writes its own.
22: - It sends no Claude call of its own. The writer and the verifier of `facts` write and check each blurb.
```

# Before and after: `packages/week/python/src/week/sheet/README.md`

## `packages/week/python/src/week/sheet/README.md` at `17f45a15d1c324e36beefd0da29b77fe56b7ef91`; lines 1–22

```text
1: # week.sheet
2: 
3: ## Knows
4: 
5: - It builds the facts of each fact group into the fact sheet of one week, and puts the facts into each chapter.
6: - It builds the bundle that each chapter reads, and it writes and reads the bundle file.
7: - The entry: outside this folder, a module imports only `week.sheet` or `week.sheet.base`.
8: - A league with no median game gets no MED facts, no median part in the impact fact, and no Median Game chapter.
9: - The terms are in `GLOSSARY.md`.
10: 
11: ## Ports
12: 
13: - `sheet/port.py` is the chapter port. A source of another package gives its facts, its chapter, and the odds.
14: - `sheet/assemble.py` calls `provider.sleeper.fetch_news` by default, so the sheet reaches the Sleeper news feed.
15: 
16: ## Does not do
17: 
18: - It writes no prose and makes no Claude call. `facts/writer.py` writes each blurb.
19: - It checks no blurb. `facts/verifier.py` does.
20: - It holds no odds engine and no rankings chapter. The rankings source gives both through the chapter port.
21: - It writes no page. `week/page.py` writes `page.json`.
22: - It builds no fact sheet of a proposed trade. `cornerstone/trade_facts.py` does.
```

## `packages/week/python/src/week/sheet/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–23

```text
1: # week.sheet
2: 
3: ## Knows
4: 
5: - It builds the facts of each fact group into the fact sheet of one week, and puts the facts into each chapter.
6: - It builds the bundle that each chapter reads, and it writes and reads the bundle file.
7: - The entry: outside this folder, a module imports only `week.sheet` or `week.sheet.base`.
8: - A league with no median game gets no MED facts, no median part in the impact fact, and no Median Game chapter.
9: - [base.py](base.py) owns `projected_totals`, which reads current roster players, including additions after the scored week. [test_sheet.py](../../../../../../apps/pipeline/tests/test_sheet.py) checks additions and drops after lineup lock.
10: - The terms are in `GLOSSARY.md`.
11: 
12: ## Ports
13: 
14: - `sheet/port.py` is the chapter port. A source of another package gives its facts, its chapter, and the odds.
15: - `sheet/assemble.py` calls `provider.sleeper.fetch_news` by default, so the sheet reaches the Sleeper news feed.
16: 
17: ## Does not do
18: 
19: - It writes no prose and makes no Claude call. `facts/writer.py` writes each blurb.
20: - It checks no blurb. `facts/verifier.py` does.
21: - It holds no odds engine and no rankings chapter. The [rankings owner](../../../../../rankings/README.md) gives both through the chapter port.
22: - It writes no page. `week/page.py` writes `page.json`.
23: - It builds no fact sheet of a proposed trade. `cornerstone/trade_facts.py` does.
```

## `.scratch/readme-module-navigation/decisions/03-grill-cold-agent-test-procedure.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 17–29

```text
17: Define what makes an agent cold and how the test withholds expected answers.
18: The evidence must show each agent's path choices, reasons, and complete read record.
19: The procedure supplies evidence; the Judge gives each acceptance test its Test verdict.
20: 
21: ## Decision
22: 
23: Brian approves the procedure below for the six tasks from decision 01.
24: 
25: ### Cold start and tracker exception
26: 
27: Each task has one fresh agent at the repository root, with no inherited history or expected answers.
28: Each agent receives only its approved behavior prompt and the common test procedure.
29: Repository and external instructions still apply, except for the test-only exception below.
```

