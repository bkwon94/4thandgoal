# 03: Does a rebuild match the published files

Map: `.scratch/trusted-green/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The differential rebuild runs `build --no-fetch` for the latest published week of each client, then diffs the output against `clients/<slug>/published/`. Find out four facts. Does the output match byte for byte? Which parts differ, such as a time stamp or text that Claude writes? How long does one rebuild take on a CI runner? Which secrets does it need? If one rebuild takes more than 5 minutes, the job runs one client only.

## Decision

Research on 2026-11-18. Notes: `decisions/03-research-rebuild-matches-published.notes.md`.

A full `build --no-fetch` is no oracle. It needs `ANTHROPIC_API_KEY` and `TYPESAFE_API_KEY`, takes about 12.5 min per client, and never matches: Claude text, live nflverse data, Sleeper news, and the clock all change. The nflverse cache is gitignored, so CI lacks the input of the facts, and the facts alone differ in about 500 values per client.

`page-json` re-renders the saved facts and blurbs. It matches `published/2026/week-10/` byte for byte for cpc and norcal, in about 2 s, with no secret and no network. Only the latest week is a fair oracle, because later code changes moved weeks 6 to 8.

Item 10 of decision 01 changes. Ticket 09 decides what the differential rebuild diffs.
