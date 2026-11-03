# cpcfantasyfootball

This repo holds two apps. Each app has a CLAUDE.md with its own commands and rules. Read the one for the app you change.

- `apps/site/` is the Next.js site. It renders `apps/site/public/<season>/week-NN/page.json` and its images.
- `apps/pipeline/` is the Python pipeline. It builds each week and publishes it into `apps/site/public/`.

## Style

Write all output in Simplified Technical English. Rules: `~/.claude/rules/communication/simplified-technical-english.md`. Active voice, present tense, one instruction per sentence, 20 words or fewer, no `-ing` as a verb, plain words. Code, technical names, and quoted output are exempt.

## Records

- `GLOSSARY.md` holds the terms of both apps, one section per app, and the workflow terms. Each term has one meaning.
- `docs/adr/` holds one ADR series for both apps. `docs/adr/README.md` maps each old app number to its new number.

## The flow

ADRs 0018 to 0021 set the flow. The spec `.scratch/one/` builds it, so its own tickets still merge to `main` as before.

1. `main` is the record branch. No agent commits on `main` or pushes to `main` (ADR 0019).
2. A spec branch is named `<slug>` and starts from `main`.
3. A ticket branch is named `<slug>-<NN>`. It is local, starts from the spec branch, and has its own worktree.
4. A ticket merges into its spec branch with `git merge --no-edit`, after the check passes.
5. One pull request goes from the spec branch to `main`, as a squash merge.
6. An agent records the evidence of each acceptance test `AT-<n>`. The agent gives no test verdict.
7. Brian gives PASS, FAIL, or BLOCKED for each test in one PR comment. A check blocks the merge until each test has PASS (ADR 0020).

The weekly `publish` is the one exception. It may push to `main`, and it may stage only `apps/site/public/<season>/`.

## Tracker

The tracker is local markdown, because the notes name league managers and the repo is public (ADR 0021).

- The root tracker is `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.
- The pipeline keeps its own tracker under `apps/pipeline/.scratch/`, with its rows in `apps/pipeline/docs/agents/state.md`.
- A new feature has an optional `MAP.md`, `decisions/`, `PRD.md`, `ACCEPTANCE.md`, and `issues/`. Old features keep their shape.

## Where the work sits

`docs/agents/state.md` lists each open feature, its next ticket, and its blocker. An agent new to the repo reads it
after this file, then reads one ticket in the tracker.

## Commits

The prek hook runs `pnpm check:fast` of the site, then `make check-fast` of the pipeline, before each commit.
Never commit with `--no-verify`.
