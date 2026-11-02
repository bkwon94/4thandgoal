# cpcfantasyfootball site

This repo is the source of the Next.js site. The Python pipeline repo
`cornerstone-fantasy-sleeper-weekly-report` publishes one `page.json` per week, with its images,
into `public/<season>/week-NN/`. This app renders the pages.

## Commands

- Install: `pnpm install`
- Dev server: `pnpm dev`
- Build the static export: `pnpm build`
- Test: `pnpm test`
- Check the export: `pnpm check:export`. Run it after `pnpm build`.

## Style

Write all output in Simplified Technical English. Rules: `~/.claude/rules/communication/simplified-technical-english.md`. Active voice, present tense, one instruction per sentence, 20 words or fewer, no `-ing` as a verb, plain words. Code, technical names, and quoted output are exempt.

## Where the work sits

`docs/agents/state.md` lists each open feature, its next ticket, and its blocker. An agent new to the repo reads it
after this file, then reads one ticket in the tracker.

## Tracker

The tracker is local markdown under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.
