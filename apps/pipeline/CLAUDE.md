# Cornerstone Weekly

## Purpose

This tool builds a weekly report page for the Cornerstone fantasy football league. It reads
league data from Sleeper. It writes the chapters of the report and writes the page data. The site repo renders the pages.

## Pipeline

1. Fetch the raw league data from Sleeper.
2. Cache the raw data under `data/cache/`.
3. Compute the stats for each chapter.
4. Write the chapter text with the Anthropic API.
5. Write `page.json` and the images into `site/`.
6. Publish the week folder to the public site repo.

## Where the work sits

`docs/agents/state.md` lists each open feature, its next ticket, and its hold. Read it, then the ticket in the
tracker under `.scratch/`.

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

Local markdown under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default names, unchanged. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` and `docs/adr/` at the root. See `docs/agents/domain.md`.
