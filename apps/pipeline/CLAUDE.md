# Cornerstone Weekly

## Purpose

This tool builds a weekly report page for the Cornerstone fantasy football league. It reads
league data from Sleeper. It writes the chapters of the report and writes the page data. The site in `apps/site` renders the pages.
The root CLAUDE.md holds the style, the flow, and the tracker. `GLOSSARY.md` names the chapter of prose a "Prose block".

## Commands

Run these in `apps/pipeline/`. Run `make help` for the full list.

- Install: `make install`. The root `uv.lock` holds the locked versions of the whole uv workspace.
- Check: `make check`. The hook runs `make check-fast`.
- Build a week: `make build CLIENT=cpc WEEK=<W>`. Each league target needs the client slug.
- Publish a week: `make publish CLIENT=cpc WEEK=<W>`. It commits `clients/<slug>/build/<season>/`, `clients/<slug>/data/<season>/`, and `clients/<slug>/published/<season>/`, then pushes `main`.
- Local API on port 8080: `make -C ../api api`. The API is its own app in `apps/api/`.

## Pipeline

1. Fetch the raw league data from Sleeper.
2. Save the raw data under `clients/<slug>/data/` and cache the shared NFL data under `data/nfl/cache/`, both at the repo root.
3. Compute the stats for each chapter.
4. Write the chapter text with the Anthropic API.
5. Write `page.json` and the images into the build folder `clients/<slug>/build/`.
6. Publish the week folder to `clients/<slug>/published/` of this repo.

## Where the work sits

`docs/agents/state.md` at the repo root lists each open feature of both apps, its next ticket, and its hold. Read it, then the
ticket in the root tracker under `.scratch/`.

## Publish rule

Nothing publishes without `cornerstone publish`. No other command or script pushes the site.

## Tests

- Run `uv run pytest` for the default suite. It skips tests marked `live`.
- A test marked `live` calls a real external API. Run it on purpose with `uv run pytest -m live`.
- Run `make check` before a merge. The prek hook runs `make check-fast` on each commit.
- Name a rule test `tests/test_rule_<topic>.py`. `make rules` finds each one with no edit.

## House style

Prose follows Simplified Technical English. The rules are in
`~/.claude/rules/communication/simplified-technical-english.md`.

## Agent skills

### Issue tracker

Local markdown under `.scratch/<feature>/` at the repo root. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default names, unchanged. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` and `docs/adr/` at the repo root, shared with the site. See `docs/agents/domain.md`.
