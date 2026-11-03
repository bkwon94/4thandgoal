# cpcfantasyfootball

This repo holds two apps.

- `apps/site/` is the Next.js site. It renders `apps/site/public/<season>/week-NN/page.json` and its images.
- `apps/pipeline/` is the Python pipeline. It builds each week and publishes it into `apps/site/public/`.
  Its own CLAUDE.md holds its pipeline steps and rules.

## Site commands

Run these in `apps/site/`.

- Install: `pnpm install`
- Dev server: `pnpm dev`
- Build the static export: `pnpm build`
- Test: `pnpm test`
- Check the export: `pnpm check:export`. Run it after `pnpm build`.

## Pipeline commands

Run these in `apps/pipeline/`. Run `make help` for the full list.

- Install: `uv sync`
- Check: `make check`. The hook runs `make check-fast`.
- Build a week: `make build WEEK=<W>`
- Publish a week: `make publish WEEK=<W>`. It commits `apps/site/public` and pushes `main`.
- Local API on port 8080: `make api`

## Style

Write all output in Simplified Technical English. Rules: `~/.claude/rules/communication/simplified-technical-english.md`. Active voice, present tense, one instruction per sentence, 20 words or fewer, no `-ing` as a verb, plain words. Code, technical names, and quoted output are exempt.

## Where the work sits

`docs/agents/state.md` lists each open feature, its next ticket, and its blocker. An agent new to the repo reads it
after this file, then reads one ticket in the tracker.

## Tracker

The tracker is local markdown under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.
The pipeline keeps its own tracker under `apps/pipeline/.scratch/`, with its rows in `apps/pipeline/docs/agents/state.md`.
