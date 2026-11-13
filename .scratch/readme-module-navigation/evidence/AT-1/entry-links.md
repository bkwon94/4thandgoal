Implementation revision: `dad744db4f3b49732adc1586e08c34be2f381f73`.
Base revision: `17f45a15d1c324e36beefd0da29b77fe56b7ef91`.
All source excerpts below come from Git objects at the stated revision.
No behavior test or cold task runs during this static capture.

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

| Source | Line | Relative target | Resolved repository target | Exists at revision |
| --- | --- | --- | --- | --- |
| `CLAUDE.md` | 5 | `apps/site/README.md` | `apps/site/README.md` | true |
| `CLAUDE.md` | 6 | `apps/pipeline/README.md` | `apps/pipeline/README.md` | true |
| `CLAUDE.md` | 7 | `apps/api/README.md` | `apps/api/README.md` | true |
| `apps/site/CLAUDE.md` | 7 | `README.md` | `apps/site/README.md` | true |
| `apps/pipeline/CLAUDE.md` | 9 | `README.md` | `apps/pipeline/README.md` | true |
