# cpcfantasyfootball

This repo holds three apps. The site and the pipeline each have a CLAUDE.md with its own commands and rules. Read the one for the app you change.

- `apps/site/` is the Next.js site. Its build copies `clients/<slug>/published/` of one client into `public/` and renders each `page.json` and its images.
- `apps/pipeline/` is the Python pipeline. It builds each week and publishes it into `clients/<slug>/published/`.
- `apps/api/` is the API of the trade analyzer. It imports the pipeline and deploys to Fly. Run `make help` in it.

The root holds one uv workspace and one pnpm workspace, each with one lock file: `uv.lock` and `pnpm-lock.yaml`.
Run `uv sync --all-packages` and `pnpm install` at the root. A member runs with `uv run --exact --package <name>`.

## Style

Write all output in Simplified Technical English. Rules: `~/.claude/rules/communication/simplified-technical-english.md`. Active voice, present tense, one instruction per sentence, 20 words or fewer, no `-ing` as a verb, plain words. Code, technical names, and quoted output are exempt.

## Records

- `GLOSSARY.md` holds the terms of both apps, one section per app, and the workflow terms. Each term has one meaning.
- `docs/adr/` holds one ADR series for both apps. `docs/adr/README.md` maps each old app number to its new number.

## The flow

ADRs 0018 to 0021 and ADR 0026 set the flow. ADR 0026 supersedes ADR 0020. The spec `.scratch/one/` builds it, so its own tickets still merge to `main` as before.

1. `main` is the record branch. No agent commits on `main` or pushes to `main` (ADR 0019).
2. A spec branch is named `<slug>` and starts from `main`.
3. A ticket branch is named `<slug>-<NN>`. It is local, starts from the spec branch, and has its own worktree.
4. A ticket merges into its spec branch with `git merge --no-edit`, after the check passes.
5. One pull request goes from the spec branch to `main`, as a squash merge.
6. An agent records the evidence of each acceptance test `AT-<n>`. The agent gives no test verdict.
7. A fresh subagent, the Judge, gives PASS, FAIL, or BLOCKED for each test in `VERDICTS.md`. A check blocks the merge until each test has PASS. A FAIL from Brian in a PR comment overrides the Judge (ADR 0026).

The weekly `publish` is the one exception. It may push to `main`, and it may stage only `clients/<slug>/published/<season>/`, `clients/<slug>/data/<season>/`, and `clients/<slug>/build/<season>/`.

The repo plugin `cpc` takes an idea to a merged spec. Run its skills in this order. Brian approves the output of each of steps 2 to 4.

1. `cpc:plan <outcome statement>` writes the map and the decision tickets. `cpc:plan <feature>` clears one decision ticket per session.
2. `cpc:to-spec <feature>` writes `PRD.md`.
3. `cpc:to-acceptance <feature>` writes `ACCEPTANCE.md`.
4. `cpc:to-tickets <feature>` writes the tickets and the `state.md` row.
5. `cpc:implement <feature>` builds each ticket on its ticket branch, merges it into the spec branch, records the evidence in `EVIDENCE.md`, has the Judge write `VERDICTS.md`, and opens one PR to `main`.
6. Brian posts no comment unless he gives a FAIL. `cpc:review <PR number>` does one round of feedback per run. The check `verdict` passes when each test has PASS from the Judge and no FAIL from Brian, and Brian merges.

## Tracker

The tracker is local markdown, because the notes name league managers and the repo is public (ADR 0021).

- The tracker is `.scratch/<feature>/` at the root, for both apps. See `docs/agents/issue-tracker.md`.
- A feature that both old trackers held keeps a `site/` and a `pipeline/` subfolder, each with its own PRD and `issues/`.
- A new feature has an optional `MAP.md`, `decisions/`, `PRD.md`, `ACCEPTANCE.md`, and `issues/`. Old features keep their shape.

## Where the work sits

`docs/agents/state.md` lists each open feature, its next ticket, and its blocker. An agent new to the repo reads it
after this file, then reads one ticket in the tracker.

## Commits

The prek hook runs `pnpm check:fast` of the site, then `make check-fast` of the pipeline and of the API, before each commit.
Never commit with `--no-verify`.
